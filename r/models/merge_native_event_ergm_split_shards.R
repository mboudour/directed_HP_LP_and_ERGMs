#!/usr/bin/env Rscript

# Merge completed model-identical native-event ERGM shards that partition a fixed
# frozen split set. This is a recovery utility only: it never refits a model,
# alters scores, or emits coefficient-, event-, dyad-, or actor-level outputs.

merge_native_shard_usage <- function() {
  paste(
    "Usage: Rscript r/models/merge_native_event_ergm_split_shards.R --input-dir=DIR ",
    "--models=M0,M1 --shard-dirs=DIR[,DIR] --output-dir=DIR [options]",
    sep = ""
  )
}

merge_native_driver_path <- function() {
  command_file <- commandArgs(trailingOnly = FALSE)
  command_file <- sub("^--file=", "", command_file[startsWith(command_file, "--file=")])
  candidate_dirs <- unique(c(
    dirname(command_file), file.path(getwd(), "r", "models"), file.path(getwd(), "..", "models")
  ))
  candidates <- file.path(candidate_dirs, "score_native_event_footprints.R")
  found <- candidates[file.exists(candidates)]
  if (length(found) == 0L) {
    stop("Cannot locate sibling score_native_event_footprints.R.", call. = FALSE)
  }
  normalizePath(found[[1L]], winslash = "/", mustWork = TRUE)
}

source(merge_native_driver_path())

merge_native_option <- function(options, name, default = NULL) {
  if (name %in% names(options)) options[[name]] else default
}

merge_native_path <- function(value) {
  normalizePath(value, winslash = "/", mustWork = TRUE)
}

merge_native_read <- function(path) {
  table <- utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  if (nrow(table) == 0L) stop("Shard table is empty: ", path, call. = FALSE)
  table
}

merge_native_key_check <- function(frame, columns, label) {
  key <- do.call(paste, c(frame[columns], sep = "\r"))
  if (anyDuplicated(key)) stop("Merged shards duplicate ", label, " rows.", call. = FALSE)
  invisible(TRUE)
}

merge_native_bind <- function(shard_dirs, filename) {
  do.call(rbind, lapply(shard_dirs, function(directory) {
    path <- file.path(directory, filename)
    if (!file.exists(path)) stop("Shard lacks required output: ", path, call. = FALSE)
    merge_native_read(path)
  }))
}

merge_native_sort <- function(frame, columns) {
  frame[do.call(order, frame[columns]), , drop = FALSE]
}

merge_native_declared_incomplete <- function(value) {
  if (is.null(value) || !nzchar(value)) return(data.frame(model = character(), split = character()))
  entries <- trimws(unlist(strsplit(value, ",", fixed = TRUE)))
  pieces <- strsplit(entries, ":", fixed = TRUE)
  if (any(lengths(pieces) != 2L)) {
    stop("--declared-incomplete entries must use MODEL:SPLIT syntax.", call. = FALSE)
  }
  output <- data.frame(
    model = vapply(pieces, `[[`, character(1L), 1L),
    split = vapply(pieces, `[[`, character(1L), 2L),
    stringsAsFactors = FALSE
  )
  if (any(!nzchar(output$model)) || any(!nzchar(output$split)) || anyDuplicated(output)) {
    stop("--declared-incomplete entries must be unique nonempty MODEL:SPLIT pairs.", call. = FALSE)
  }
  output
}

