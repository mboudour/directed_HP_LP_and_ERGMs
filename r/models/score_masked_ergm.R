#!/usr/bin/env Rscript

# Score static-pilot candidate dyads with conditional ERGM probabilities fitted
# only to each replicate's masked training network. This driver consumes the
# explicit mask-export contract; it never looks for raw data or fits a network
# reconstructed from a full edge list.
#
# Example:
# Rscript r/models/score_masked_ergm.R \
#   --input-dir=results/phase2/eu_core_static_pilot \
#   --output-dir=results/models/eu_core_masked_ergm \
#   --models=M0,M1,M3a,M4c --estimate=MPLE --seed=20261013

score_masked_ergm_usage <- function() {
  paste(
    "Usage: Rscript r/models/score_masked_ergm.R --input-dir=DIR --output-dir=DIR [options]",
    "",
    "Required input contract:",
    "  --input-dir=DIR              Static-pilot directory containing r_inputs/nodes.csv and masks/.",
    "  DIR/r_inputs/nodes.csv       CSV with a unique, nonempty id column.",
    "  DIR/masks/replicate_001_train_edges.csv      CSV with from,to.",
    "  DIR/masks/replicate_001_candidates.csv       CSV with candidate_tail,candidate_head,label (0/1).",
    "  Every replicate prefix must have exactly one training-edge and candidate CSV.",
    "",
    "Options:",
    "  --output-dir=DIR             New or explicitly overwritable output directory.",
    "  --models=M0,M1,M3a,M4c       Comma-separated static ladder model IDs.",
    "  --estimate=MPLE              MPLE (default) or MCMLE.",
    "  --seed=20261013              Random seed used before fitting masked networks.",
    "  --overwrite=FALSE            Refuse a non-empty output directory unless TRUE.",
    "",
    "Outputs: conditional_predictions.csv, metrics.csv, replicate_status.csv,",
    "model_status.csv, replicate_network_summary.csv, and run_manifest.json.",
    "Conditional probabilities are exact ERGM conditional tie probabilities for",
    "candidate dyads only; they are not full-network fits or forecasts.",
    sep = "\n"
  )
}

score_masked_ergm_ladder_path <- function() {
  command_file <- commandArgs(trailingOnly = FALSE)
  command_file <- sub("^--file=", "", command_file[startsWith(command_file, "--file=")])
  source_files <- unlist(lapply(sys.frames(), function(frame) {
    if (exists("ofile", envir = frame, inherits = FALSE)) {
      as.character(get("ofile", envir = frame, inherits = FALSE))
    } else {
      character()
    }
  }), use.names = FALSE)
  candidate_dirs <- unique(c(
    dirname(c(command_file, source_files)),
    file.path(getwd(), "r", "models"),
    file.path(getwd(), "..", "models"),
    file.path(getwd(), "..", "r", "models")
  ))
  candidates <- file.path(candidate_dirs, "static_directed_ergm_ladder.R")
  found <- candidates[file.exists(candidates)]
  if (length(found) == 0L) {
    stop("Cannot locate sibling driver static_directed_ergm_ladder.R.", call. = FALSE)
  }
  normalizePath(found[[1L]], winslash = "/", mustWork = TRUE)
}

# Reuse the static ladder's input, network, formula-specification, and fitting
# helpers. Sourcing is intentionally deferred to execution/source time, so this
# file remains testable without statnet installed.
source(score_masked_ergm_ladder_path())

score_empty_predictions <- function() {
  data.frame(
    replicate = character(),
    model = character(),
    candidate_tail = character(),
    candidate_head = character(),
    label = integer(),
    conditional_probability = numeric(),
    stringsAsFactors = FALSE
  )
}

score_empty_model_status <- function() {
  data.frame(
    replicate = character(),
    model = character(),
    formula = character(),
    status = character(),
    fit_status = character(),
    prediction_status = character(),
    message = character(),
    warnings = character(),
    candidates_requested = integer(),
    candidates_predicted = integer(),
    stringsAsFactors = FALSE
  )
}

score_empty_replicate_status <- function() {
  data.frame(
    replicate = character(),
    status = character(),
    message = character(),
    train_edges_path = character(),
    candidates_path = character(),
    nodes = integer(),
    training_edges = integer(),
    candidates = integer(),
    positives = integer(),
    negatives = integer(),
    self_loops_dropped = integer(),
    duplicate_edges_dropped = integer(),
    stringsAsFactors = FALSE
  )
}

