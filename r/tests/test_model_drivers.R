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

specs <- static_ladder_specs()
stopifnot(identical(specs$model, c("M0", "M1", "M2", "M3a", "M3b", "M3c", "M4a", "M4b", "M4c")))
stopifnot(grepl("mutual", specs$rhs[specs$model == "M1"], fixed = TRUE))
stopifnot(grepl("gwodegree", specs$rhs[specs$model == "M2"], fixed = TRUE))
stopifnot(grepl("gwesp", specs$rhs[specs$model == "M3a"], fixed = TRUE))
stopifnot(grepl("ctriple", specs$rhs[specs$model == "M4c"], fixed = TRUE))

identity <- proposition6_lagged_cn_identity()
stopifnot(isTRUE(identity$pass))
stopifnot(isTRUE(identity$logit_identity))
stopifnot(isTRUE(identity$rank_identity))
stopifnot(isTRUE(identity$odds_step_identity))
stopifnot(identical(identity$table$lagged_common_neighbors, c(2, 1, 1, 0)))

cat("PASS: static ERGM ladder specification and Proposition 6 lagged-CN identity.\n")
