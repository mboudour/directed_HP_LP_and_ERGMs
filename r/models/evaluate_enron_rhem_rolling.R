#!/usr/bin/env Rscript
# Evaluate a sampled-risk-set, conditional-sender RHEM over predeclared
# chronological folds. Eventnet supplies history covariates and candidate sets;
# survival::coxph estimates the conditional partial likelihood within each
# event-level choice set (EVENT_INTERVAL). This is receiver-set discrimination
# conditional on observed sender and receiver-set size, never a model of email
# timing, sender choice, or receiver-set size.

options(stringsAsFactors = FALSE)

usage <- function() {
  cat(
    paste(
      "Usage: Rscript r/models/evaluate_enron_rhem_rolling.R",
      "--input-dir=<Eventnet bundle> --output-dir=<aggregate output>",
      "[--observation=CONDITIONAL_SENDER_SET] [--overwrite=TRUE]",
      sep = "\n"
    ),
    "\n"
  )
}

parse_args <- function(args) {
  values <- list(
    observation = "CONDITIONAL_SENDER_SET",
    overwrite = FALSE
  )
  for (arg in args) {
    if (identical(arg, "--help")) {
      usage()
      quit(status = 0L)
    }
    if (!startsWith(arg, "--")) {
      stop("Unexpected positional argument: ", arg, call. = FALSE)
    }
    parts <- strsplit(substring(arg, 3L), "=", fixed = TRUE)[[1L]]
    key <- parts[[1L]]
    value <- if (length(parts) > 1L) paste(parts[-1L], collapse = "=") else "TRUE"
    key <- gsub("-", "_", key, fixed = TRUE)
    values[[key]] <- value
  }
  required <- c("input_dir", "output_dir")
  missing <- required[!vapply(required, function(key) !is.null(values[[key]]), logical(1L))]
  if (length(missing) > 0L) {
    stop("Missing required arguments: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  values$overwrite <- identical(tolower(as.character(values$overwrite)), "true")
  values
}

sha256_file <- function(path) {
  if (!requireNamespace("digest", quietly = TRUE)) {
    stop("Package digest is required for provenance hashing.", call. = FALSE)
  }
  digest::digest(file = path, algo = "sha256")
}

safe_numeric <- function(values, name) {
  parsed <- suppressWarnings(as.numeric(values))
  if (any(!is.finite(parsed))) {
    stop("Non-finite values in required Eventnet statistic: ", name, call. = FALSE)
  }
  parsed
}

read_eventnet_data <- function(input_dir, observation) {
  path <- file.path(input_dir, "eventnet_output", paste0("enron_events_eventnet_", observation, ".csv"))
  if (!file.exists(path)) {
    stop("Eventnet observation table is missing: ", path, call. = FALSE)
  }
  data <- utils::read.csv(path, check.names = FALSE)
  required <- c(
    "IS_OBSERVED", "EVENT_INTERVAL", "EVENT_INTERVAL_ID", "exact_rep", "dyad_rep",
    "reciprocation", "target_pair_rep", "transitive_closure"
  )
  missing <- setdiff(required, names(data))
  if (length(missing) > 0L) {
    stop("Eventnet table lacks columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  data$IS_OBSERVED <- safe_numeric(data$IS_OBSERVED, "IS_OBSERVED")
  if (!all(data$IS_OBSERVED %in% c(0, 1))) {
    stop("IS_OBSERVED must be binary.", call. = FALSE)
  }
  data$EVENT_INTERVAL <- safe_numeric(data$EVENT_INTERVAL, "EVENT_INTERVAL")
  data
}

attach_event_index <- function(data, input_dir) {
  index_path <- file.path(input_dir, "event_index_private.csv")
  if (!file.exists(index_path)) {
    stop("Private event index is missing: ", index_path, call. = FALSE)
  }
  index <- utils::read.csv(index_path, check.names = FALSE)
  required <- c("event_interval_id", "timestamp_utc", "month", "head_size")
  missing <- setdiff(required, names(index))
  if (length(missing) > 0L) {
    stop("Event index lacks columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  observed <- data[data$IS_OBSERVED == 1, c("EVENT_INTERVAL", "EVENT_INTERVAL_ID")]
  if (anyDuplicated(observed$EVENT_INTERVAL)) {
    stop("Every Eventnet choice set must have one observed event.", call. = FALSE)
  }
  observed$event_interval_id <- safe_numeric(observed$EVENT_INTERVAL_ID, "EVENT_INTERVAL_ID")
  index$event_interval_id <- safe_numeric(index$event_interval_id, "event_interval_id")
  if (anyDuplicated(index$event_interval_id)) {
    stop("Private event index has duplicate interval IDs.", call. = FALSE)
  }
  mapped <- merge(observed, index, by = "event_interval_id", all.x = TRUE, sort = FALSE)
  if (nrow(mapped) != nrow(observed) || any(is.na(mapped$timestamp_utc))) {
    stop("Unable to map one or more Eventnet choice sets to native-event timestamps.", call. = FALSE)
  }
  timestamps <- as.POSIXct(mapped$timestamp_utc, tz = "UTC")
  if (any(is.na(timestamps))) {
    stop("Event index contains a malformed UTC timestamp.", call. = FALSE)
  }
  map <- data.frame(
    EVENT_INTERVAL = mapped$EVENT_INTERVAL,
    event_time = timestamps,
    month = mapped$month,
    head_size = safe_numeric(mapped$head_size, "head_size"),
    stringsAsFactors = FALSE
  )
  result <- merge(data, map, by = "EVENT_INTERVAL", all.x = TRUE, sort = FALSE)
  if (nrow(result) != nrow(data) || any(is.na(result$event_time))) {
    stop("Failed to attach timestamp metadata to all candidate rows.", call. = FALSE)
  }
  result
}

read_folds <- function(input_dir) {
  path <- file.path(input_dir, "rolling_folds_private.csv")
  if (!file.exists(path)) {
    stop("Rolling-fold contract is missing: ", path, call. = FALSE)
  }
  folds <- utils::read.csv(path, check.names = FALSE)
  required <- c("fold", "train_end_utc_exclusive", "test_start_utc_inclusive", "test_end_utc_exclusive")
  missing <- setdiff(required, names(folds))
  if (length(missing) > 0L) {
    stop("Fold contract lacks columns: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  for (column in required[-1L]) {
    folds[[column]] <- as.POSIXct(folds[[column]], tz = "UTC")
    if (any(is.na(folds[[column]]))) {
      stop("Malformed fold UTC boundary in column ", column, call. = FALSE)
    }
  }
  folds
}

preprocess_statistics <- function(data, terms) {
  for (term in terms) {
    data[[term]] <- sqrt(pmax(safe_numeric(data[[term]], term), 0))
  }
  data
}

fit_rhem <- function(train, terms, model_name) {
  nonconstant <- terms[vapply(terms, function(term) stats::sd(train[[term]]) > 0, logical(1L))]
  dropped <- setdiff(terms, nonconstant)
  if (length(nonconstant) == 0L) {
    return(list(status = "no_variable_terms", message = "No varying training covariates.", coefficients = numeric(), dropped = dropped))
  }
  formula <- stats::as.formula(
    paste(
      "survival::Surv(rep(1, nrow(train)), IS_OBSERVED) ~",
      paste(c(nonconstant, "survival::strata(EVENT_INTERVAL)"), collapse = " + ")
    )
  )
  warnings <- character()
  fitted <- tryCatch(
    withCallingHandlers(
      survival::coxph(formula, data = train, ties = "breslow", singular.ok = TRUE),
      warning = function(condition) {
        warnings <<- c(warnings, conditionMessage(condition))
        invokeRestart("muffleWarning")
      }
    ),
    error = function(error) error
  )
  if (inherits(fitted, "error")) {
    return(list(status = "fit_failed", message = conditionMessage(fitted), coefficients = numeric(), dropped = dropped))
  }
  coefficients <- stats::coef(fitted)
  finite <- is.finite(coefficients)
  status <- if (all(finite)) "fit_succeeded" else "fit_succeeded_nonfinite_terms_dropped"
  list(
    status = status,
    message = paste(unique(warnings), collapse = " | "),
    coefficients = coefficients[finite],
    dropped = c(dropped, names(coefficients)[!finite]),
    requested_terms = terms,
    model_name = model_name,
    training_choice_sets = length(unique(train$EVENT_INTERVAL))
  )
}

score_rows <- function(data, coefficients) {
  if (length(coefficients) == 0L) {
    return(rep(0, nrow(data)))
  }
  matrix <- as.matrix(data[, names(coefficients), drop = FALSE])
  as.vector(matrix %*% coefficients)
}

choice_metrics <- function(data, scores, scope) {
  if (identical(scope, "head_size_1")) {
    keep <- data$head_size == 1
    data <- data[keep, , drop = FALSE]
    scores <- scores[keep]
  } else if (identical(scope, "head_size_ge_2")) {
    keep <- data$head_size >= 2
    data <- data[keep, , drop = FALSE]
    scores <- scores[keep]
  }
  if (nrow(data) == 0L) {
    return(c(choice_sets = 0, mean_log_score = NA_real_, top1_tie_adjusted = NA_real_, mrr_tie_adjusted = NA_real_, mean_rank = NA_real_))
  }
  split_index <- split(seq_len(nrow(data)), data$EVENT_INTERVAL)
  per_choice <- lapply(split_index, function(indices) {
    values <- scores[indices]
    observed <- which(data$IS_OBSERVED[indices] == 1)
    if (length(observed) != 1L) {
      stop("Each evaluated choice set must contain one observed event.", call. = FALSE)
    }
    observed_score <- values[[observed]]
    maximum <- max(values)
    probability <- exp(observed_score - maximum) / sum(exp(values - maximum))
    greater <- sum(values > observed_score)
    ties <- sum(values == observed_score)
    average_rank <- greater + (ties + 1) / 2
    c(
      log_score = log(probability),
      top1_tie_adjusted = if (observed_score == maximum) 1 / ties else 0,
      mrr_tie_adjusted = 1 / average_rank,
      rank = average_rank
    )
  })
  matrix <- do.call(rbind, per_choice)
  c(
    choice_sets = nrow(matrix),
    mean_log_score = mean(matrix[, "log_score"]),
    top1_tie_adjusted = mean(matrix[, "top1_tie_adjusted"]),
    mrr_tie_adjusted = mean(matrix[, "mrr_tie_adjusted"]),
    mean_rank = mean(matrix[, "rank"])
  )
}

write_summary <- function(path, manifest, metrics, statuses) {
  lines <- c(
    "# Enron conditional RHEM rolling-origin pilot",
    "",
    "This output evaluates sender-conditioned, same-recipient-count receiver-set choice on Eventnet's sampled case-control sets. It does not estimate email timing, sender choice, receiver-set size, or unconditional event probabilities.",
    "",
    "## Completion",
    "",
    paste0("- Observation: `", manifest$observation, "`"),
    paste0("- Eventnet candidates: `", manifest$eventnet_rows, "` rows across `", manifest$choice_sets, "` choice sets"),
    paste0("- Requested controls per observed event: `", manifest$requested_controls_per_event, "`"),
    paste0("- Eventnet random seed: `", manifest$eventnet_random_seed, "`"),
    paste0("- Completed model-fold fits: `", sum(statuses$status %in% c("fit_succeeded", "fit_succeeded_nonfinite_terms_dropped")), "/", nrow(statuses), "`"),
    "",
    "## Metrics",
    "",
    "| Model | Fold | Scope | Choice sets | Mean conditional log score | Top-1 (tie adjusted) | MRR (tie adjusted) | Mean rank |",
    "|:---|:---|:---|---:|---:|---:|---:|---:|"
  )
  for (row in seq_len(nrow(metrics))) {
    metric <- metrics[row, ]
    lines <- c(
      lines,
      sprintf(
        "| %s | %s | %s | %d | %.4f | %.4f | %.4f | %.3f |",
        metric$model, metric$fold, metric$scope, metric$choice_sets,
        metric$mean_log_score, metric$top1_tie_adjusted,
        metric$mrr_tie_adjusted, metric$mean_rank
      )
    )
  }
  lines <- c(
    lines,
    "",
    "## Interpretation boundary",
    "",
    "Scores are conditional on this one seeded Eventnet sampled risk set and on the selected within-timestamp Eventnet order. They are pilot discrimination metrics, not population-calibrated probabilities. Final interpretation requires the registered multi-seed and batch-history/tie-order sensitivities."
  )
  writeLines(lines, path)
}

main <- function() {
  if (!requireNamespace("survival", quietly = TRUE)) {
    stop("Package survival is required; run Rscript r/bootstrap_renv.R.", call. = FALSE)
  }
  args <- parse_args(commandArgs(trailingOnly = TRUE))
  input_dir <- normalizePath(args$input_dir, mustWork = TRUE)
  output_dir <- normalizePath(args$output_dir, mustWork = FALSE)
  if (dir.exists(output_dir) && length(list.files(output_dir, all.files = TRUE, no.. = TRUE)) > 0L) {
    if (!args$overwrite) {
      stop("Output directory is non-empty; pass --overwrite=TRUE: ", output_dir, call. = FALSE)
    }
    unlink(output_dir, recursive = TRUE)
  }
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  data <- read_eventnet_data(input_dir, args$observation)
  data <- attach_event_index(data, input_dir)
  folds <- read_folds(input_dir)
  input_manifest_path <- file.path(input_dir, "rhem_input_manifest.json")
  if (!file.exists(input_manifest_path)) {
    stop("RHEM input manifest is missing: ", input_manifest_path, call. = FALSE)
  }
  input_manifest <- jsonlite::read_json(input_manifest_path, simplifyVector = TRUE)
  requested_controls <- input_manifest$risk_set$controls_per_observed_event
  random_seed <- input_manifest$risk_set$eventnet_random_seed
  if (length(requested_controls) != 1L || length(random_seed) != 1L) {
    stop("RHEM input manifest lacks scalar risk-set controls or random seed.", call. = FALSE)
  }
  terms <- c("dyad_rep", "reciprocation", "transitive_closure", "exact_rep", "target_pair_rep")
  data <- preprocess_statistics(data, terms)
  models <- list(
    DYADIC_HISTORY = c("dyad_rep", "reciprocation", "transitive_closure"),
    GROUP_AUGMENTED = c("dyad_rep", "reciprocation", "transitive_closure", "exact_rep", "target_pair_rep")
  )

  metrics <- list()
  coefficients <- list()
  statuses <- list()
  for (fold_index in seq_len(nrow(folds))) {
    fold <- folds[fold_index, ]
    train <- data[data$event_time < fold$train_end_utc_exclusive, , drop = FALSE]
    test <- data[
      data$event_time >= fold$test_start_utc_inclusive & data$event_time < fold$test_end_utc_exclusive,
      ,
      drop = FALSE
    ]
    for (model_name in names(models)) {
      fitted <- fit_rhem(train, models[[model_name]], model_name)
      statuses[[length(statuses) + 1L]] <- data.frame(
        model = model_name,
        fold = fold$fold,
        status = fitted$status,
        message = fitted$message,
        training_choice_sets = length(unique(train$EVENT_INTERVAL)),
        test_choice_sets = length(unique(test$EVENT_INTERVAL)),
        dropped_terms = paste(unique(fitted$dropped), collapse = ";"),
        stringsAsFactors = FALSE
      )
      if (!(fitted$status %in% c("fit_succeeded", "fit_succeeded_nonfinite_terms_dropped"))) {
        next
      }
      coefficient_values <- fitted$coefficients
      if (length(coefficient_values) > 0L) {
        coefficients[[length(coefficients) + 1L]] <- data.frame(
          model = model_name,
          fold = fold$fold,
          term = names(coefficient_values),
          coefficient = as.numeric(coefficient_values),
          stringsAsFactors = FALSE
        )
      }
      scores <- score_rows(test, coefficient_values)
      for (scope in c("all", "head_size_1", "head_size_ge_2")) {
        values <- choice_metrics(test, scores, scope)
        metrics[[length(metrics) + 1L]] <- data.frame(
          model = model_name,
          fold = fold$fold,
          scope = scope,
          choice_sets = as.integer(values[["choice_sets"]]),
          mean_log_score = as.numeric(values[["mean_log_score"]]),
          top1_tie_adjusted = as.numeric(values[["top1_tie_adjusted"]]),
          mrr_tie_adjusted = as.numeric(values[["mrr_tie_adjusted"]]),
          mean_rank = as.numeric(values[["mean_rank"]]),
          stringsAsFactors = FALSE
        )
      }
    }
  }
  metric_table <- do.call(rbind, metrics)
  status_table <- do.call(rbind, statuses)
  coefficient_table <- if (length(coefficients) > 0L) do.call(rbind, coefficients) else data.frame()
  utils::write.csv(metric_table, file.path(output_dir, "ranking_metrics.csv"), row.names = FALSE)
  utils::write.csv(status_table, file.path(output_dir, "model_status.csv"), row.names = FALSE)
  utils::write.csv(coefficient_table, file.path(output_dir, "coefficients.csv"), row.names = FALSE)
  manifest <- list(
    purpose = "conditional_sender_sampled_risk_set_rhem_rolling_origin_pilot",
    observation = args$observation,
    input_dir = input_dir,
    eventnet_observation_sha256 = sha256_file(
      file.path(input_dir, "eventnet_output", paste0("enron_events_eventnet_", args$observation, ".csv"))
    ),
    eventnet_rows = nrow(data),
    choice_sets = length(unique(data$EVENT_INTERVAL)),
    requested_controls_per_event = requested_controls,
    eventnet_random_seed = random_seed,
    model_terms = models,
    statistic_transformation = "square_root_nonnegative",
    estimation = "survival::coxph conditional partial likelihood stratified by EVENT_INTERVAL",
    folds = folds,
    limitations = c(
      "The case-control table is one frozen Eventnet sample with 20 controls per observed event.",
      "Evaluation ranks receiver sets conditional on observed sender and observed receiver-set size.",
      "History covariates are Eventnet EVENT_INTERVAL quantities and depend on its declared within-timestamp order.",
      "Metrics are sampled-choice-set discrimination metrics, not calibrated probabilities over all possible events."
    )
  )
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), pretty = TRUE, auto_unbox = TRUE)
  write_summary(file.path(output_dir, "summary.md"), manifest, metric_table, status_table)
  cat("Conditional RHEM rolling-origin pilot complete.\n")
  cat("Choice sets: ", manifest$choice_sets, "; completed fit-folds: ", sum(status_table$status %in% c("fit_succeeded", "fit_succeeded_nonfinite_terms_dropped")), "/", nrow(status_table), "\n", sep = "")
  cat("Output bundle: ", output_dir, "\n", sep = "")
}

main()