score_empty_network_summary <- function() {
  data.frame(
    replicate = character(),
    nodes = integer(),
    directed_edges = integer(),
    possible_directed_edges = integer(),
    density = numeric(),
    reciprocal_pairs = numeric(),
    reciprocated_edge_fraction = numeric(),
    input_rows = integer(),
    self_loops_dropped = integer(),
    duplicate_rows_dropped = integer(),
    stringsAsFactors = FALSE
  )
}

score_empty_metrics <- function() {
  data.frame(
    replicate = character(),
    model = character(),
    metric = character(),
    value = numeric(),
    status = character(),
    message = character(),
    candidates = integer(),
    positives = integer(),
    negatives = integer(),
    stringsAsFactors = FALSE
  )
}

score_discover_replicates <- function(input_dir) {
  masks_dir <- file.path(input_dir, "masks")
  if (!dir.exists(masks_dir)) {
    stop("Input directory is missing masks/: ", masks_dir, call. = FALSE)
  }
  train_files <- list.files(
    masks_dir,
    pattern = "^replicate_[0-9]+_train_edges\\.csv$",
    full.names = FALSE
  )
  candidate_files <- list.files(
    masks_dir,
    pattern = "^replicate_[0-9]+_candidates\\.csv$",
    full.names = FALSE
  )
  train_ids <- sub("_train_edges\\.csv$", "", train_files)
  candidate_ids <- sub("_candidates\\.csv$", "", candidate_files)
  if (length(train_ids) == 0L && length(candidate_ids) == 0L) {
    stop("No replicate_*_train_edges.csv / replicate_*_candidates.csv pairs found in: ", masks_dir,
         call. = FALSE)
  }
  missing_train <- setdiff(candidate_ids, train_ids)
  missing_candidates <- setdiff(train_ids, candidate_ids)
  if (length(missing_train) > 0L || length(missing_candidates) > 0L) {
    fragments <- c(
      if (length(missing_train) > 0L) paste0("missing train edges for ", paste(missing_train, collapse = ", ")),
      if (length(missing_candidates) > 0L) paste0("missing candidates for ", paste(missing_candidates, collapse = ", "))
    )
    stop("Incomplete replicate pairs: ", paste(fragments, collapse = "; "), call. = FALSE)
  }
  replicate_ids <- sort(train_ids)
  data.frame(
    replicate = replicate_ids,
    train_edges_path = file.path(masks_dir, paste0(replicate_ids, "_train_edges.csv")),
    candidates_path = file.path(masks_dir, paste0(replicate_ids, "_candidates.csv")),
    stringsAsFactors = FALSE
  )
}

score_read_candidates <- function(path) {
  if (!file.exists(path)) stop("Candidate CSV does not exist: ", path, call. = FALSE)
  candidates <- utils::read.csv(
    path,
    stringsAsFactors = FALSE,
    check.names = FALSE,
    colClasses = "character",
    na.strings = "NA"
  )
  required <- c("candidate_tail", "candidate_head", "label")
  if (!all(required %in% names(candidates))) {
    stop("Candidate CSV must contain columns: ", paste(required, collapse = ", "), ".", call. = FALSE)
  }
  tail <- as.character(candidates$candidate_tail)
  head <- as.character(candidates$candidate_head)
  label_number <- suppressWarnings(as.numeric(as.character(candidates$label)))
  if (anyNA(tail) || anyNA(head) || any(!nzchar(tail)) || any(!nzchar(head))) {
    stop("Candidate endpoints may not be missing or empty.", call. = FALSE)
  }
  if (anyNA(label_number) || any(!is.finite(label_number)) ||
      any(label_number != floor(label_number)) || any(!label_number %in% c(0, 1))) {
    stop("Candidate labels must be binary numeric values 0 or 1.", call. = FALSE)
  }
  if (any(tail == head)) stop("Candidate CSV contains self-loops.", call. = FALSE)
  key <- paste(tail, head, sep = "\r")
  if (anyDuplicated(key)) stop("Candidate CSV contains duplicate directed dyads.", call. = FALSE)
  data.frame(
    candidate_tail = tail,
    candidate_head = head,
    label = as.integer(label_number),
    stringsAsFactors = FALSE
  )
}

