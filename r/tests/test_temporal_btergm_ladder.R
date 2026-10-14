#!/usr/bin/env Rscript

# Base-R/source contract only: no network, ergm, btergm, or jsonlite required.
# Run from the repository root: Rscript r/tests/test_temporal_btergm_ladder.R
candidates <- c(file.path("r", "models", "temporal_btergm_ladder.R"),
                file.path("..", "models", "temporal_btergm_ladder.R"),
                file.path("..", "r", "models", "temporal_btergm_ladder.R"))
driver <- candidates[file.exists(candidates)][[1L]]
env <- new.env(parent = globalenv())
sys.source(driver, envir = env)
expect_error <- function(expr, pattern = NULL) {
  result <- tryCatch(force(expr), error = function(e) e)
  stopifnot(inherits(result, "error"))
  if (!is.null(pattern)) stopifnot(grepl(pattern, conditionMessage(result), fixed = TRUE))
  invisible(result)
}

specs <- env$tbe_ladder_specs()
stopifnot(identical(specs$model, c("T_tt", "T0", "T1", "T2", "T2_minus_H")))
stopifnot(identical(specs$rhs[[1L]], "edges + edgecov(lag_total_CN)"))
t0 <- paste("edges + mutual + memory(type='autoregression', lag=1) + delrecip(lag=1)",
            "+ edgecov(lag_oi) + edgecov(lag_oo) + edgecov(lag_ii)",
            "+ edgecov(lag_outdegree_source) + edgecov(lag_indegree_target)")
degrees <- "gwodegree(0.5, fixed=TRUE) + gwidegree(0.5, fixed=TRUE)"
esp <- "gwesp(0.5, fixed=TRUE, type='OTP') + gwesp(0.5, fixed=TRUE, type='OSP') + gwesp(0.5, fixed=TRUE, type='ISP')"
stopifnot(identical(specs$rhs[[2L]], t0))
stopifnot(identical(specs$rhs[[3L]], paste(t0, "+", degrees)))
stopifnot(identical(specs$rhs[[4L]], paste(t0, "+", degrees, "+", esp)))
stopifnot(identical(specs$rhs[[5L]], paste("edges + mutual +", degrees, "+", esp)))
stopifnot(!grepl("lag_|memory|delrecip|edgecov", specs$rhs[[5L]]))
stopifnot(all(grepl("conditional score estimator only", specs$interpretation, fixed = TRUE)))
stopifnot(all(grepl("never forecasts", specs$interpretation, fixed = TRUE)))
stopifnot(all(grepl("estimator, not a competitor", specs$bootstrap_role, fixed = TRUE)))
custom <- env$tbe_ladder_specs(0.7, 0.8)
stopifnot(grepl("gwodegree(0.7, fixed=TRUE)", custom$rhs[[4L]], fixed = TRUE))
stopifnot(grepl("gwesp(0.8, fixed=TRUE, type='ISP')", custom$rhs[[4L]], fixed = TRUE))

options <- list(input = "panel.csv", nodes = "nodes.csv", "output-dir" = "out")
config <- env$tbe_config(options)
stopifnot(identical(config[["bootstrap-reps"]], 20L), identical(config$parallel, "no"),
          identical(config$ncpus, 1L), identical(config$models, specs$model),
          identical(config[["degree-decay"]], 0.5), identical(config[["esp-decay"]], 0.5))
parsed <- env$tbe_parse_cli(c("--input=panel.csv", "--nodes", "nodes.csv", "--output-dir=out",
                              "--models=T2,T_tt", "--parallel=snow", "--ncpus=2", "--seed=0", "--overwrite=yes"))
selected <- env$tbe_config(parsed)
stopifnot(identical(selected$models, c("T2", "T_tt")), identical(selected$seed, 0L), selected$overwrite)
expect_error(env$tbe_config(c(options, list(models = "T0,T0"))))
expect_error(env$tbe_config(c(options, list(models = "M0"))))
expect_error(env$tbe_config(c(options, list(models = "T0,"))))
expect_error(env$tbe_config(c(options, list(models = "T0,,T1"))))
expect_error(env$tbe_config(c(options, list("bootstrap-reps" = "0"))))
expect_error(env$tbe_config(c(options, list("degree-decay" = "NaN"))))
expect_error(env$tbe_config(c(options, list(ncpus = "1.5"))))
expect_error(env$tbe_config(c(options, list(parallel = "yes"))))
expect_error(env$tbe_config(c(options, list(forecast = "TRUE"))))
expect_error(env$tbe_parse_cli(c("--input=a", "--input=b")))

