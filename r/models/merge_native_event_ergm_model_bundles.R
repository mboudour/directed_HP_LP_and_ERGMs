#!/usr/bin/env Rscript

# Merge model-disjoint native-event ERGM score bundles sharing the same frozen
# split inputs. This recovery utility never refits, modifies candidates, or
# releases coefficient-, actor-, dyad-, or event-level records.

merge_native_model_usage <- function() {
  paste(
    "Usage: Rscript r/models/merge_native_event_ergm_model_bundles.R --input-dir=DIR ",
    "--bundle-specs=DIR::M0,M1;DIR::M4 --output-dir=DIR [--overwrite=TRUE]",
    sep = ""
  )
}

merge_native_model_driver_path <- function() {
  command_file <- commandArgs(trailingOnly = FALSE)
  command_file <- sub("^--file=", "", command_file[startsWith(command_file, "--file=")])
  candidate_dirs <- unique(c(
    dirname(command_file), file.path(getwd(), "r", "models"), file.path(getwd(), "..", "models")
  ))
  candidates <- file.path(candidate_dirs, "score_native_event_footprints.R")
  found <- candidates[file.exists(candidates)]
  if (length(found) == 0L) stop("Cannot locate sibling scorer.", call. = FALSE)
  normalizePath(found[[1L]], winslash = "/", mustWork = TRUE)
}

source(merge_native_model_driver_path())

merge_native_model_option <- function(options, name, default = NULL) {
  if (name %in% names(options)) options[[name]] else default
}

merge_native_model_path <- function(value) {
  normalizePath(value, winslash = "/", mustWork = TRUE)
}

merge_native_model_specs <- function(value) {
  entries <- trimws(unlist(strsplit(value, ";", fixed = TRUE)))
  entries <- entries[nzchar(entries)]
  pieces <- strsplit(entries, "::", fixed = TRUE)
  if (length(entries) == 0L || any(lengths(pieces) != 2L)) {
    stop("--bundle-specs entries must use DIR::MODEL[,MODEL] syntax.", call. = FALSE)
  }
  output <- lapply(pieces, function(piece) {
    models <- native_model_ids(piece[[2L]])
    list(path = merge_native_model_path(piece[[1L]]), models = models)
  })
  declared <- unlist(lapply(output, `[[`, "models"), use.names = FALSE)
  if (anyDuplicated(declared)) stop("Each model may occur in one bundle only.", call. = FALSE)
  output
}

merge_native_model_read <- function(directory, filename) {
  path <- file.path(directory, filename)
  if (!file.exists(path)) stop("Bundle lacks required output: ", path, call. = FALSE)
  output <- utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  if (nrow(output) == 0L) stop("Bundle output is empty: ", path, call. = FALSE)
  output
}

merge_native_model_key_check <- function(frame, columns, label) {
  key <- do.call(paste, c(frame[columns], sep = "\r"))
  if (anyDuplicated(key)) stop("Merged bundles duplicate ", label, " rows.", call. = FALSE)
}