score_validate_candidates <- function(candidates, node_ids) {
  missing_nodes <- setdiff(unique(c(candidates$candidate_tail, candidates$candidate_head)), node_ids)
  if (length(missing_nodes) > 0L) {
    stop("Candidates reference node IDs absent from r_inputs/nodes.csv: ",
         paste(head(missing_nodes, 10L), collapse = ", "), call. = FALSE)
  }
  invisible(candidates)
}

score_select_models <- function(models_text) {
  model_ids <- trimws(strsplit(models_text, ",", fixed = TRUE)[[1L]])
  if (length(model_ids) == 0L || any(!nzchar(model_ids))) {
    stop("--models must be a non-empty comma-separated model list.", call. = FALSE)
  }
  if (anyDuplicated(model_ids)) {
    stop("--models contains duplicate model IDs: ", paste(unique(model_ids[duplicated(model_ids)]), collapse = ", "),
         call. = FALSE)
  }
  available <- static_ladder_specs()
  unknown <- setdiff(model_ids, available$model)
  if (length(unknown) > 0L) {
    stop("Unknown ladder model ID(s): ", paste(unknown, collapse = ", "),
         ". Available: ", paste(available$model, collapse = ", "), call. = FALSE)
  }
  available[match(model_ids, available$model), , drop = FALSE]
}

score_as_node_indices <- function(x, name, node_count) {
  numeric_x <- suppressWarnings(as.numeric(as.character(x)))
  valid <- !is.na(numeric_x) & is.finite(numeric_x) & numeric_x == floor(numeric_x) &
    numeric_x >= 1 & numeric_x <= node_count
  if (!all(valid)) {
    stop("ergm::predict output has invalid ", name, " node indices.", call. = FALSE)
  }
  as.integer(numeric_x)
}

score_extract_candidate_probabilities <- function(prediction_frame, candidates, node_ids) {
  if (!is.data.frame(prediction_frame)) {
    stop("ergm::predict did not return a data.frame requested with output='data.frame'.", call. = FALSE)
  }
  required <- c("tail", "head", "p")
  if (!all(required %in% names(prediction_frame))) {
    stop("ergm::predict output lacks required columns: ", paste(required, collapse = ", "), ".", call. = FALSE)
  }
  tail_index <- score_as_node_indices(prediction_frame$tail, "tail", length(node_ids))
  head_index <- score_as_node_indices(prediction_frame$head, "head", length(node_ids))
  probability <- suppressWarnings(as.numeric(as.character(prediction_frame$p)))
  if (anyNA(probability) || any(!is.finite(probability)) || any(probability < 0 | probability > 1)) {
    stop("ergm::predict output contains invalid response-scale probabilities.", call. = FALSE)
  }

  # Statnet returns node indices. Map those indices through the exact labels in
  # r_inputs/nodes.csv before joining to the candidate panel; never join raw
  # numeric output positions directly to candidate IDs.
  indexed_predictions <- data.frame(
    candidate_tail = node_ids[tail_index],
    candidate_head = node_ids[head_index],
    conditional_probability = probability,
    stringsAsFactors = FALSE
  )
  prediction_key <- paste(indexed_predictions$candidate_tail, indexed_predictions$candidate_head, sep = "\r")
  if (anyDuplicated(prediction_key)) {
    stop("ergm::predict output contains duplicate directed dyads.", call. = FALSE)
  }
  candidate_key <- paste(candidates$candidate_tail, candidates$candidate_head, sep = "\r")
  match_index <- match(candidate_key, prediction_key)
  if (anyNA(match_index)) {
    missing <- which(is.na(match_index))
    show <- head(missing, 10L)
    missing_dyads <- paste(candidates$candidate_tail[show], candidates$candidate_head[show], sep = "->")
    stop("ergm::predict output is missing candidate dyad(s): ", paste(missing_dyads, collapse = ", "),
         call. = FALSE)
  }
  data.frame(
    candidate_tail = candidates$candidate_tail,
    candidate_head = candidates$candidate_head,
    label = candidates$label,
    conditional_probability = indexed_predictions$conditional_probability[match_index],
    stringsAsFactors = FALSE
  )
}