merge_native_main <- function() {
  options <- parse_cli(commandArgs(trailingOnly = TRUE))
  if (!is.null(options$help)) {
    cat(merge_native_shard_usage(), "\n")
    return(invisible(NULL))
  }
  required <- c("input-dir", "models", "shard-dirs", "output-dir")
  missing <- required[!required %in% names(options)]
  if (length(missing) > 0L) {
    cat(merge_native_shard_usage(), "\n", file = stderr())
    stop("Missing required options: ", paste(paste0("--", missing), collapse = ", "), call. = FALSE)
  }
  allowed <- c(required, "declared-incomplete", "overwrite")
  unknown <- setdiff(names(options), allowed)
  if (length(unknown) > 0L) {
    stop("Unknown option(s): ", paste(paste0("--", unknown), collapse = ", "), call. = FALSE)
  }
  input_dir <- merge_native_path(merge_native_option(options, "input-dir"))
  models <- native_model_ids(merge_native_option(options, "models"))
  declared_incomplete <- merge_native_declared_incomplete(
    merge_native_option(options, "declared-incomplete", NULL)
  )
  shard_dirs <- trimws(unlist(strsplit(merge_native_option(options, "shard-dirs"), ",", fixed = TRUE)))
  shard_dirs <- shard_dirs[nzchar(shard_dirs)]
  if (length(shard_dirs) == 0L || anyDuplicated(shard_dirs)) {
    stop("--shard-dirs must provide unique completed shard directories.", call. = FALSE)
  }
  shard_dirs <- vapply(shard_dirs, merge_native_path, character(1L))
  output_dir <- prepare_output_dir(
    merge_native_option(options, "output-dir"),
    as_flag(merge_native_option(options, "overwrite", "FALSE"), "overwrite")
  )

  expected_splits <- native_discover_splits(input_dir)$split
  source_records <- vector("list", length(shard_dirs))
  selected_splits <- character()
  for (index in seq_along(shard_dirs)) {
    manifest_path <- file.path(shard_dirs[[index]], "run_manifest.json")
    if (!file.exists(manifest_path)) stop("Shard lacks manifest: ", manifest_path, call. = FALSE)
    manifest <- jsonlite::read_json(manifest_path, simplifyVector = TRUE)
    if (!identical(manifest$status, "completed")) {
      stop("Shard is not completed: ", shard_dirs[[index]], call. = FALSE)
    }
    source_models <- sort(unlist(manifest$models))
    if (!all(source_models %in% models)) {
      stop("Shard contains a model outside the requested model set: ", shard_dirs[[index]], call. = FALSE)
    }
    shard_input <- normalizePath(manifest$input$input_dir, winslash = "/", mustWork = TRUE)
    if (!identical(shard_input, input_dir)) {
      stop("Shard input is not the declared frozen input directory: ", shard_dirs[[index]], call. = FALSE)
    }
    shard_splits <- unlist(manifest$counts$selected_splits)
    if (length(shard_splits) == 0L) {
      stop("Shard manifest does not declare selected_splits: ", shard_dirs[[index]], call. = FALSE)
    }
    selected_splits <- c(selected_splits, shard_splits)
    source_records[[index]] <- list(path = shard_dirs[[index]], selected_splits = as.list(shard_splits))
  }
  if (anyDuplicated(selected_splits) || !identical(sort(selected_splits), sort(expected_splits))) {
    stop("Shard split sets must be disjoint and jointly equal the complete frozen split set.", call. = FALSE)
  }

  scores <- merge_native_bind(shard_dirs, "event_footprint_scores.csv")
  metrics <- merge_native_bind(shard_dirs, "ranking_metrics.csv")
  model_status <- merge_native_bind(shard_dirs, "model_status.csv")
  diagnostics <- merge_native_bind(shard_dirs, "fit_diagnostics.csv")
  split_status <- merge_native_bind(shard_dirs, "split_status.csv")
  network_summary <- merge_native_bind(shard_dirs, "network_summary.csv")
  merge_native_key_check(scores, c("split", "model", "panel", "candidate_id"), "score")
  merge_native_key_check(metrics, c("split", "model", "panel", "score", "metric"), "metric")
  merge_native_key_check(model_status, c("split", "model"), "model-status")
  merge_native_key_check(diagnostics, c("split", "model"), "fit-diagnostic")
  merge_native_key_check(split_status, "split", "split-status")
  merge_native_key_check(network_summary, "split", "network-summary")
  if (any(model_status$status != "scored") || any(diagnostics$outcome != "scored") ||
      any(split_status$status != "completed")) {
    stop("All declared shard model and split outcomes must be scored/completed.", call. = FALSE)
  }

  expected_pairs <- expand.grid(model = models, split = expected_splits, stringsAsFactors = FALSE)
  observed_pairs <- unique(model_status[c("model", "split")])
  pair_key <- function(frame) paste(frame$model, frame$split, sep = "\r")
  missing_pairs <- expected_pairs[!pair_key(expected_pairs) %in% pair_key(observed_pairs), , drop = FALSE]
  if (!identical(
    sort(pair_key(missing_pairs)), sort(pair_key(declared_incomplete))
  )) {
    stop(
      "Model/split coverage differs from --declared-incomplete; missing: ",
      paste(pair_key(missing_pairs), collapse = ", "), call. = FALSE
    )
  }
  if (nrow(declared_incomplete) > 0L) {
    specs <- static_ladder_specs()
    for (index in seq_len(nrow(declared_incomplete))) {
      model <- declared_incomplete$model[[index]]
      split <- declared_incomplete$split[[index]]
      identity <- native_split_identity(split)
      template <- model_status[model_status$split == split, , drop = FALSE][1L, , drop = FALSE]
      formula <- specs$rhs[specs$model == model]
      model_status <- rbind(model_status, data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        model = model, formula = paste("nw ~", formula), status = "fit_aborted_runtime_guard",
        fit_status = "fit_aborted_runtime_guard", prediction_status = "not_attempted",
        message = "MPLE did not complete within the declared runtime guard; score omitted.",
        warnings = "", unique_candidate_dyads = template$unique_candidate_dyads,
        event_candidates = template$event_candidates, stringsAsFactors = FALSE
      ))
      diagnostics <- rbind(diagnostics, data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        model = model, outcome = "fit_aborted_runtime_guard", fit_warning_count = 0L,
        prediction_warning_count = 0L, coefficient_count = 0L,
        nonfinite_coefficient_count = 0L, max_abs_finite_coefficient = NA_real_,
        conditional_dyads_scored = 0L, min_conditional_probability = NA_real_,
        max_conditional_probability = NA_real_, exact_zero_probability_count = 0L,
        exact_one_probability_count = 0L, stringsAsFactors = FALSE
      ))
      split_status$status[split_status$split == split] <- "completed_with_model_failures"
      split_status$message[split_status$split == split] <- "See model_status.csv for declared M3 runtime guard."
    }
  }

  scores <- merge_native_sort(scores, c("split", "model", "panel", "candidate_id"))
  metrics <- merge_native_sort(metrics, c("split", "model", "panel", "score", "metric"))
  model_status <- merge_native_sort(model_status, c("split", "model"))
  diagnostics <- merge_native_sort(diagnostics, c("split", "model"))
  split_status <- merge_native_sort(split_status, "split")
  network_summary <- merge_native_sort(network_summary, "split")
  metric_summary <- native_summarise_metrics(metrics)
  diagnostic_summary <- native_summarise_fit_diagnostics(diagnostics)
  utils::write.csv(scores, file.path(output_dir, "event_footprint_scores.csv"), row.names = FALSE, na = "")
  utils::write.csv(metrics, file.path(output_dir, "ranking_metrics.csv"), row.names = FALSE, na = "")
  utils::write.csv(metric_summary, file.path(output_dir, "metric_summary.csv"), row.names = FALSE, na = "")
  utils::write.csv(model_status, file.path(output_dir, "model_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(diagnostics, file.path(output_dir, "fit_diagnostics.csv"), row.names = FALSE, na = "")
  utils::write.csv(
    diagnostic_summary, file.path(output_dir, "fit_diagnostics_summary.csv"), row.names = FALSE, na = ""
  )
  utils::write.csv(split_status, file.path(output_dir, "split_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(network_summary, file.path(output_dir, "network_summary.csv"), row.names = FALSE, na = "")
  native_write_summary(
    file.path(output_dir, "summary.md"), basename(input_dir), split_status, metric_summary,
    diagnostic_summary
  )
  manifest <- list(
    status = if (nrow(declared_incomplete) == 0L) {
      "completed"
    } else {
      "completed_with_declared_runtime_guard"
    },
    script = "r/models/merge_native_event_ergm_split_shards.R",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(input_dir = input_dir),
    output_dir = output_dir,
    models = as.list(models),
    shard_sources = source_records,
    counts = list(
      expected_splits = length(expected_splits), selected_splits = as.list(sort(selected_splits)),
      declared_incomplete_model_splits = split(declared_incomplete$split, declared_incomplete$model),
      conditional_footprint_score_rows = nrow(scores), ranking_metric_rows = nrow(metrics),
      fit_diagnostic_rows = nrow(diagnostics), fit_diagnostic_summary_rows = nrow(diagnostic_summary)
    ),
    contract = paste(
      "Completed shards partition the original frozen split set and have identical models.",
      "Rows are concatenated without transformation; metric and diagnostic summaries are recomputed."
    ),
    privacy = "Merged output is ignored; aggregate-only publication remains controlled by script 70."
  )
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), auto_unbox = TRUE, pretty = TRUE)
  message("Native-event ERGM split shards merged. Output: ", output_dir)
}

if (sys.nframe() == 0L) merge_native_main()