merge_native_model_main <- function() {
  options <- parse_cli(commandArgs(trailingOnly = TRUE))
  if (!is.null(options$help)) {
    cat(merge_native_model_usage(), "\n")
    return(invisible(NULL))
  }
  required <- c("input-dir", "bundle-specs", "output-dir")
  missing <- required[!required %in% names(options)]
  if (length(missing) > 0L) stop("Missing required options: ", paste(missing, collapse = ", "), call. = FALSE)
  allowed <- c(required, "overwrite")
  unknown <- setdiff(names(options), allowed)
  if (length(unknown) > 0L) stop("Unknown option(s): ", paste(unknown, collapse = ", "), call. = FALSE)
  input_dir <- merge_native_model_path(merge_native_model_option(options, "input-dir"))
  specs <- merge_native_model_specs(merge_native_model_option(options, "bundle-specs"))
  output_dir <- prepare_output_dir(
    merge_native_model_option(options, "output-dir"),
    as_flag(merge_native_model_option(options, "overwrite", "FALSE"), "overwrite")
  )

  records <- vector("list", length(specs))
  score_rows <- list()
  metric_rows <- list()
  status_rows <- list()
  diagnostic_rows <- list()
  split_status <- NULL
  network_summary <- NULL
  guarded <- FALSE
  for (index in seq_along(specs)) {
    spec <- specs[[index]]
    manifest_path <- file.path(spec$path, "run_manifest.json")
    if (!file.exists(manifest_path)) stop("Bundle lacks manifest: ", manifest_path, call. = FALSE)
    manifest <- jsonlite::read_json(manifest_path, simplifyVector = TRUE)
    if (!(manifest$status %in% c("completed", "completed_with_declared_runtime_guard"))) {
      stop("Bundle has unsupported completion status: ", spec$path, call. = FALSE)
    }
    guarded <- guarded || identical(manifest$status, "completed_with_declared_runtime_guard")
    source_input <- normalizePath(manifest$input$input_dir, winslash = "/", mustWork = TRUE)
    if (!identical(source_input, input_dir)) stop("Bundle uses different frozen inputs: ", spec$path, call. = FALSE)
    source_models <- unlist(manifest$models)
    if (!all(spec$models %in% source_models)) stop("Bundle lacks requested model: ", spec$path, call. = FALSE)
    files <- c("event_footprint_scores.csv", "ranking_metrics.csv", "model_status.csv", "fit_diagnostics.csv")
    tables <- lapply(files, function(file) merge_native_model_read(spec$path, file))
    names(tables) <- files
    for (name in names(tables)) {
      if (!"model" %in% names(tables[[name]])) stop("Bundle table lacks model column: ", name, call. = FALSE)
      tables[[name]] <- tables[[name]][tables[[name]]$model %in% spec$models, , drop = FALSE]
      if (nrow(tables[[name]]) == 0L) stop("No selected rows in bundle table: ", name, call. = FALSE)
    }
    score_rows[[index]] <- tables[["event_footprint_scores.csv"]]
    metric_rows[[index]] <- tables[["ranking_metrics.csv"]]
    status_rows[[index]] <- tables[["model_status.csv"]]
    diagnostic_rows[[index]] <- tables[["fit_diagnostics.csv"]]
    candidate_split_status <- merge_native_model_read(spec$path, "split_status.csv")
    candidate_network_summary <- merge_native_model_read(spec$path, "network_summary.csv")
    if (is.null(split_status)) {
      split_status <- candidate_split_status
      network_summary <- candidate_network_summary
    } else if (!identical(network_summary, candidate_network_summary)) {
      stop("Network summaries differ across model bundles.", call. = FALSE)
    }
    records[[index]] <- list(path = spec$path, models = as.list(spec$models), status = manifest$status)
  }

  scores <- do.call(rbind, score_rows)
  metrics <- do.call(rbind, metric_rows)
  model_status <- do.call(rbind, status_rows)
  diagnostics <- do.call(rbind, diagnostic_rows)
  merge_native_model_key_check(scores, c("split", "model", "panel", "candidate_id"), "score")
  merge_native_model_key_check(metrics, c("split", "model", "panel", "score", "metric"), "metric")
  merge_native_model_key_check(model_status, c("split", "model"), "model-status")
  merge_native_model_key_check(diagnostics, c("split", "model"), "fit-diagnostic")
  order_frame <- function(frame, columns) frame[do.call(order, frame[columns]), , drop = FALSE]
  scores <- order_frame(scores, c("split", "model", "panel", "candidate_id"))
  metrics <- order_frame(metrics, c("split", "model", "panel", "score", "metric"))
  model_status <- order_frame(model_status, c("split", "model"))
  diagnostics <- order_frame(diagnostics, c("split", "model"))
  metric_summary <- native_summarise_metrics(metrics)
  diagnostic_summary <- native_summarise_fit_diagnostics(diagnostics)
  utils::write.csv(scores, file.path(output_dir, "event_footprint_scores.csv"), row.names = FALSE, na = "")
  utils::write.csv(metrics, file.path(output_dir, "ranking_metrics.csv"), row.names = FALSE, na = "")
  utils::write.csv(metric_summary, file.path(output_dir, "metric_summary.csv"), row.names = FALSE, na = "")
  utils::write.csv(model_status, file.path(output_dir, "model_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(diagnostics, file.path(output_dir, "fit_diagnostics.csv"), row.names = FALSE, na = "")
  utils::write.csv(diagnostic_summary, file.path(output_dir, "fit_diagnostics_summary.csv"), row.names = FALSE, na = "")
  utils::write.csv(split_status, file.path(output_dir, "split_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(network_summary, file.path(output_dir, "network_summary.csv"), row.names = FALSE, na = "")
  native_write_summary(file.path(output_dir, "summary.md"), basename(input_dir), split_status, metric_summary, diagnostic_summary)
  manifest <- list(
    status = if (guarded) "completed_with_declared_runtime_guard" else "completed",
    script = "r/models/merge_native_event_ergm_model_bundles.R",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(input_dir = input_dir), output_dir = output_dir,
    models = as.list(sort(unique(model_status$model))), source_bundles = records,
    counts = list(
      conditional_footprint_score_rows = nrow(scores), ranking_metric_rows = nrow(metrics),
      fit_diagnostic_rows = nrow(diagnostics), fit_diagnostic_summary_rows = nrow(diagnostic_summary)
    ),
    contract = "Model-disjoint score bundles use the same frozen splits; rows are untransformed and summaries are recomputed.",
    privacy = "Merged output is ignored; only aggregate outputs may be published through script 70."
  )
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), auto_unbox = TRUE, pretty = TRUE)
  message("Native-event ERGM model bundles merged. Output: ", output_dir)
}

if (sys.nframe() == 0L) merge_native_model_main()