score_predict_candidates <- function(fit, candidates, node_ids) {
  warnings <- character()
  prediction <- withCallingHandlers(
    tryCatch(
      stats::predict(
        fit,
        conditional = TRUE,
        type = "response",
        output = "data.frame"
      ),
      error = function(error) error
    ),
    warning = function(warning) {
      warnings <<- c(warnings, conditionMessage(warning))
      invokeRestart("muffleWarning")
    }
  )
  if (inherits(prediction, "error")) {
    return(list(
      status = "prediction_failed",
      message = conditionMessage(prediction),
      warnings = warnings,
      predictions = NULL
    ))
  }
  extracted <- tryCatch(
    score_extract_candidate_probabilities(prediction, candidates, node_ids),
    error = function(error) error
  )
  if (inherits(extracted, "error")) {
    return(list(
      status = "prediction_failed",
      message = conditionMessage(extracted),
      warnings = warnings,
      predictions = NULL
    ))
  }
  list(status = "prediction_succeeded", message = "", warnings = warnings, predictions = extracted)
}

score_binary_metrics <- function(replicate, model, labels, probabilities) {
  candidate_count <- length(labels)
  positive_count <- sum(labels == 1L)
  negative_count <- sum(labels == 0L)
  metric_names <- c("roc_auc", "pr_auc")
  if (positive_count == 0L || negative_count == 0L) {
    return(data.frame(
      replicate = rep(replicate, length(metric_names)),
      model = rep(model, length(metric_names)),
      metric = metric_names,
      value = NA_real_,
      status = "not_defined_degenerate_labels",
      message = "ROC-AUC and PR-AUC require at least one positive and one negative candidate label.",
      candidates = rep(as.integer(candidate_count), length(metric_names)),
      positives = rep(as.integer(positive_count), length(metric_names)),
      negatives = rep(as.integer(negative_count), length(metric_names)),
      stringsAsFactors = FALSE
    ))
  }

  # ROC-AUC uses average ranks, so tied conditional probabilities receive the
  # standard half-credit. PR-AUC is threshold-step average precision with all
  # observations tied at a score handled as one threshold, not arbitrary rows.
  ranks <- rank(probabilities, ties.method = "average")
  roc_auc <- (sum(ranks[labels == 1L]) - positive_count * (positive_count + 1L) / 2) /
    (positive_count * negative_count)
  ordering <- order(-probabilities, seq_along(probabilities))
  ordered_scores <- probabilities[ordering]
  ordered_labels <- labels[ordering]
  group_end <- c(which(ordered_scores[-1L] != ordered_scores[-length(ordered_scores)]), length(ordered_scores))
  cumulative_positive <- cumsum(ordered_labels == 1L)[group_end]
  precision <- cumulative_positive / group_end
  recall <- cumulative_positive / positive_count
  pr_auc <- sum((recall - c(0, head(recall, -1L))) * precision)
  data.frame(
    replicate = rep(replicate, length(metric_names)),
    model = rep(model, length(metric_names)),
    metric = metric_names,
    value = c(roc_auc, pr_auc),
    status = "calculated",
    message = "",
    candidates = rep(as.integer(candidate_count), length(metric_names)),
    positives = rep(as.integer(positive_count), length(metric_names)),
    negatives = rep(as.integer(negative_count), length(metric_names)),
    stringsAsFactors = FALSE
  )
}

score_not_scored_metrics <- function(replicate, model, status, message, candidates) {
  labels <- if (is.null(candidates)) integer() else candidates$label
  data.frame(
    replicate = rep(replicate, 2L),
    model = rep(model, 2L),
    metric = c("roc_auc", "pr_auc"),
    value = NA_real_,
    status = status,
    message = message,
    candidates = rep(as.integer(length(labels)), 2L),
    positives = rep(as.integer(sum(labels == 1L)), 2L),
    negatives = rep(as.integer(sum(labels == 0L)), 2L),
    stringsAsFactors = FALSE
  )
}

score_write_csv <- function(frame, path) {
  utils::write.csv(frame, path, row.names = FALSE, na = "")
}

