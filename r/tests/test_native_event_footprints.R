#!/usr/bin/env Rscript

# Dependency-light tests for native event ERGM footprint aggregation. The driver
# sources only helpers until its main is called, so statnet is unnecessary here.

locate_driver <- function(filename) {
  candidates <- c(
    file.path("r", "models", filename),
    file.path("..", "models", filename),
    file.path("..", "r", "models", filename)
  )
  found <- candidates[file.exists(candidates)]
  if (length(found) == 0L) stop("Cannot locate model driver: ", filename, call. = FALSE)
  normalizePath(found[[1L]], winslash = "/", mustWork = TRUE)
}

source(locate_driver("score_native_event_footprints.R"))

footprints <- data.frame(
  panel = c("random", "random", "random"),
  candidate_id = c("positive", "positive", "negative"),
  label = c(1L, 1L, 0L),
  tail_nodes_json = c('["a"]', '["a"]', '["b"]'),
  head_nodes_json = c('["b","c"]', '["b","c"]', '["a"]'),
  tail_arity = c(1L, 1L, 1L),
  head_arity = c(2L, 2L, 1L),
  footprint_size = c(2L, 2L, 1L),
  candidate_tail = c("a", "a", "b"),
  candidate_head = c("b", "c", "a"),
  stringsAsFactors = FALSE
)
predictions <- data.frame(
  candidate_tail = c("a", "a", "b"),
  candidate_head = c("b", "c", "a"),
  label = c(0L, 0L, 0L),
  conditional_probability = c(0.2, 0.8, 0.5),
  stringsAsFactors = FALSE
)
observed <- data.frame(from = c("a", "b"), to = c("b", "a"), stringsAsFactors = FALSE)
aggregated <- native_aggregate_footprints(footprints, predictions, observed)
stopifnot(nrow(aggregated) == 2L)
positive <- aggregated[aggregated$candidate_id == "positive", , drop = FALSE]
negative <- aggregated[aggregated$candidate_id == "negative", , drop = FALSE]
stopifnot(isTRUE(all.equal(positive$L1, 0.5)))
stopifnot(isTRUE(all.equal(positive$L1g, 0.4)))
stopifnot(isTRUE(all.equal(positive$L2, 0.16)))
stopifnot(isTRUE(all.equal(positive$log_L2, log(0.16))))
stopifnot(isTRUE(all.equal(positive$observed_footprint_arc_fraction, 0.5)))
stopifnot(isTRUE(all.equal(negative$L1, 0.5)))
stopifnot(isTRUE(all.equal(negative$observed_footprint_arc_fraction, 1)))

rank_metrics <- native_rank_metrics(
  data.frame(
    panel = c("random", "random", "random", "random"),
    label = c(1L, 1L, 0L, 0L),
    L1 = c(0.8, 0.7, 0.3, 0.2),
    L1g = c(0.8, 0.7, 0.3, 0.2),
    L2 = c(0.64, 0.49, 0.09, 0.04),
    log_L2 = log(c(0.64, 0.49, 0.09, 0.04)),
    stringsAsFactors = FALSE
  ),
  "mcar_replicate_001", "mcar", 1L, "M3"
)
stopifnot(all(rank_metrics$status == "calculated"))
stopifnot(all(rank_metrics$value[rank_metrics$metric %in% c("roc_auc", "pr_auc")] == 1))

source_text <- paste(readLines(locate_driver("score_native_event_footprints.R"), warn = FALSE), collapse = "\n")
stopifnot(grepl("L1=mean\\(p\\)", source_text))
stopifnot(grepl("L2=product\\(p\\)", source_text))
stopifnot(grepl("score_predict_candidates", source_text, fixed = TRUE))
stopifnot(grepl("predict\\(fit, conditional=TRUE", source_text))

cat("PASS: native-event ERGM footprint aggregation and ranking-metric contract.\n")
