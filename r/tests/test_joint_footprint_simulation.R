#!/usr/bin/env Rscript

# Dependency-light tests for candidate-specific observation constraints. Statnet
# itself is deliberately not required for these contract checks.

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

source(locate_driver("simulate_joint_footprint_ergm.R"))

driver_text <- paste(readLines(locate_driver("simulate_joint_footprint_ergm.R"), warn = FALSE), collapse = "\n")
stopifnot(grepl('estimate = "MLE"', driver_text, fixed = TRUE))
stopifnot(grepl("eval.loglik = FALSE", driver_text, fixed = TRUE))
stopifnot(grepl('"split"', driver_text, fixed = TRUE))
stopifnot(grepl("MCMLE.samplesize = fit_samplesize", driver_text, fixed = TRUE))

footprints <- data.frame(
  panel = c("random", "random", "random", "random", "multi_dyad", "multi_dyad"),
  candidate_id = c("positive", "positive", "negative", "negative", "multi", "multi"),
  label = c(1L, 1L, 0L, 0L, 1L, 1L),
  tail_nodes_json = c('["a"]', '["a"]', '["a"]', '["a"]', '["x"]', '["x"]'),
  head_nodes_json = c('["b","c"]', '["b","c"]', '["b","d"]', '["b","d"]', '["c","e"]', '["c","e"]'),
  tail_arity = c(1L, 1L, 1L, 1L, 1L, 1L),
  head_arity = c(2L, 2L, 2L, 2L, 2L, 2L),
  footprint_size = c(2L, 2L, 2L, 2L, 2L, 2L),
  candidate_tail = c("a", "a", "a", "a", "x", "x"),
  candidate_head = c("b", "c", "b", "d", "c", "e"),
  stringsAsFactors = FALSE
)
observed <- data.frame(
  from = c("a", "a", "c", "c", "e"),
  to = c("b", "d", "a", "x", "x"),
  stringsAsFactors = FALSE
)

candidates <- joint_candidate_table(footprints, observed)
positive <- candidates[candidates$candidate_id == "positive", , drop = FALSE]
negative <- candidates[candidates$candidate_id == "negative", , drop = FALSE]
stopifnot(positive$observed_footprint_arcs == 1L)
stopifnot(positive$unobserved_footprint_arcs == 1L)
stopifnot(positive$all_unknown_dyads_reverse_observed)
stopifnot(negative$observed_footprint_arcs == 2L)
stopifnot(negative$unobserved_footprint_arcs == 0L)

selected <- joint_select_candidates(
  candidates, min_unknown = 0L, max_unknown = 1L, max_per_label = 1L, seed = 5L
)
stopifnot(nrow(selected) == 2L)
stopifnot(identical(sort(selected$label), c(0L, 1L)))
stopifnot(all(selected$unobserved_footprint_arcs <= 1L))

multi_selected <- joint_select_candidates(
  candidates, min_unknown = 2L, max_unknown = 2L, max_per_label = 1L, seed = 5L,
  require_reverse_observed = TRUE
)
stopifnot(nrow(multi_selected) == 1L)
stopifnot(identical(multi_selected$candidate_id, "multi"))
stopifnot(multi_selected$unknown_dyads_with_reverse_observed == 2L)

positive_dyads <- joint_candidate_dyads(footprints, positive)
stopifnot(identical(positive_dyads$candidate_head, c("b", "c")))

fixed_outcome <- joint_simulation_scores(
  fit = NULL,
  nw = NULL,
  candidate = negative,
  footprint_dyads = joint_candidate_dyads(footprints, negative),
  observed_edges = observed,
  node_ids = c("a", "b", "c", "d"),
  nsim = 5L,
  mcmc_burnin = 1L,
  mcmc_interval = 1L,
  seed = 1L
)
stopifnot(identical(fixed_outcome$status, "fixed_complete_footprint"))
stopifnot(fixed_outcome$L3_F == 1)
stopifnot(fixed_outcome$L2 == 1)
stopifnot(fixed_outcome$delta_dep == 0)

cat("PASS: joint footprint candidate constraints and fixed-observation scoring contract.\n")