score_masked_ergm_main <- function() {
  options <- parse_cli(commandArgs(trailingOnly = TRUE))
  if (!is.null(options$help)) {
    cat(score_masked_ergm_usage(), "\n")
    return(invisible(NULL))
  }
  required_options <- c("input-dir", "output-dir")
  missing_options <- required_options[!required_options %in% names(options)]
  if (length(missing_options) > 0L) {
    cat(score_masked_ergm_usage(), "\n", file = stderr())
    stop("Missing required options: ", paste(paste0("--", missing_options), collapse = ", "), call. = FALSE)
  }
  allowed_options <- c(required_options, "models", "estimate", "seed", "overwrite")
  unknown_options <- setdiff(names(options), allowed_options)
  if (length(unknown_options) > 0L) {
    stop("Unknown option(s): ", paste(paste0("--", unknown_options), collapse = ", "), call. = FALSE)
  }

  overwrite <- as_flag(option_value(options, "overwrite", "FALSE"), "overwrite")
  output_dir <- prepare_output_dir(option_value(options, "output-dir"), overwrite)
  input_dir <- normalizePath(option_value(options, "input-dir"), winslash = "/", mustWork = TRUE)
  models_text <- option_value(options, "models", "M0,M1,M3a,M4c")
  selected_specs <- score_select_models(models_text)
  estimate <- toupper(option_value(options, "estimate", "MPLE"))
  if (!estimate %in% c("MPLE", "MCMLE")) stop("--estimate must be MPLE or MCMLE.", call. = FALSE)
  seed <- as_positive_number(option_value(options, "seed", "20261013"), "seed", integer = TRUE)
  set.seed(seed)

  package_names <- c("network", "ergm", "jsonlite")
  missing_packages <- package_names[!vapply(package_names, requireNamespace, logical(1L), quietly = TRUE)]
  if (length(missing_packages) > 0L) {
    message_text <- paste("Missing required R package(s):", paste(missing_packages, collapse = ", "),
                          ". Run Rscript r/bootstrap_renv.R first.")
    write_failure_manifest(file.path(output_dir, "run_manifest.json"), "failure_missing_packages", message_text, options)
    stop(message_text, call. = FALSE)
  }
  ergm_version <- utils::packageVersion("ergm")
  if (ergm_version < "4.12.0") {
    message_text <- paste0("ergm >= 4.12.0 is required for this conditional-prediction contract; found ", ergm_version, ".")
    write_failure_manifest(file.path(output_dir, "run_manifest.json"), "failure_unsupported_ergm_version", message_text, options)
    stop(message_text, call. = FALSE)
  }

  nodes_path <- file.path(input_dir, "r_inputs", "nodes.csv")
  node_ids <- read_node_ids(nodes_path, "id")
  replicate_files <- score_discover_replicates(input_dir)
  control <- ergm::control.ergm()

  prediction_rows <- list()
  model_status_rows <- list()
  replicate_status_rows <- list()
  network_summary_rows <- list()
  metric_rows <- list()

  for (replicate_index in seq_len(nrow(replicate_files))) {
    replicate <- replicate_files$replicate[[replicate_index]]
    train_path <- replicate_files$train_edges_path[[replicate_index]]
    candidates_path <- replicate_files$candidates_path[[replicate_index]]
    candidates <- tryCatch(score_read_candidates(candidates_path), error = function(error) error)
    edge_info <- tryCatch(
      read_directed_edges(train_path, "from", "to", drop_loops = TRUE, node_ids = node_ids),
      error = function(error) error
    )
    input_error <- if (inherits(candidates, "error")) candidates else if (inherits(edge_info, "error")) edge_info else NULL
    if (!is.null(input_error)) {
      replicate_status_rows[[length(replicate_status_rows) + 1L]] <- data.frame(
        replicate = replicate,
        status = "input_failed",
        message = conditionMessage(input_error),
        train_edges_path = train_path,
        candidates_path = candidates_path,
        nodes = as.integer(length(node_ids)),
        training_edges = NA_integer_,
        candidates = NA_integer_,
        positives = NA_integer_,
        negatives = NA_integer_,
        self_loops_dropped = NA_integer_,
        duplicate_edges_dropped = NA_integer_,
        stringsAsFactors = FALSE
      )
      next
    }
    candidate_validation <- tryCatch(score_validate_candidates(candidates, node_ids), error = function(error) error)
    if (inherits(candidate_validation, "error")) {
      replicate_status_rows[[length(replicate_status_rows) + 1L]] <- data.frame(
        replicate = replicate,
        status = "input_failed",
        message = conditionMessage(candidate_validation),
        train_edges_path = train_path,
        candidates_path = candidates_path,
        nodes = as.integer(length(node_ids)),
        training_edges = as.integer(nrow(edge_info$edges)),
        candidates = as.integer(nrow(candidates)),
        positives = as.integer(sum(candidates$label == 1L)),
        negatives = as.integer(sum(candidates$label == 0L)),
        self_loops_dropped = as.integer(edge_info$self_loops_dropped),
        duplicate_edges_dropped = as.integer(edge_info$duplicate_rows_dropped),
        stringsAsFactors = FALSE
      )
      next
    }

    nw <- tryCatch(make_network(edge_info), error = function(error) error)
    if (inherits(nw, "error")) {
      replicate_status_rows[[length(replicate_status_rows) + 1L]] <- data.frame(
        replicate = replicate,
        status = "network_failed",
        message = conditionMessage(nw),
        train_edges_path = train_path,
        candidates_path = candidates_path,
        nodes = as.integer(length(node_ids)),
        training_edges = as.integer(nrow(edge_info$edges)),
        candidates = as.integer(nrow(candidates)),
        positives = as.integer(sum(candidates$label == 1L)),
        negatives = as.integer(sum(candidates$label == 0L)),
        self_loops_dropped = as.integer(edge_info$self_loops_dropped),
        duplicate_edges_dropped = as.integer(edge_info$duplicate_rows_dropped),
        stringsAsFactors = FALSE
      )
      next
    }

    summary_row <- network_summary_row(edge_info)
    summary_row <- cbind(data.frame(replicate = replicate, stringsAsFactors = FALSE), summary_row)
    network_summary_rows[[length(network_summary_rows) + 1L]] <- summary_row
    replicate_model_status <- character(nrow(selected_specs))
    for (model_index in seq_len(nrow(selected_specs))) {
      spec <- selected_specs[model_index, , drop = FALSE]
      fit_result <- fit_one_ergm(spec, nw, estimate, control)
      if (!identical(fit_result$status, "fit_succeeded")) {
        model_status_rows[[length(model_status_rows) + 1L]] <- data.frame(
          replicate = replicate,
          model = fit_result$model,
          formula = fit_result$formula,
          status = "fit_failed",
          fit_status = fit_result$status,
          prediction_status = "not_attempted",
          message = fit_result$message,
          warnings = paste(unique(fit_result$warnings), collapse = " | "),
          candidates_requested = as.integer(nrow(candidates)),
          candidates_predicted = 0L,
          stringsAsFactors = FALSE
        )
        metric_rows[[length(metric_rows) + 1L]] <- score_not_scored_metrics(
          replicate, fit_result$model, "not_scored_fit_failed", fit_result$message, candidates
        )
        replicate_model_status[[model_index]] <- "fit_failed"
        next
      }

      prediction_result <- score_predict_candidates(fit_result$fit, candidates, node_ids)
      warning_text <- paste(unique(c(fit_result$warnings, prediction_result$warnings)), collapse = " | ")
      if (!identical(prediction_result$status, "prediction_succeeded")) {
        model_status_rows[[length(model_status_rows) + 1L]] <- data.frame(
          replicate = replicate,
          model = fit_result$model,
          formula = fit_result$formula,
          status = "prediction_failed",
          fit_status = fit_result$status,
          prediction_status = prediction_result$status,
          message = prediction_result$message,
          warnings = warning_text,
          candidates_requested = as.integer(nrow(candidates)),
          candidates_predicted = 0L,
          stringsAsFactors = FALSE
        )
        metric_rows[[length(metric_rows) + 1L]] <- score_not_scored_metrics(
          replicate, fit_result$model, "not_scored_prediction_failed", prediction_result$message, candidates
        )
        replicate_model_status[[model_index]] <- "prediction_failed"
        next
      }

      prediction_frame <- prediction_result$predictions
      prediction_rows[[length(prediction_rows) + 1L]] <- cbind(
        data.frame(replicate = replicate, model = fit_result$model, stringsAsFactors = FALSE),
        prediction_frame
      )
      model_status_rows[[length(model_status_rows) + 1L]] <- data.frame(
        replicate = replicate,
        model = fit_result$model,
        formula = fit_result$formula,
        status = "scored",
        fit_status = fit_result$status,
        prediction_status = prediction_result$status,
        message = "",
        warnings = warning_text,
        candidates_requested = as.integer(nrow(candidates)),
        candidates_predicted = as.integer(nrow(prediction_frame)),
        stringsAsFactors = FALSE
      )
      metric_rows[[length(metric_rows) + 1L]] <- score_binary_metrics(
        replicate, fit_result$model, prediction_frame$label, prediction_frame$conditional_probability
      )
      replicate_model_status[[model_index]] <- "scored"
    }

    replicate_status_rows[[length(replicate_status_rows) + 1L]] <- data.frame(
      replicate = replicate,
      status = if (all(replicate_model_status == "scored")) "completed" else "completed_with_model_failures",
      message = if (all(replicate_model_status == "scored")) "" else "See model_status.csv for model-specific fit or prediction failures.",
      train_edges_path = train_path,
      candidates_path = candidates_path,
      nodes = as.integer(length(node_ids)),
      training_edges = as.integer(nrow(edge_info$edges)),
      candidates = as.integer(nrow(candidates)),
      positives = as.integer(sum(candidates$label == 1L)),
      negatives = as.integer(sum(candidates$label == 0L)),
      self_loops_dropped = as.integer(edge_info$self_loops_dropped),
      duplicate_edges_dropped = as.integer(edge_info$duplicate_rows_dropped),
      stringsAsFactors = FALSE
    )
  }

  predictions <- if (length(prediction_rows) > 0L) do.call(rbind, prediction_rows) else score_empty_predictions()
  model_status <- if (length(model_status_rows) > 0L) do.call(rbind, model_status_rows) else score_empty_model_status()
  replicate_status <- if (length(replicate_status_rows) > 0L) do.call(rbind, replicate_status_rows) else score_empty_replicate_status()
  network_summary <- if (length(network_summary_rows) > 0L) do.call(rbind, network_summary_rows) else score_empty_network_summary()
  metrics <- if (length(metric_rows) > 0L) do.call(rbind, metric_rows) else score_empty_metrics()

  score_write_csv(predictions, file.path(output_dir, "conditional_predictions.csv"))
  score_write_csv(metrics, file.path(output_dir, "metrics.csv"))
  score_write_csv(replicate_status, file.path(output_dir, "replicate_status.csv"))
  score_write_csv(model_status, file.path(output_dir, "model_status.csv"))
  score_write_csv(network_summary, file.path(output_dir, "replicate_network_summary.csv"))

  run_status <- if (nrow(replicate_status) == 0L || any(replicate_status$status != "completed")) {
    "completed_with_failures"
  } else {
    "completed"
  }
  manifest <- list(
    status = run_status,
    script = "r/models/score_masked_ergm.R",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(
      input_dir = input_dir,
      nodes_csv = normalizePath(nodes_path, winslash = "/", mustWork = FALSE),
      masks_dir = normalizePath(file.path(input_dir, "masks"), winslash = "/", mustWork = FALSE),
      contract = "r_inputs/nodes.csv[id]; masks/replicate_NNN_train_edges.csv[from,to]; masks/replicate_NNN_candidates.csv[candidate_tail,candidate_head,label]"
    ),
    output_dir = output_dir,
    models = as.list(selected_specs$model),
    estimation = list(estimate = estimate, seed = seed),
    conditional_prediction = list(
      call = "predict(fit, conditional=TRUE, type='response', output='data.frame')",
      extraction = "Statnet tail/head node indices are mapped through r_inputs/nodes.csv id labels, then joined only to candidate dyads."
    ),
    metrics = list(
      roc_auc = "Average-rank ROC-AUC; ties receive half-credit.",
      pr_auc = "Threshold-step average precision with equal-score rows pooled.",
      degenerate_labels = "Both values are NA with status not_defined_degenerate_labels when a replicate has no positives or no negatives."
    ),
    package_versions = lapply(package_names, function(package) as.character(utils::packageVersion(package))),
    counts = list(
      replicates_discovered = nrow(replicate_files),
      replicates_with_status = nrow(replicate_status),
      models_requested_per_valid_replicate = nrow(selected_specs),
      conditional_prediction_rows = nrow(predictions)
    ),
    limitations = c(
      "Each model is fitted only to that replicate's train_edges CSV and scores only its candidate CSV; no full-network fit is substituted.",
      "Conditional probabilities condition on all other dyads in the fitted masked training network. They are not simulated forecasts or estimates of an unconditional future tie probability.",
      "ERGM terms can be unavailable, degenerate, or fail to estimate on a masked network. These errors are retained per replicate/model in model_status.csv rather than replaced by another model.",
      "No raw-data paths, full pilot edge list, or source-data provenance are inferred or read by this driver."
    )
  )
  names(manifest$package_versions) <- package_names
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), auto_unbox = TRUE, pretty = TRUE, null = "null")
  message("Masked ERGM conditional scoring complete. Output: ", output_dir)
}

if (sys.nframe() == 0L) score_masked_ergm_main()
