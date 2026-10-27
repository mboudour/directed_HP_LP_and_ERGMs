#!/usr/bin/env Rscript

# Fit each static ERGM only to one event-first observed projection, calculate
# exact conditional dyad probabilities, and aggregate them to L1, L1g, and L2
# graph-footprint scores for predeclared native-event candidate panels. The
# scores remain graph-footprint quantities: no output claims a probability that
# an email event itself occurred.

native_score_usage <- function() {
  paste(
    "Usage: Rscript r/models/score_native_event_footprints.R --input-dir=DIR --output-dir=DIR [options]",
    "",
    "Required input contract created by scripts/39_export_native_event_ergm_inputs.py:",
    "  DIR/nodes.csv                                      CSV with unique id column.",
    "  DIR/splits/<mechanism>_replicate_NNN/train_edges.csv       CSV with from,to.",
    "  DIR/splits/<mechanism>_replicate_NNN/candidate_dyads.csv   CSV with candidate_tail,candidate_head,label.",
    "  DIR/splits/<mechanism>_replicate_NNN/candidate_footprints.csv",
    "",
    "Options:",
    "  --models=M0,M1,M3,M4c       Static ERGM ladder IDs.",
    "  --splits=NAME[,NAME]        Optional explicit frozen split subset for checkpointed runs.",
    "  --estimate=MPLE             MPLE (default) or MCMLE.",
    "  --seed=20261013             Random seed before split-specific fitting.",
    "  --overwrite=FALSE           Refuse non-empty output unless TRUE.",
    "",
    "Outputs: event_footprint_scores.csv, ranking_metrics.csv, metric_summary.csv,",
    "model_status.csv, fit_diagnostics.csv, fit_diagnostics_summary.csv, split_status.csv,",
    "network_summary.csv, summary.md, run_manifest.json.",
    sep = "\n"
  )
}

native_score_masked_driver_path <- function() {
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
  candidates <- file.path(candidate_dirs, "score_masked_ergm.R")
  found <- candidates[file.exists(candidates)]
  if (length(found) == 0L) {
    stop("Cannot locate sibling driver score_masked_ergm.R.", call. = FALSE)
  }
  normalizePath(found[[1L]], winslash = "/", mustWork = TRUE)
}

# Reusing exact conditional-response extraction keeps all ERGM probability
# handling identical to the prior arc-level benchmark. This source call only
# defines helpers because score_masked_ergm_main() is guarded by sys.nframe().
source(native_score_masked_driver_path())

native_empty_scores <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), panel = character(),
    model = character(), candidate_id = character(), label = integer(), tail_nodes_json = character(),
    head_nodes_json = character(), tail_arity = integer(), head_arity = integer(), footprint_size = integer(),
    observed_footprint_arc_fraction = numeric(), L1 = numeric(), L1g = numeric(), L2 = numeric(),
    log_L2 = numeric(), stringsAsFactors = FALSE
  )
}

native_empty_model_status <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), model = character(),
    formula = character(), status = character(), fit_status = character(), prediction_status = character(),
    message = character(), warnings = character(), unique_candidate_dyads = integer(),
    event_candidates = integer(), stringsAsFactors = FALSE
  )
}

native_empty_split_status <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), status = character(),
    message = character(), training_edges_path = character(), candidate_dyads_path = character(),
    candidate_footprints_path = character(), nodes = integer(), training_edges = integer(),
    unique_candidate_dyads = integer(), event_candidates = integer(), stringsAsFactors = FALSE
  )
}

native_empty_metrics <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), panel = character(),
    model = character(), score = character(), metric = character(), value = numeric(),
    candidates = integer(), positives = integer(), negatives = integer(), k = integer(),
    status = character(), message = character(), stringsAsFactors = FALSE
  )
}

native_empty_fit_diagnostics <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), model = character(),
    outcome = character(), fit_warning_count = integer(), prediction_warning_count = integer(),
    coefficient_count = integer(), nonfinite_coefficient_count = integer(),
    max_abs_finite_coefficient = numeric(), conditional_dyads_scored = integer(),
    min_conditional_probability = numeric(), max_conditional_probability = numeric(),
    exact_zero_probability_count = integer(), exact_one_probability_count = integer(),
    stringsAsFactors = FALSE
  )
}

native_fit_diagnostic_row <- function(split, mechanism, replicate, model, outcome,
                                      fit_result, prediction_result = NULL) {
  # This records no coefficient values or dyad identities. It is deliberately a
  # numerical-stability diagnostic, not a coefficient-inference result.
  fit_warnings <- if (is.null(fit_result$warnings)) character() else fit_result$warnings
  prediction_warnings <- if (is.null(prediction_result) || is.null(prediction_result$warnings)) {
    character()
  } else {
    prediction_result$warnings
  }
  coefficients <- if (identical(fit_result$status, "fit_succeeded")) {
    tryCatch(stats::coef(fit_result$fit), error = function(error) numeric())
  } else {
    numeric()
  }
  finite_coefficients <- coefficients[is.finite(coefficients)]
  probabilities <- if (!is.null(prediction_result) &&
                       identical(prediction_result$status, "prediction_succeeded")) {
    prediction_result$predictions$conditional_probability
  } else {
    numeric()
  }
  data.frame(
    split = split, mechanism = mechanism, replicate = replicate, model = model, outcome = outcome,
    fit_warning_count = length(fit_warnings), prediction_warning_count = length(prediction_warnings),
    coefficient_count = length(coefficients),
    nonfinite_coefficient_count = sum(!is.finite(coefficients)),
    max_abs_finite_coefficient = if (length(finite_coefficients) > 0L) {
      max(abs(finite_coefficients))
    } else {
      NA_real_
    },
    conditional_dyads_scored = length(probabilities),
    min_conditional_probability = if (length(probabilities) > 0L) min(probabilities) else NA_real_,
    max_conditional_probability = if (length(probabilities) > 0L) max(probabilities) else NA_real_,
    exact_zero_probability_count = sum(probabilities == 0),
    exact_one_probability_count = sum(probabilities == 1),
    stringsAsFactors = FALSE
  )
}