fixture <- tempfile("temporal_btergm_contract_")
dir.create(fixture)
nodes_file <- file.path(fixture, "nodes.csv")
panel_file <- file.path(fixture, "panel.csv")
writeLines(c("id", "001", "002", "003", "004", "005"), nodes_file)
# Intentionally shuffled chronology, with an isolated actor 005 at every time.
writeLines(c("time,from,to", "003,004,001", "001,001,003", "002,003,004",
             "001,003,002", "001,001,004", "001,002,004", "001,004,002"), panel_file)
nodes <- env$tbe_read_nodes(nodes_file)
panel <- env$tbe_read_panel(panel_file, nodes)
stopifnot(identical(nodes, sprintf("%03d", 1:5)))
stopifnot(identical(panel$times, c("001", "002", "003")))
stopifnot(all(nchar(panel$edges$from) == 3L), identical(panel$edges$from[[1L]], "001"))
env$tbe_validate_bounds(panel, config)
small <- config; small[["max-nodes"]] <- 4L
expect_error(env$tbe_validate_bounds(panel, small), "no subsetting")
adj <- env$tbe_adjacencies(panel)
stopifnot(identical(names(adj), panel$times))
stopifnot(all(vapply(adj, function(a) identical(dim(a), c(5L, 5L)), logical(1L))))
stopifnot(all(vapply(adj, function(a) identical(rownames(a), nodes), logical(1L))))
stopifnot(all(vapply(adj, function(a) sum(a["005", ]) + sum(a[, "005"]) == 0, logical(1L))))
lag <- env$tbe_lag_covariates(adj)
stopifnot(identical(names(lag), c("lag_total_CN", "lag_oi", "lag_oo", "lag_ii", "lag_outdegree_source", "lag_indegree_target")))
stopifnot(all(vapply(lag, function(x) length(x) == 3L && all(x[[1L]] == 0), logical(1L))))
stopifnot(lag$lag_oi[[2L]]["001", "002"] == 2,
          lag$lag_oo[[2L]]["001", "002"] == 1,
          lag$lag_ii[[2L]]["003", "004"] == 1,
          lag$lag_total_CN[[2L]]["001", "002"] == 3,
          lag$lag_outdegree_source[[2L]]["001", "002"] == 2,
          lag$lag_indegree_target[[2L]]["001", "002"] == 2)
stopifnot(all(vapply(lag, function(x) all(diag(x[[2L]]) == 0), logical(1L))))
# The final panel must not affect a preceding panel's regressors.
future <- adj; future[[3L]]["005", "001"] <- 1L
stopifnot(identical(lag, env$tbe_lag_covariates(future)))
# Pure formula-context helpers accept matrix placeholders, without a package fit.
for (i in seq_len(nrow(specs))) {
  formula <- env$tbe_formula_context(specs[i, , drop = FALSE], adj, lag)
  context <- environment(formula)
  temporal <- specs$uses_temporal_terms[[i]]
  stopifnot(length(context$networks) == if (temporal) 3L else 2L)
  stopifnot(identical(names(context$networks), if (temporal) panel$times else panel$times[-1L]))
  stopifnot(identical(context$lag_total_CN[[if (temporal) 2L else 1L]], lag$lag_total_CN[[2L]]))
}

