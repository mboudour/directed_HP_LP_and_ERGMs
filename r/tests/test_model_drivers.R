#!/usr/bin/env Rscript

# Dependency-light smoke tests. They source pure helpers only, so they can run
# before statnet is installed:
#   Rscript r/tests/test_model_drivers.R

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

source(locate_driver("static_directed_ergm_ladder.R"))
source(locate_driver("temporal_lagged_check.R"))
score_driver <- locate_driver("score_masked_ergm.R")
source(score_driver)

specs <- static_ladder_specs()
stopifnot(identical(specs$model, c("M0", "M1", "M2", "M3", "M4", "M4c")))
stopifnot(grepl("mutual", specs$rhs[specs$model == "M1"], fixed = TRUE))
stopifnot(grepl("gwodegree", specs$rhs[specs$model == "M2"], fixed = TRUE))
stopifnot(grepl("type='OTP'", specs$rhs[specs$model == "M3"], fixed = TRUE))
stopifnot(grepl("type='OSP'", specs$rhs[specs$model == "M4"], fixed = TRUE))
stopifnot(grepl("type='ISP'", specs$rhs[specs$model == "M4"], fixed = TRUE))
stopifnot(grepl("ctriple", specs$rhs[specs$model == "M4c"], fixed = TRUE))

identity <- proposition6_lagged_cn_identity()
stopifnot(isTRUE(identity$pass))
stopifnot(isTRUE(identity$logit_identity))
stopifnot(isTRUE(identity$rank_identity))
stopifnot(isTRUE(identity$odds_step_identity))
stopifnot(identical(identity$table$lagged_common_neighbors, c(2, 1, 1, 0)))

masked_specs <- score_select_models("M0, M1, M3, M4c")
stopifnot(identical(masked_specs$model, c("M0", "M1", "M3", "M4c")))
stopifnot(identical(
  names(score_empty_predictions()),
  c("replicate", "model", "candidate_tail", "candidate_head", "label", "conditional_probability")
))

# Statnet's data-frame output contains node indices. The scorer must map those
# positions through nodes.csv labels before matching the candidate dyads.
candidate_fixture <- data.frame(
  candidate_tail = c("z", "001"),
  candidate_head = c("001", "alpha"),
  label = c(1L, 0L),
  stringsAsFactors = FALSE
)
prediction_fixture <- data.frame(
  tail = c(1L, 3L),
  head = c(2L, 1L),
  p = c(0.25, 0.75),
  stringsAsFactors = FALSE
)
extracted_fixture <- score_extract_candidate_probabilities(
  prediction_fixture,
  candidate_fixture,
  c("001", "alpha", "z")
)
stopifnot(identical(extracted_fixture$conditional_probability, c(0.75, 0.25)))
stopifnot(identical(extracted_fixture$candidate_tail, candidate_fixture$candidate_tail))
stopifnot(identical(extracted_fixture$candidate_head, candidate_fixture$candidate_head))

tie_metrics <- score_binary_metrics(
  "replicate_001", "M0", c(1L, 0L), c(0.5, 0.5)
)
stopifnot(identical(tie_metrics$metric, score_metric_names()))
stopifnot(isTRUE(all.equal(
  tie_metrics$value[tie_metrics$metric %in% c("roc_auc", "pr_auc")],
  c(0.5, 0.5)
)))
stopifnot(isTRUE(all.equal(
  tie_metrics$value[tie_metrics$metric %in% c("accuracy", "precision", "recall", "f1")],
  c(0.5, 0.5, 1, 2 / 3)
)))
stopifnot(identical(
  tie_metrics$status[tie_metrics$metric == "matthews_correlation"],
  "not_defined_single_predicted_class"
))
stopifnot(isTRUE(all.equal(
  tie_metrics$value[tie_metrics$metric == "log_loss"],
  log(2)
)))
large_labels <- rep(c(1L, 0L), 50000L)
large_probabilities <- rep(c(0.9, 0.1), 50000L)
large_metrics <- score_binary_metrics(
  "replicate_large", "M0", large_labels, large_probabilities
)
stopifnot(is.finite(large_metrics$value[large_metrics$metric == "matthews_correlation"]))
stopifnot(is.finite(large_metrics$value[large_metrics$metric == "roc_auc"]))
stopifnot(is.finite(large_metrics$value[large_metrics$metric == "pr_auc"]))
degenerate_metrics <- score_binary_metrics(
  "replicate_001", "M0", c(1L, 1L), c(0.8, 0.2)
)
stopifnot(identical(
  degenerate_metrics$status,
  rep("not_defined_degenerate_labels", length(score_metric_names()))
))
stopifnot(all(is.na(degenerate_metrics$value)))

# IDs are opaque labels. Leading zeros must survive the shared static helpers.
fixture_dir <- tempfile("masked_ergm_contract_")
dir.create(fixture_dir)
nodes_path <- file.path(fixture_dir, "nodes.csv")
edges_path <- file.path(fixture_dir, "edges.csv")
writeLines(c("id", "001", "002"), nodes_path)
writeLines(c("from,to", "001,002"), edges_path)
fixture_nodes <- read_node_ids(nodes_path, "id")
fixture_edges <- read_directed_edges(edges_path, "from", "to", TRUE, fixture_nodes)
stopifnot(identical(fixture_nodes, c("001", "002")))
stopifnot(identical(fixture_edges$edges$from, "001"))
panel_path <- file.path(fixture_dir, "panel.csv")
writeLines(c("time,from,to", "001,001,002", "002,002,001"), panel_path)
temporal_fixture <- read_panel_edges(panel_path, "time", "from", "to", TRUE, fixture_nodes, "numeric")
stopifnot(identical(temporal_fixture$times, c("001", "002")))
stopifnot(identical(temporal_fixture$edges$from, c("001", "002")))
masks_dir <- file.path(fixture_dir, "masks")
dir.create(masks_dir)
train_fixture <- file.path(masks_dir, "replicate_001_train_edges.csv")
candidate_fixture_path <- file.path(masks_dir, "replicate_001_candidates.csv")
file.copy(edges_path, train_fixture)
writeLines(
  c("candidate_tail,candidate_head,label", "001,002,1", "002,001,0"),
  candidate_fixture_path
)
discovered_fixture <- score_discover_replicates(fixture_dir)
read_candidate_fixture <- score_read_candidates(candidate_fixture_path)
stopifnot(identical(discovered_fixture$replicate, "replicate_001"))
stopifnot(identical(read_candidate_fixture$label, c(1L, 0L)))
stopifnot(identical(read_candidate_fixture$candidate_tail, c("001", "002")))
unlink(fixture_dir, recursive = TRUE)

# This source-level check pins the required exact conditional-response call
# without requiring statnet or a fit in the smoke-test environment.
score_source <- paste(readLines(score_driver, warn = FALSE), collapse = "\n")
stopifnot(grepl("stats::predict\\(", score_source))
stopifnot(grepl("conditional = TRUE", score_source, fixed = TRUE))
stopifnot(grepl('type = "response"', score_source, fixed = TRUE))
stopifnot(grepl('output = "data.frame"', score_source, fixed = TRUE))

cat("PASS: static ladder, masked-ERGM conditional scoring contract, and Proposition 6 lagged-CN identity.\n")