native_summarise_fit_diagnostics <- function(diagnostics) {
  if (nrow(diagnostics) == 0L) {
    return(data.frame(
      model = character(), attempted_fits = integer(), scored_fits = integer(),
      fit_or_prediction_failures = integer(), fit_warning_count = integer(),
      prediction_warning_count = integer(), nonfinite_coefficient_count = integer(),
      max_abs_finite_coefficient = numeric(), conditional_dyads_scored = integer(),
      min_conditional_probability = numeric(), max_conditional_probability = numeric(),
      exact_zero_probability_count = integer(), exact_one_probability_count = integer(),
      stringsAsFactors = FALSE
    ))
  }
  do.call(rbind, lapply(split(diagnostics, diagnostics$model), function(frame) {
    finite_maxima <- frame$max_abs_finite_coefficient[is.finite(frame$max_abs_finite_coefficient)]
    finite_minima <- frame$min_conditional_probability[is.finite(frame$min_conditional_probability)]
    finite_prob_maxima <- frame$max_conditional_probability[is.finite(frame$max_conditional_probability)]
    data.frame(
      model = frame$model[[1L]], attempted_fits = nrow(frame),
      scored_fits = sum(frame$outcome == "scored"),
      fit_or_prediction_failures = sum(frame$outcome != "scored"),
      fit_warning_count = sum(frame$fit_warning_count),
      prediction_warning_count = sum(frame$prediction_warning_count),
      nonfinite_coefficient_count = sum(frame$nonfinite_coefficient_count),
      max_abs_finite_coefficient = if (length(finite_maxima) > 0L) max(finite_maxima) else NA_real_,
      conditional_dyads_scored = sum(frame$conditional_dyads_scored),
      min_conditional_probability = if (length(finite_minima) > 0L) min(finite_minima) else NA_real_,
      max_conditional_probability = if (length(finite_prob_maxima) > 0L) max(finite_prob_maxima) else NA_real_,
      exact_zero_probability_count = sum(frame$exact_zero_probability_count),
      exact_one_probability_count = sum(frame$exact_one_probability_count),
      stringsAsFactors = FALSE
    )
  }))
}

native_split_identity <- function(split) {
  pieces <- strsplit(split, "_replicate_", fixed = TRUE)[[1L]]
  if (length(pieces) != 2L || !grepl("^[0-9]+$", pieces[[2L]])) {
    stop("Invalid event-first split directory name: ", split, call. = FALSE)
  }
  list(mechanism = pieces[[1L]], replicate = as.integer(pieces[[2L]]))
}

native_discover_splits <- function(input_dir) {
  splits_dir <- file.path(input_dir, "splits")
  if (!dir.exists(splits_dir)) stop("Input directory lacks splits/: ", splits_dir, call. = FALSE)
  directories <- list.dirs(splits_dir, recursive = FALSE, full.names = FALSE)
  required <- c("train_edges.csv", "candidate_dyads.csv", "candidate_footprints.csv")
  complete <- directories[vapply(directories, function(split) {
    all(file.exists(file.path(splits_dir, split, required)))
  }, logical(1L))]
  if (length(complete) == 0L) {
    stop("No complete native-event ERGM input splits found in: ", splits_dir, call. = FALSE)
  }
  data.frame(
    split = sort(complete),
    train_edges_path = file.path(splits_dir, sort(complete), "train_edges.csv"),
    candidate_dyads_path = file.path(splits_dir, sort(complete), "candidate_dyads.csv"),
    candidate_footprints_path = file.path(splits_dir, sort(complete), "candidate_footprints.csv"),
    stringsAsFactors = FALSE
  )
}

native_select_splits <- function(split_files, splits_text = NULL) {
  # Restrict a run to an explicit, complete subset of frozen split directories.
  if (is.null(splits_text) || !nzchar(splits_text)) return(split_files)
  requested <- trimws(unlist(strsplit(splits_text, ",", fixed = TRUE)))
  requested <- requested[nzchar(requested)]
  if (length(requested) == 0L || anyDuplicated(requested)) {
    stop("--splits must name one or more unique frozen split directories.", call. = FALSE)
  }
  unknown <- setdiff(requested, split_files$split)
  if (length(unknown) > 0L) {
    stop(
      "--splits names unknown frozen split(s): ", paste(unknown, collapse = ", "),
      call. = FALSE
    )
  }
  selected <- split_files[split_files$split %in% requested, , drop = FALSE]
  selected[match(requested, selected$split), , drop = FALSE]
}