stopifnot(identical(env$tbe_order_times(c("2025-01", "2024-12"))$times, c("2024-12", "2025-01")))
expect_error(env$tbe_order_times("001"), "At least two panels")
expect_error(env$tbe_order_times(c("001", "003")), "exact consecutive")
expect_error(env$tbe_order_times(c("1", "01")), "aliased labels")
expect_error(env$tbe_order_times(c("2025-01", "2025-03")), "exact consecutive")
expect_error(env$tbe_order_times(c("2025-13", "2026-01")), "Invalid")
expect_error(env$tbe_order_times(c("spring", "summer")), "cadence is never guessed")
writeLines(c("time,from,to", "001,001,002", "002,001,002", "002,001,002"), panel_file)
expect_error(env$tbe_read_panel(panel_file, nodes), "Duplicate")
writeLines(c("time,from,to", "001,001,002", "002,001,001"), panel_file)
expect_error(env$tbe_read_panel(panel_file, nodes), "Self-loops")
writeLines(c("time,from,to", "001,001,002", "002,001,999"), panel_file)
expect_error(env$tbe_read_panel(panel_file, nodes), "absent from nodes.csv")
writeLines(c("id", "001", "001"), nodes_file)
expect_error(env$tbe_read_nodes(nodes_file), "unique")
# The fallback writer must preserve arbitrary path/message characters in JSON.
manifest <- file.path(fixture, "run_manifest.json")
env$tbe_failure_manifest(manifest, "failure_missing_packages", 'quote" backslash\\ newline\n tab\t',
                         options, c("btergm", "network", "jsonlite"))
json <- paste(readLines(manifest), collapse = "\n")
stopifnot(grepl('"forecasts": false', json, fixed = TRUE), grepl('"simulated_probabilities": false', json, fixed = TRUE))
stopifnot(grepl('"missing_packages": ["btergm","network","jsonlite"]', json, fixed = TRUE))
stopifnot(grepl("\\u000a", json, fixed = TRUE), grepl("\\u0009", json, fixed = TRUE))
unlink(fixture, recursive = TRUE)

# Test direct S4 coefficient and bootstrap-slot extraction without btergm.
methods::setClass("tbe_contract_boot", representation(t = "matrix"))
methods::setClass("tbe_contract_fit", representation(coef = "numeric", boot = "tbe_contract_boot"))
fixture_boot <- methods::new(
  "tbe_contract_boot",
  t = matrix(c(-1.4, 0.2, -1.2, 0.4, -1.0, 0.6), ncol = 2L, byrow = TRUE,
             dimnames = list(NULL, c("edges", "mutual")))
)
fixture_fit <- methods::new("tbe_contract_fit", coef = c(edges = -1.2, mutual = 0.4), boot = fixture_boot)
extracted <- env$tbe_extract_coefficients("T0", fixture_fit, 20L)
stopifnot(identical(extracted$ci_status, c("empirical_percentile", "empirical_percentile")),
          all(is.finite(extracted$ci_lower)), all(is.finite(extracted$ci_upper)),
          identical(extracted$bootstrap_reps_finite, c(3L, 3L)))
empty_boot <- methods::new("tbe_contract_boot", t = matrix(numeric(), nrow = 0L, ncol = 0L))
failed_fit <- methods::new("tbe_contract_fit", coef = c(edges = -1.2, mutual = 0.4), boot = empty_boot)
failed_ci <- env$tbe_extract_coefficients("T0", failed_fit, 20L)
stopifnot(all(failed_ci$ci_status == "not_extractable"), all(is.na(failed_ci$ci_lower)),
          all(is.na(failed_ci$ci_upper)), identical(failed_ci$estimate, extracted$estimate))

# Pin the package API and forbid prediction/simulation/alternative estimators.
source_text <- paste(readLines(driver, warn = FALSE), collapse = "\n")
stopifnot(grepl("btergm::btergm(formula, R = config[[\"bootstrap-reps\"]], parallel = config$parallel", source_text, fixed = TRUE))
stopifnot(grepl("ncpus = config$ncpus, verbose = FALSE", source_text, fixed = TRUE))
stopifnot(grepl('methods::slot(fit, "coef")', source_text, fixed = TRUE))
stopifnot(grepl('boot_object[["t"]]', source_text, fixed = TRUE))
stopifnot(grepl('stats::quantile(finite, probs = c(0.025, 0.975)', source_text, fixed = TRUE))
stopifnot(!grepl('stats::confint(fit', source_text, fixed = TRUE))
stopifnot(grepl('c("btergm", "network", "jsonlite")', source_text, fixed = TRUE))
stopifnot(!grepl("(^|[^[:alnum:]_])(predict|simulate|gof|mtergm|tbergm|tergm|ergm)::", source_text))
stopifnot(!grepl("(stats::)?predict[[:space:]]*\\(|simulate[[:space:]]*\\(|ergm::ergm[[:space:]]*\\(", source_text))
cat("PASS: temporal btergm formulas/options, exact consecutive panels, opaque labels, lag alignment, and no-forecast API contract (base R only).\n")