native_read_footprints <- function(path, node_ids) {
  if (!file.exists(path)) stop("Candidate footprint CSV does not exist: ", path, call. = FALSE)
  footprints <- utils::read.csv(
    path, stringsAsFactors = FALSE, check.names = FALSE, colClasses = "character", na.strings = "NA"
  )
  required <- c(
    "panel", "candidate_id", "label", "tail_nodes_json", "head_nodes_json", "tail_arity",
    "head_arity", "footprint_size", "candidate_tail", "candidate_head"
  )
  if (!all(required %in% names(footprints))) {
    stop("Candidate footprint CSV lacks required columns: ", paste(required, collapse = ", "), call. = FALSE)
  }
  if (anyNA(footprints[, required]) || any(!nzchar(footprints$panel)) ||
      any(!nzchar(footprints$candidate_id)) || any(!nzchar(footprints$candidate_tail)) ||
      any(!nzchar(footprints$candidate_head))) {
    stop("Candidate footprint CSV contains missing or empty required values.", call. = FALSE)
  }
  labels <- suppressWarnings(as.numeric(footprints$label))
  tail_arity <- suppressWarnings(as.numeric(footprints$tail_arity))
  head_arity <- suppressWarnings(as.numeric(footprints$head_arity))
  footprint_size <- suppressWarnings(as.numeric(footprints$footprint_size))
  if (anyNA(labels) || any(!labels %in% c(0, 1)) || anyNA(tail_arity) || anyNA(head_arity) ||
      anyNA(footprint_size) || any(tail_arity < 1L) || any(head_arity < 1L) || any(footprint_size < 1L)) {
    stop("Candidate footprint CSV contains invalid labels or role/footprint sizes.", call. = FALSE)
  }
  if (any(footprints$candidate_tail == footprints$candidate_head)) {
    stop("Candidate footprint CSV contains self-loop dyads.", call. = FALSE)
  }
  missing_nodes <- setdiff(unique(c(footprints$candidate_tail, footprints$candidate_head)), node_ids)
  if (length(missing_nodes) > 0L) {
    stop("Candidate footprint CSV references nodes absent from nodes.csv: ",
         paste(head(missing_nodes, 10L), collapse = ", "), call. = FALSE)
  }
  key <- paste(footprints$panel, footprints$candidate_id, sep = "\r")
  consistency <- aggregate(
    data.frame(label = labels, tail_arity = tail_arity, head_arity = head_arity,
               footprint_size = footprint_size, stringsAsFactors = FALSE),
    by = list(candidate_key = key),
    FUN = function(values) length(unique(values))
  )
  if (any(consistency$label != 1L) || any(consistency$tail_arity != 1L) ||
      any(consistency$head_arity != 1L) || any(consistency$footprint_size != 1L)) {
    stop("Candidate footprint metadata is inconsistent within an event candidate.", call. = FALSE)
  }
  dyad_key <- paste(key, footprints$candidate_tail, footprints$candidate_head, sep = "\r")
  if (anyDuplicated(dyad_key)) stop("Candidate footprint CSV repeats a candidate dyad.", call. = FALSE)
  data.frame(
    panel = footprints$panel,
    candidate_id = footprints$candidate_id,
    label = as.integer(labels),
    tail_nodes_json = footprints$tail_nodes_json,
    head_nodes_json = footprints$head_nodes_json,
    tail_arity = as.integer(tail_arity),
    head_arity = as.integer(head_arity),
    footprint_size = as.integer(footprint_size),
    candidate_tail = footprints$candidate_tail,
    candidate_head = footprints$candidate_head,
    stringsAsFactors = FALSE
  )
}

native_aggregate_footprints <- function(footprints, dyad_predictions, observed_edges) {
  prediction_key <- paste(dyad_predictions$candidate_tail, dyad_predictions$candidate_head, sep = "\r")
  footprint_key <- paste(footprints$candidate_tail, footprints$candidate_head, sep = "\r")
  positions <- match(footprint_key, prediction_key)
  if (anyNA(positions)) {
    stop("ERGM conditional prediction is missing a candidate footprint dyad.", call. = FALSE)
  }
  probabilities <- dyad_predictions$conditional_probability[positions]
  if (anyNA(probabilities) || any(!is.finite(probabilities)) || any(probabilities < 0 | probabilities > 1)) {
    stop("ERGM prediction returned invalid footprint probabilities.", call. = FALSE)
  }
  observed_keys <- paste(observed_edges$from, observed_edges$to, sep = "\r")
  footprints$conditional_probability <- probabilities
  footprints$observed_dyad <- as.integer(footprint_key %in% observed_keys)
  candidate_keys <- paste(footprints$panel, footprints$candidate_id, sep = "\r")
  groups <- split(seq_len(nrow(footprints)), candidate_keys)
  rows <- lapply(groups, function(indices) {
    group <- footprints[indices, , drop = FALSE]
    probability <- pmax(group$conditional_probability, .Machine$double.xmin)
    log_probability <- log(probability)
    expected_size <- group$footprint_size[[1L]]
    if (nrow(group) != expected_size) {
      stop("Candidate footprint row count differs from its declared footprint size.", call. = FALSE)
    }
    log_l2 <- sum(log_probability)
    l2 <- if (log_l2 < log(.Machine$double.xmin)) 0 else exp(log_l2)
    data.frame(
      panel = group$panel[[1L]],
      candidate_id = group$candidate_id[[1L]],
      label = group$label[[1L]],
      tail_nodes_json = group$tail_nodes_json[[1L]],
      head_nodes_json = group$head_nodes_json[[1L]],
      tail_arity = group$tail_arity[[1L]],
      head_arity = group$head_arity[[1L]],
      footprint_size = expected_size,
      observed_footprint_arc_fraction = mean(group$observed_dyad),
      L1 = mean(group$conditional_probability),
      L1g = exp(mean(log_probability)),
      L2 = l2,
      log_L2 = log_l2,
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

native_precision_recall_at_k <- function(labels, scores, k) {
  if (length(labels) == 0L || length(labels) != length(scores) || k < 1L || k > length(labels)) {
    stop("precision/recall@k requires aligned nonempty scores and valid k.", call. = FALSE)
  }
  positives <- sum(labels == 1L)
  if (positives < 1L) stop("precision/recall@k requires a positive label.", call. = FALSE)
  ordering <- order(-scores, seq_along(scores))
  ordered_scores <- scores[ordering]
  ordered_labels <- labels[ordering]
  selected <- 0L
  expected_true_positive <- 0
  start <- 1L
  while (start <= length(ordered_scores) && selected < k) {
    stop <- start
    while (stop < length(ordered_scores) && ordered_scores[[stop + 1L]] == ordered_scores[[start]]) {
      stop <- stop + 1L
    }
    group_labels <- ordered_labels[start:stop]
    take <- min(k - selected, length(group_labels))
    expected_true_positive <- expected_true_positive + take * mean(group_labels == 1L)
    selected <- selected + take
    start <- stop + 1L
  }
  c(precision_at_k = expected_true_positive / k, recall_at_k = expected_true_positive / positives)
}

native_rank_metrics <- function(scores, split, mechanism, replicate, model) {
  rows <- list()
  for (panel in sort(unique(scores$panel))) {
    panel_scores <- scores[scores$panel == panel, , drop = FALSE]
    labels <- panel_scores$label
    positive_count <- sum(labels == 1L)
    negative_count <- sum(labels == 0L)
    for (score_name in c("L1", "L1g", "L2")) {
      values <- if (score_name == "L2") panel_scores$log_L2 else panel_scores[[score_name]]
      if (positive_count == 0L || negative_count == 0L) {
        metric_rows <- data.frame(
          metric = c("roc_auc", "pr_auc", "precision_at_k", "recall_at_k"),
          value = NA_real_, status = "not_defined_degenerate_labels",
          message = "Ranking metrics require at least one positive and one negative.", stringsAsFactors = FALSE
        )
      } else {
        ranks <- rank(values, ties.method = "average")
        roc_value <- (sum(ranks[labels == 1L]) - positive_count * (positive_count + 1L) / 2) /
          (positive_count * negative_count)
        ordering <- order(-values, seq_along(values))
        ordered_values <- values[ordering]
        ordered_labels <- labels[ordering]
        group_end <- c(
          which(ordered_values[-1L] != ordered_values[-length(ordered_values)]),
          length(ordered_values)
        )
        cumulative_positive <- cumsum(ordered_labels == 1L)[group_end]
        precision <- cumulative_positive / group_end
        recall <- cumulative_positive / positive_count
        pr_value <- sum((recall - c(0, head(recall, -1L))) * precision)
        at_k <- native_precision_recall_at_k(labels, values, positive_count)
        metric_rows <- data.frame(
          metric = c("roc_auc", "pr_auc", "precision_at_k", "recall_at_k"),
          value = c(roc_value, pr_value, unname(at_k)), status = "calculated", message = "",
          stringsAsFactors = FALSE
        )
      }
      rows[[length(rows) + 1L]] <- cbind(
        data.frame(
          split = split, mechanism = mechanism, replicate = replicate, panel = panel,
          model = model, score = score_name, candidates = nrow(panel_scores),
          positives = positive_count, negatives = negative_count, k = positive_count,
          stringsAsFactors = FALSE
        ),
        metric_rows
      )
    }
  }
  do.call(rbind, rows)
}

native_summarise_metrics <- function(metrics) {
  valid <- metrics[metrics$status == "calculated" & !is.na(metrics$value), , drop = FALSE]
  if (nrow(valid) == 0L) {
    return(data.frame(
      panel = character(), mechanism = character(), model = character(), score = character(),
      metric = character(), completed_replicates = integer(), mean = numeric(), sd = numeric(),
      stringsAsFactors = FALSE
    ))
  }
  grouping <- interaction(valid$panel, valid$mechanism, valid$model, valid$score, valid$metric,
                          drop = TRUE, lex.order = TRUE)
  split_rows <- split(valid, grouping)
  do.call(rbind, lapply(split_rows, function(frame) {
    data.frame(
      panel = frame$panel[[1L]], mechanism = frame$mechanism[[1L]], model = frame$model[[1L]],
      score = frame$score[[1L]], metric = frame$metric[[1L]],
      completed_replicates = nrow(frame), mean = mean(frame$value),
      sd = if (nrow(frame) > 1L) stats::sd(frame$value) else 0,
      stringsAsFactors = FALSE
    )
  }))
}

native_write_summary <- function(path, dataset_id, split_status, metric_summary, fit_diagnostics) {
  completed <- split_status[split_status$status == "completed", , drop = FALSE]
  lines <- c(
    "# ERGM conditional footprint scores for native-event panels",
    "",
    paste0("- Dataset: `", dataset_id, "`"),
    "- Each static ERGM is fit separately to a frozen event-first observed projection.",
    "- L1 is the arithmetic mean of conditional-pseudolikelihood dyad scores; L1g is their geometric mean; L2 is their product.",
    "- L2 metrics use `log_L2`, a strictly monotone numeric representation of the L2 product.",
    "- These scores estimate **graph-footprint completion**, not the probability that a recorded native event occurred.",
    "",
    "## Completion status",
    "",
    paste0("- Frozen splits: ", nrow(split_status), " (completed without model failure: ", nrow(completed), ")"),
    "- Inspect `model_status.csv` before interpreting a model or split.",
    "",
    "## Ranking metrics across successful replicates",
    "",
    "| Panel | Mechanism | Model | Score | Metric | Replicates | Mean | SD |",
    "|---|---|---|---|---|---:|---:|---:|"
  )
  if (nrow(metric_summary) == 0L) {
    lines <- c(lines, "| — | — | — | — | — | 0 | — | — |")
  } else {
    metric_summary <- metric_summary[order(
      metric_summary$panel, metric_summary$mechanism, metric_summary$model,
      metric_summary$score, metric_summary$metric
    ), , drop = FALSE]
    for (index in seq_len(nrow(metric_summary))) {
      row <- metric_summary[index, , drop = FALSE]
      lines <- c(lines, sprintf(
        "| %s | %s | %s | %s | %s | %d | %.4f | %.4f |",
        row$panel, row$mechanism, row$model, row$score, row$metric,
        row$completed_replicates, row$mean, row$sd
      ))
    }
  }
  diagnostic_lines <- c(
    "",
    "## Aggregate MPLE numerical diagnostics",
    "",
    "No coefficient-inference claim is made. Models use MPLE without coefficient regularization or input standardization.",
    "The table reports fitting and conditional-score stability only; no coefficient values are released.",
    "",
    "| Model | fits attempted/scored | failures | fit/prediction warnings | nonfinite coefficients | max $|\\hat\\theta|$ | exact $p=0/1$ |",
    "|---|---:|---:|---:|---:|---:|---:|"
  )
  if (nrow(fit_diagnostics) == 0L) {
    diagnostic_lines <- c(diagnostic_lines, "| — | 0/0 | — | — | — | — | — |")
  } else {
    fit_diagnostics <- fit_diagnostics[order(fit_diagnostics$model), , drop = FALSE]
    for (index in seq_len(nrow(fit_diagnostics))) {
      row <- fit_diagnostics[index, , drop = FALSE]
      maximum <- if (is.finite(row$max_abs_finite_coefficient)) {
        sprintf("%.3f", row$max_abs_finite_coefficient)
      } else {
        "—"
      }
      diagnostic_lines <- c(diagnostic_lines, sprintf(
        "| %s | %d/%d | %d | %d/%d | %d | %s | %d/%d |",
        row$model, row$attempted_fits, row$scored_fits, row$fit_or_prediction_failures,
        row$fit_warning_count, row$prediction_warning_count, row$nonfinite_coefficient_count,
        maximum, row$exact_zero_probability_count, row$exact_one_probability_count
      ))
    }
  }
  lines <- c(
    lines,
    "",
    "This L2 is a product of single-dyad conditional-pseudolikelihood scores, not the matched-marginal L2 used for the plan's dependence increment. No L3-F joint simulation, L3-C concept score, or native-event probability is reported here. Those require separate conditional simulation and target-specific analysis.",
    diagnostic_lines,
    ""
  )
  writeLines(lines, path, useBytes = TRUE)
}

native_model_ids <- function(models_text) {
  # Parse model IDs before deciding whether M5 attributes are required.
  trimws(strsplit(models_text, ",", fixed = TRUE)[[1L]])
}

native_read_political_attributes <- function(path, node_ids) {
  # Read complete Senate attributes for M5/M6 political specifications.
  nodes <- utils::read.csv(
    path, stringsAsFactors = FALSE, check.names = FALSE, colClasses = "character", na.strings = "NA"
  )
  required <- c("id", "party", "state", "ideology", "majority_caucus", "seniority_years")
  if (!all(required %in% names(nodes))) {
    stop("Political models require nodes.csv columns: ", paste(required, collapse = ", "), ".", call. = FALSE)
  }
  if (anyDuplicated(nodes$id) || anyNA(nodes$id) || any(!nzchar(nodes$id))) {
    stop("Political-model nodes.csv IDs must be unique and nonempty.", call. = FALSE)
  }
  positions <- match(node_ids, nodes$id)
  if (anyNA(positions) || length(nodes$id) != length(node_ids)) {
    stop("Political-model nodes.csv IDs must match the fixed ERGM node universe exactly.", call. = FALSE)
  }
  attributes <- nodes[positions, required, drop = FALSE]
  if (anyNA(attributes$party) || anyNA(attributes$state) ||
      any(!nzchar(attributes$party)) || any(!nzchar(attributes$state))) {
    stop("Political models require nonmissing party and state attributes for every node.", call. = FALSE)
  }
  ideology <- suppressWarnings(as.numeric(attributes$ideology))
  if (anyNA(ideology) || any(!is.finite(ideology))) {
    stop("Political models require finite numeric ideology values for every node.", call. = FALSE)
  }
  attributes$ideology <- ideology
  majority_caucus <- suppressWarnings(as.numeric(attributes$majority_caucus))
  seniority_years <- suppressWarnings(as.numeric(attributes$seniority_years))
  if (anyNA(majority_caucus) || any(!majority_caucus %in% c(0, 1))) {
    stop("M6 requires binary majority_caucus values for every node.", call. = FALSE)
  }
  if (anyNA(seniority_years) || any(!is.finite(seniority_years)) || any(seniority_years < 0)) {
    stop("M6 requires finite nonnegative seniority_years values for every node.", call. = FALSE)
  }
  attributes$majority_caucus <- majority_caucus
  attributes$seniority_years <- seniority_years
  attributes
}

native_score_main <- function() {
  options <- parse_cli(commandArgs(trailingOnly = TRUE))
  if (!is.null(options$help)) {
    cat(native_score_usage(), "\n")
    return(invisible(NULL))
  }
  required <- c("input-dir", "output-dir")
  missing <- required[!required %in% names(options)]
  if (length(missing) > 0L) {
    cat(native_score_usage(), "\n", file = stderr())
    stop("Missing required options: ", paste(paste0("--", missing), collapse = ", "), call. = FALSE)
  }
  allowed <- c(required, "models", "splits", "estimate", "seed", "overwrite")
  unknown <- setdiff(names(options), allowed)
  if (length(unknown) > 0L) {
    stop("Unknown option(s): ", paste(paste0("--", unknown), collapse = ", "), call. = FALSE)
  }
  output_dir <- prepare_output_dir(option_value(options, "output-dir"), as_flag(option_value(options, "overwrite", "FALSE"), "overwrite"))
  input_dir <- normalizePath(option_value(options, "input-dir"), winslash = "/", mustWork = TRUE)
  models_text <- option_value(options, "models", "M0,M1,M3,M4c")
  selected_model_ids <- native_model_ids(models_text)
  uses_political_covariates <- any(c("M5", "M6") %in% selected_model_ids)
  uses_mutuality_sensitivity <- "M4c_no_mutual" %in% selected_model_ids
  selected_specs <- score_select_models(
    models_text,
    include_political = uses_political_covariates,
    include_mutuality_sensitivity = uses_mutuality_sensitivity
  )
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
  if (utils::packageVersion("ergm") < "4.12.0") {
    message_text <- paste0("ergm >= 4.12.0 is required; found ", utils::packageVersion("ergm"), ".")
    write_failure_manifest(file.path(output_dir, "run_manifest.json"), "failure_unsupported_ergm_version", message_text, options)
    stop(message_text, call. = FALSE)
  }

  node_path <- file.path(input_dir, "nodes.csv")
  node_ids <- read_node_ids(node_path, "id")
  vertex_attributes <- if (uses_political_covariates) {
    native_read_political_attributes(node_path, node_ids)
  } else {
    NULL
  }
  split_files <- native_select_splits(
    native_discover_splits(input_dir), option_value(options, "splits", NULL)
  )
  control <- ergm::control.ergm()
  all_scores <- list()
  all_metrics <- list()
  all_model_status <- list()
  all_fit_diagnostics <- list()
  all_split_status <- list()
  all_network_summary <- list()

  for (split_index in seq_len(nrow(split_files))) {
    split <- split_files$split[[split_index]]
    identity <- native_split_identity(split)
    edges <- tryCatch(
      read_directed_edges(split_files$train_edges_path[[split_index]], "from", "to", TRUE, node_ids),
      error = function(error) error
    )
    dyads <- tryCatch(score_read_candidates(split_files$candidate_dyads_path[[split_index]]), error = function(error) error)
    footprints <- tryCatch(native_read_footprints(split_files$candidate_footprints_path[[split_index]], node_ids), error = function(error) error)
    input_error <- if (inherits(edges, "error")) edges else if (inherits(dyads, "error")) dyads else if (inherits(footprints, "error")) footprints else NULL
    if (!is.null(input_error)) {
      all_split_status[[length(all_split_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        status = "input_failed", message = conditionMessage(input_error),
        training_edges_path = split_files$train_edges_path[[split_index]],
        candidate_dyads_path = split_files$candidate_dyads_path[[split_index]],
        candidate_footprints_path = split_files$candidate_footprints_path[[split_index]],
        nodes = length(node_ids), training_edges = NA_integer_, unique_candidate_dyads = NA_integer_,
        event_candidates = NA_integer_, stringsAsFactors = FALSE
      )
      next
    }
    candidate_validation <- tryCatch(score_validate_candidates(dyads, node_ids), error = function(error) error)
    if (inherits(candidate_validation, "error")) {
      all_split_status[[length(all_split_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        status = "input_failed", message = conditionMessage(candidate_validation),
        training_edges_path = split_files$train_edges_path[[split_index]],
        candidate_dyads_path = split_files$candidate_dyads_path[[split_index]],
        candidate_footprints_path = split_files$candidate_footprints_path[[split_index]],
        nodes = length(node_ids), training_edges = nrow(edges$edges), unique_candidate_dyads = nrow(dyads),
        event_candidates = length(unique(paste(footprints$panel, footprints$candidate_id, sep = "\r"))),
        stringsAsFactors = FALSE
      )
      next
    }
    nw <- tryCatch(make_network(edges, vertex_attributes), error = function(error) error)
    if (inherits(nw, "error")) {
      all_split_status[[length(all_split_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        status = "network_failed", message = conditionMessage(nw),
        training_edges_path = split_files$train_edges_path[[split_index]],
        candidate_dyads_path = split_files$candidate_dyads_path[[split_index]],
        candidate_footprints_path = split_files$candidate_footprints_path[[split_index]],
        nodes = length(node_ids), training_edges = nrow(edges$edges), unique_candidate_dyads = nrow(dyads),
        event_candidates = length(unique(paste(footprints$panel, footprints$candidate_id, sep = "\r"))),
        stringsAsFactors = FALSE
      )
      next
    }
    network_summary <- cbind(
      data.frame(split = split, mechanism = identity$mechanism, replicate = identity$replicate, stringsAsFactors = FALSE),
      network_summary_row(edges)
    )
    all_network_summary[[length(all_network_summary) + 1L]] <- network_summary
    model_outcomes <- character(nrow(selected_specs))
    for (model_index in seq_len(nrow(selected_specs))) {
      spec <- selected_specs[model_index, , drop = FALSE]
      fit_result <- fit_one_ergm(spec, nw, estimate, control)
      if (!identical(fit_result$status, "fit_succeeded")) {
        all_model_status[[length(all_model_status) + 1L]] <- data.frame(
          split = split, mechanism = identity$mechanism, replicate = identity$replicate,
          model = fit_result$model, formula = fit_result$formula, status = "fit_failed",
          fit_status = fit_result$status, prediction_status = "not_attempted", message = fit_result$message,
          warnings = paste(unique(fit_result$warnings), collapse = " | "), unique_candidate_dyads = nrow(dyads),
          event_candidates = length(unique(paste(footprints$panel, footprints$candidate_id, sep = "\r"))),
          stringsAsFactors = FALSE
        )
        all_fit_diagnostics[[length(all_fit_diagnostics) + 1L]] <- native_fit_diagnostic_row(
          split, identity$mechanism, identity$replicate, fit_result$model, "fit_failed", fit_result
        )
        model_outcomes[[model_index]] <- "fit_failed"
        next
      }
      prediction_result <- score_predict_candidates(fit_result$fit, dyads, node_ids)
      warning_text <- paste(unique(c(fit_result$warnings, prediction_result$warnings)), collapse = " | ")
      if (!identical(prediction_result$status, "prediction_succeeded")) {
        all_model_status[[length(all_model_status) + 1L]] <- data.frame(
          split = split, mechanism = identity$mechanism, replicate = identity$replicate,
          model = fit_result$model, formula = fit_result$formula, status = "prediction_failed",
          fit_status = fit_result$status, prediction_status = prediction_result$status,
          message = prediction_result$message, warnings = warning_text, unique_candidate_dyads = nrow(dyads),
          event_candidates = length(unique(paste(footprints$panel, footprints$candidate_id, sep = "\r"))),
          stringsAsFactors = FALSE
        )
        all_fit_diagnostics[[length(all_fit_diagnostics) + 1L]] <- native_fit_diagnostic_row(
          split, identity$mechanism, identity$replicate, fit_result$model,
          "prediction_failed", fit_result, prediction_result
        )
        model_outcomes[[model_index]] <- "prediction_failed"
        next
      }
      event_scores <- tryCatch(
        native_aggregate_footprints(footprints, prediction_result$predictions, edges$edges),
        error = function(error) error
      )
      if (inherits(event_scores, "error")) {
        all_model_status[[length(all_model_status) + 1L]] <- data.frame(
          split = split, mechanism = identity$mechanism, replicate = identity$replicate,
          model = fit_result$model, formula = fit_result$formula, status = "aggregation_failed",
          fit_status = fit_result$status, prediction_status = prediction_result$status,
          message = conditionMessage(event_scores), warnings = warning_text, unique_candidate_dyads = nrow(dyads),
          event_candidates = length(unique(paste(footprints$panel, footprints$candidate_id, sep = "\r"))),
          stringsAsFactors = FALSE
        )
        all_fit_diagnostics[[length(all_fit_diagnostics) + 1L]] <- native_fit_diagnostic_row(
          split, identity$mechanism, identity$replicate, fit_result$model,
          "aggregation_failed", fit_result, prediction_result
        )
        model_outcomes[[model_index]] <- "aggregation_failed"
        next
      }
      all_scores[[length(all_scores) + 1L]] <- cbind(
        data.frame(split = split, mechanism = identity$mechanism, replicate = identity$replicate,
                   model = fit_result$model, stringsAsFactors = FALSE),
        event_scores
      )
      all_metrics[[length(all_metrics) + 1L]] <- native_rank_metrics(
        event_scores, split, identity$mechanism, identity$replicate, fit_result$model
      )
      all_model_status[[length(all_model_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        model = fit_result$model, formula = fit_result$formula, status = "scored",
        fit_status = fit_result$status, prediction_status = prediction_result$status,
        message = "", warnings = warning_text, unique_candidate_dyads = nrow(dyads),
        event_candidates = nrow(event_scores), stringsAsFactors = FALSE
      )
      all_fit_diagnostics[[length(all_fit_diagnostics) + 1L]] <- native_fit_diagnostic_row(
        split, identity$mechanism, identity$replicate, fit_result$model, "scored",
        fit_result, prediction_result
      )
      model_outcomes[[model_index]] <- "scored"
    }
    all_split_status[[length(all_split_status) + 1L]] <- data.frame(
      split = split, mechanism = identity$mechanism, replicate = identity$replicate,
      status = if (all(model_outcomes == "scored")) "completed" else "completed_with_model_failures",
      message = if (all(model_outcomes == "scored")) "" else "See model_status.csv for model-specific detail.",
      training_edges_path = split_files$train_edges_path[[split_index]],
      candidate_dyads_path = split_files$candidate_dyads_path[[split_index]],
      candidate_footprints_path = split_files$candidate_footprints_path[[split_index]],
      nodes = length(node_ids), training_edges = nrow(edges$edges), unique_candidate_dyads = nrow(dyads),
      event_candidates = length(unique(paste(footprints$panel, footprints$candidate_id, sep = "\r"))),
      stringsAsFactors = FALSE
    )
  }

  scores <- if (length(all_scores) > 0L) do.call(rbind, all_scores) else native_empty_scores()
  metrics <- if (length(all_metrics) > 0L) do.call(rbind, all_metrics) else native_empty_metrics()
  model_status <- if (length(all_model_status) > 0L) do.call(rbind, all_model_status) else native_empty_model_status()
  fit_diagnostics <- if (length(all_fit_diagnostics) > 0L) {
    do.call(rbind, all_fit_diagnostics)
  } else {
    native_empty_fit_diagnostics()
  }
  split_status <- if (length(all_split_status) > 0L) do.call(rbind, all_split_status) else native_empty_split_status()
  network_summary <- if (length(all_network_summary) > 0L) do.call(rbind, all_network_summary) else data.frame()
  metric_summary <- native_summarise_metrics(metrics)
  fit_diagnostic_summary <- native_summarise_fit_diagnostics(fit_diagnostics)
  utils::write.csv(scores, file.path(output_dir, "event_footprint_scores.csv"), row.names = FALSE, na = "")
  utils::write.csv(metrics, file.path(output_dir, "ranking_metrics.csv"), row.names = FALSE, na = "")
  utils::write.csv(metric_summary, file.path(output_dir, "metric_summary.csv"), row.names = FALSE, na = "")
  utils::write.csv(model_status, file.path(output_dir, "model_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(fit_diagnostics, file.path(output_dir, "fit_diagnostics.csv"), row.names = FALSE, na = "")
  utils::write.csv(
    fit_diagnostic_summary,
    file.path(output_dir, "fit_diagnostics_summary.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(split_status, file.path(output_dir, "split_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(network_summary, file.path(output_dir, "network_summary.csv"), row.names = FALSE, na = "")
  native_write_summary(
    file.path(output_dir, "summary.md"), basename(input_dir), split_status, metric_summary,
    fit_diagnostic_summary
  )

  manifest <- list(
    status = if (nrow(split_status) == 0L || any(split_status$status != "completed")) "completed_with_failures" else "completed",
    script = "r/models/score_native_event_footprints.R",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(
      input_dir = input_dir,
      contract = if (uses_political_covariates) {
        "nodes.csv[id,party,state,ideology]; splits/<split>/train_edges.csv[from,to]; candidate_dyads.csv; candidate_footprints.csv"
      } else {
        "nodes.csv[id]; splits/<split>/train_edges.csv[from,to]; candidate_dyads.csv; candidate_footprints.csv"
      }
    ),
    output_dir = output_dir,
    models = as.list(selected_specs$model),
    political_covariates = if (uses_political_covariates) {
      list(
        terms = c("nodematch(party)", "nodematch(state)", "absdiff(ideology)"),
        interpretation = "Fixed 118th-Senate actor covariates supplied in nodes.csv."
      )
    } else {
      NULL
    },
    estimation = list(
      estimate = estimate, seed = seed,
      regularization = "none", input_standardization = "none"
    ),
    conditional_prediction = list(
      call = "predict(fit, conditional=TRUE, type='response', output='data.frame')",
      aggregation = "L1=mean(p); L1g=exp(mean(log(p))); L2=product(p) of single-dyad conditional-pseudolikelihood scores; metrics use log_L2 as a monotone numerically stable representation"
    ),
    metrics = list(
      scope = "ranking only: ROC-AUC, PR-AUC, precision@k, recall@k",
      excluded = "No accuracy, F1, MCC, log loss, or native-event probability claim is made."
    ),
    package_versions = lapply(package_names, function(package) as.character(utils::packageVersion(package))),
    counts = list(
      splits_discovered = nrow(split_files), splits_with_status = nrow(split_status),
      selected_splits = as.list(split_files$split),
      conditional_footprint_score_rows = nrow(scores), ranking_metric_rows = nrow(metrics),
      fit_diagnostic_rows = nrow(fit_diagnostics),
      fit_diagnostic_summary_rows = nrow(fit_diagnostic_summary)
    ),
    limitations = c(
      "Every model is fit to one split's observed projection only; full-network coefficients are not reused.",
      "L1, L1g, and L2 describe conditional dyadic graph-footprint completion, not a probability of a recorded native email event.",
      "L2 is a product of single-dyad conditional-pseudolikelihood scores. It is not the matched-marginal L2 or L3-F required for the plan's joint conditional ERGM simulation.",
      "Model fit, conditional prediction, and aggregation failures remain visible in model_status.csv."
    )
  )
  names(manifest$package_versions) <- package_names
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), auto_unbox = TRUE, pretty = TRUE, null = "null")
  message("Native-event ERGM footprint scoring complete. Output: ", output_dir)
}

if (sys.nframe() == 0L) native_score_main()
