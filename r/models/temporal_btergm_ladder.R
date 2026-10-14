#!/usr/bin/env Rscript

# Planned temporal ladder, estimated ONLY by btergm MPLE/temporal bootstrap.
# T1/T2/T2_minus_H are conditional score estimators only: never forecasts,
# never simulated probabilities. Temporal bootstrap is an estimator, not a
# competitor. No prediction, simulation, MCMC-MLE, or formation/dissolution path.
# API references and lag-alignment rationale: docs/TEMPORAL_BTERGM_LADDER.md.

tbe_usage <- function() {
  paste(
    "Usage: Rscript r/models/temporal_btergm_ladder.R --input=PANEL.csv --nodes=NODES.csv --output-dir=DIR [options]",
    "",
    "Required: --input=PATH (time,from,to); --nodes=PATH (id); --output-dir=PATH.",
    "Periods must be consecutive integer indices or consecutive YYYY-MM months.",
    "IDs and original time labels are preserved as character strings; all panels share nodes.csv order.",
    "",
    "  --bootstrap-reps=20          Temporal bootstrap replicates; bounded pilot default.",
    "  --degree-decay=0.5           Fixed gwodegree/gwidegree decay.",
    "  --esp-decay=0.5              Fixed gwesp OTP/OSP/ISP decay.",
    "  --models=all                 all or a unique comma-separated subset of T_tt,T0,T1,T2,T2_minus_H.",
    "  --parallel=no                no (portable default), snow, or multicore (not Windows).",
    "  --ncpus=1                    Positive integer; used only when parallel is enabled.",
    "  --seed=20261013              Nonnegative integer random seed.",
    "  --max-nodes=100              Reject larger inputs; never silently subset.",
    "  --max-transitions=2          Reject longer inputs; at least two panels required.",
    "  --max-dyads=50000            Bound on n*(n-1)*(panels-1) response dyad-time rows.",
    "  --overwrite=FALSE            Explicit permission to replace this driver's outputs.",
    "",
    "Outputs: model_specs.csv, model_status.csv, coefficients.csv, input_summary.csv,",
    "panel_summary.csv, lag_alignment.csv, diagnostics.txt, model_objects.rds, run_manifest.json.",
    "MPLE conditional score estimators only, never forecasts or simulated probabilities.",
    "Temporal bootstrap is an estimator, not a competitor; 20 reps do not support confirmatory inference.",
    sep = "\n"
  )
}

tbe_parse_cli <- function(args) {
  out <- list()
  i <- 1L
  while (i <= length(args)) {
    arg <- args[[i]]
    if (!startsWith(arg, "--")) stop("Unexpected argument: ", arg, call. = FALSE)
    item <- substring(arg, 3L)
    if (item %in% c("help", "h")) { out$help <- TRUE; i <- i + 1L; next }
    eq <- regexpr("=", item, fixed = TRUE)[[1L]]
    if (eq > 0L) {
      key <- substring(item, 1L, eq - 1L)
      value <- substring(item, eq + 1L)
    } else {
      key <- item
      if (i == length(args) || startsWith(args[[i + 1L]], "--")) {
        stop("Argument --", key, " requires a value.", call. = FALSE)
      }
      i <- i + 1L
      value <- args[[i]]
    }
    if (!nzchar(key) || !nzchar(value)) stop("Empty option or value.", call. = FALSE)
    if (key %in% names(out)) stop("Duplicate option: --", key, call. = FALSE)
    out[[key]] <- value
    i <- i + 1L
  }
  out
}

tbe_flag <- function(x, name) {
  if (tolower(x) %in% c("true", "t", "1", "yes", "y")) return(TRUE)
  if (tolower(x) %in% c("false", "f", "0", "no", "n")) return(FALSE)
  stop("--", name, " must be TRUE or FALSE.", call. = FALSE)
}

tbe_number <- function(x, name, integer = FALSE, zero = FALSE) {
  n <- suppressWarnings(as.numeric(x))
  if (length(n) != 1L || !is.finite(n) || n < 0 || (!zero && n == 0) ||
      (integer && (n != floor(n) || n > .Machine$integer.max))) {
    stop("--", name, " must be a ", if (zero) "nonnegative" else "positive",
         if (integer) " integer." else " finite number.", call. = FALSE)
  }
  if (integer) as.integer(n) else n
}

tbe_ladder_specs <- function(degree_decay = 0.5, esp_decay = 0.5) {
  number <- function(x) format(x, digits = 15L, scientific = FALSE, trim = TRUE)
  degrees <- paste0("gwodegree(", number(degree_decay), ", fixed=TRUE) + gwidegree(",
                    number(degree_decay), ", fixed=TRUE)")
  esp <- paste0("gwesp(", number(esp_decay), ", fixed=TRUE, type='",
                c("OTP", "OSP", "ISP"), "')", collapse = " + ")
  t0 <- paste("edges + mutual + memory(type='autoregression', lag=1) + delrecip(lag=1)",
              "+ edgecov(lag_oi) + edgecov(lag_oo) + edgecov(lag_ii)",
              "+ edgecov(lag_outdegree_source) + edgecov(lag_indegree_target)")
  t1 <- paste(t0, "+", degrees)
  data.frame(
    model = c("T_tt", "T0", "T1", "T2", "T2_minus_H"),
    rhs = c("edges + edgecov(lag_total_CN)", t0, t1, paste(t1, "+", esp),
            paste("edges + mutual +", degrees, "+", esp)),
    uses_temporal_terms = c(FALSE, TRUE, TRUE, TRUE, FALSE),
    uses_explicit_lagged_covariates = c(TRUE, TRUE, TRUE, TRUE, FALSE),
    estimator = "btergm MPLE with temporal bootstrap",
    interpretation = "MPLE conditional score estimator only; never forecasts; no simulated probabilities",
    bootstrap_role = "temporal bootstrap is an estimator, not a competitor",
    stringsAsFactors = FALSE
  )
}

tbe_config <- function(options) {
  defaults <- list("bootstrap-reps" = "20", "degree-decay" = "0.5", "esp-decay" = "0.5",
                   models = "all", parallel = "no", ncpus = "1", seed = "20261013",
                   "max-nodes" = "100", "max-transitions" = "2", "max-dyads" = "50000",
                   overwrite = "FALSE")
  required <- c("input", "nodes", "output-dir")
  missing <- setdiff(required, names(options))
  if (length(missing)) stop("Missing required options: ", paste(missing, collapse = ", "), call. = FALSE)
  unknown <- setdiff(names(options), c(required, names(defaults)))
  if (length(unknown)) stop("Unknown options: ", paste(unknown, collapse = ", "), call. = FALSE)
  config <- utils::modifyList(defaults, options)
  for (nm in c("bootstrap-reps", "ncpus", "max-nodes", "max-transitions", "max-dyads")) {
    config[[nm]] <- tbe_number(config[[nm]], nm, integer = TRUE)
  }
  for (nm in c("degree-decay", "esp-decay")) config[[nm]] <- tbe_number(config[[nm]], nm)
  config$seed <- tbe_number(config$seed, "seed", integer = TRUE, zero = TRUE)
  config$overwrite <- tbe_flag(config$overwrite, "overwrite")
  config$parallel <- tolower(config$parallel)
  if (!config$parallel %in% c("no", "snow", "multicore")) {
    stop("--parallel must be no, snow, or multicore.", call. = FALSE)
  }
  if (config$parallel == "multicore" && .Platform$OS.type == "windows") {
    stop("--parallel=multicore is not supported on Windows; use no or snow.", call. = FALSE)
  }
  specs <- tbe_ladder_specs(config[["degree-decay"]], config[["esp-decay"]])
  selected <- if (identical(config$models, "all")) specs$model else trimws(strsplit(config$models, ",", fixed = TRUE)[[1L]])
  if (grepl("(^|,)[[:space:]]*(,|$)", config$models) ||
      !length(selected) || any(!nzchar(selected)) || anyDuplicated(selected) ||
      length(setdiff(selected, specs$model))) {
    stop("--models must be all or a unique comma-separated subset of T_tt,T0,T1,T2,T2_minus_H.", call. = FALSE)
  }
  config$models <- selected
  config
}

tbe_read_nodes <- function(path) {
  if (!file.exists(path)) stop("Node CSV does not exist: ", path, call. = FALSE)
  nodes <- utils::read.csv(path, colClasses = "character", stringsAsFactors = FALSE,
                           check.names = FALSE, na.strings = NULL)
  if (!"id" %in% names(nodes)) stop("Node CSV requires an id column.", call. = FALSE)
  ids <- nodes$id
  if (length(ids) < 2L || anyNA(ids) || any(!nzchar(ids)) || anyDuplicated(ids)) {
    stop("Node CSV requires at least two unique, nonempty IDs.", call. = FALSE)
  }
  ids
}

tbe_order_times <- function(values) {
  labels <- unique(values)
  if (length(labels) < 2L) stop("At least two panels are required (panel count >= 2).", call. = FALSE)
  if (all(grepl("^-?[0-9]+$", labels))) {
    positions <- suppressWarnings(as.numeric(labels))
    if (any(!is.finite(positions)) || any(abs(positions) > 2^53 - 1)) {
      stop("Integer period indices must be exactly representable (absolute value <= 2^53-1).", call. = FALSE)
    }
    cadence <- "consecutive_integer_indices"
  } else if (all(grepl("^[0-9]{4}-[0-9]{2}$", labels))) {
    months <- as.integer(substring(labels, 6L, 7L))
    if (any(months < 1L | months > 12L)) stop("Invalid YYYY-MM period.", call. = FALSE)
    positions <- as.integer(substring(labels, 1L, 4L)) * 12L + months
    cadence <- "consecutive_calendar_months"
  } else {
    stop("Time labels must be integer period indices or YYYY-MM months; cadence is never guessed.", call. = FALSE)
  }
  order <- order(positions)
  positions <- positions[order]
  if (anyDuplicated(positions) || any(diff(positions) != 1)) {
    stop("Panel times must be exact consecutive periods without gaps or aliased labels; no panels were filled or skipped.", call. = FALSE)
  }
  list(times = labels[order], cadence = cadence)
}

tbe_read_panel <- function(path, node_ids) {
  if (!file.exists(path)) stop("Panel CSV does not exist: ", path, call. = FALSE)
  # Endpoints and times are labels, not quantities: keep leading zeros intact.
  raw <- utils::read.csv(path, colClasses = "character", stringsAsFactors = FALSE,
                         check.names = FALSE, na.strings = NULL)
  if (!all(c("time", "from", "to") %in% names(raw))) stop("Panel CSV requires time,from,to columns.", call. = FALSE)
  edges <- raw[, c("time", "from", "to"), drop = FALSE]
  if (anyNA(edges) || any(!nzchar(as.matrix(edges)))) stop("Panel labels may not be missing or empty.", call. = FALSE)
  if (any(edges$from == edges$to)) stop("Self-loops are not allowed; input must already be loop-free.", call. = FALSE)
  if (anyDuplicated(edges)) stop("Duplicate time,from,to rows are not allowed; input must already be binary.", call. = FALSE)
  absent <- setdiff(unique(c(edges$from, edges$to)), node_ids)
  if (length(absent)) stop("Endpoints absent from nodes.csv: ", paste(head(absent, 10L), collapse = ", "), call. = FALSE)
  timing <- tbe_order_times(edges$time)
  edges <- edges[order(match(edges$time, timing$times), match(edges$from, node_ids), match(edges$to, node_ids)), , drop = FALSE]
  rownames(edges) <- NULL
  list(edges = edges, node_ids = node_ids, times = timing$times, cadence = timing$cadence,
       input_rows = nrow(raw))
}

tbe_validate_bounds <- function(panel, config) {
  n <- length(panel$node_ids)
  transitions <- length(panel$times) - 1L
  dyads <- as.double(n) * (n - 1L) * transitions
  if (n > config[["max-nodes"]] || transitions > config[["max-transitions"]] || dyads > config[["max-dyads"]]) {
    stop("Input exceeds --max-nodes, --max-transitions, or --max-dyads; no subsetting was performed.", call. = FALSE)
  }
  invisible(dyads)
}

tbe_adjacencies <- function(panel) {
  panels <- lapply(panel$times, function(time) {
    a <- matrix(0L, length(panel$node_ids), length(panel$node_ids),
                dimnames = list(panel$node_ids, panel$node_ids))
    edges <- panel$edges[panel$edges$time == time, , drop = FALSE]
    if (nrow(edges)) a[cbind(match(edges$from, panel$node_ids), match(edges$to, panel$node_ids))] <- 1L
    a
  })
  names(panels) <- panel$times
  panels
}

tbe_lag_covariates <- function(panels) {
  if (length(panels) < 2L) stop("Lag covariates require at least two panels.", call. = FALSE)
  covnames <- c("lag_total_CN", "lag_oi", "lag_oo", "lag_ii", "lag_outdegree_source", "lag_indegree_target")
  zero <- panels[[1L]] * 0
  covariates <- setNames(lapply(covnames, function(x) rep(list(zero), length(panels))), covnames)
  for (time in 2:length(panels)) {
    lag <- panels[[time - 1L]]
    n <- nrow(lag)
    oi <- lag %*% lag
    oo <- lag %*% t(lag)
    ii <- t(lag) %*% lag
    values <- list(oi + oo + ii, oi, oo, ii,
                   matrix(rowSums(lag), nrow = n, ncol = n),
                   matrix(colSums(lag), nrow = n, ncol = n, byrow = TRUE))
    for (j in seq_along(covnames)) {
      diag(values[[j]]) <- 0
      dimnames(values[[j]]) <- dimnames(lag)
      covariates[[j]][[time]] <- values[[j]]
    }
  }
  for (j in seq_along(covariates)) names(covariates[[j]]) <- names(panels)
  covariates
}

tbe_networks <- function(panels) {
  lapply(panels, function(a) {
    nw <- network::network.initialize(nrow(a), directed = TRUE, loops = FALSE, multiple = FALSE)
    network::network.vertex.names(nw) <- rownames(a)
    arcs <- which(a != 0L, arr.ind = TRUE)
    if (nrow(arcs)) network::add.edges(nw, tail = arcs[, 1L], head = arcs[, 2L])
    nw
  })
}

tbe_formula_context <- function(spec, networks, covariates) {
  # btergm first requires full-length edgecov lists, then trims oldest elements
  # to match its memory/delrecip lists (T-1). Thus do NOT pre-trim memory models.
  # Models without built-in temporal terms are explicitly restricted to 2..T,
  # so their response panels match T0/T1/T2 and the placeholder is never fitted.
  temporal <- isTRUE(spec$uses_temporal_terms[[1L]])
  objects <- c(list(networks = if (temporal) networks else networks[-1L]),
               if (temporal) covariates else lapply(covariates, function(x) x[-1L]))
  env <- list2env(objects, parent = parent.frame())
  stats::as.formula(paste("networks ~", spec$rhs[[1L]]), env = env)
}

tbe_empty_coefficients <- function() {
  data.frame(model = character(), term = character(), estimate = numeric(), bootstrap_std_error = numeric(),
             ci_lower = numeric(), ci_upper = numeric(), ci_level = numeric(), ci_method = character(),
             ci_status = character(), ci_message = character(), bootstrap_reps_requested = integer(),
             bootstrap_reps_finite = integer(), interpretation = character(), stringsAsFactors = FALSE)
}

tbe_extract_coefficients <- function(model, fit, reps) {
  co <- stats::coef(fit)
  if (!length(co) || is.null(names(co))) stop("Fit supplied no named coefficients.", call. = FALSE)
  samples <- tryCatch(methods::slot(fit, "boot")$t, error = function(e) NULL)
  se <- rep(NA_real_, length(co))
  finite_reps <- rep(NA_integer_, length(co))
  if (is.matrix(samples) && ncol(samples) == length(co)) {
    for (i in seq_along(co)) {
      finite <- samples[is.finite(samples[, i]), i]
      finite_reps[[i]] <- length(finite)
      if (length(finite) >= 2L) se[[i]] <- stats::sd(finite)
    }
  }
  warnings <- character()
  ci <- withCallingHandlers(
    tryCatch(stats::confint(fit, level = 0.95, type = "perc", invlogit = FALSE), error = function(e) e),
    warning = function(w) { warnings <<- c(warnings, conditionMessage(w)); invokeRestart("muffleWarning") }
  )
  lower <- upper <- rep(NA_real_, length(co))
  if (inherits(ci, "error")) {
    ci_message <- conditionMessage(ci)
  } else if (is.matrix(ci) && all(c("2.5%", "97.5%") %in% colnames(ci)) && !is.null(rownames(ci))) {
    idx <- match(names(co), rownames(ci))
    lower <- as.numeric(ci[idx, "2.5%"])
    upper <- as.numeric(ci[idx, "97.5%"])
    ci_message <- ""
  } else {
    ci_message <- "confint returned an unsupported shape; no interval was substituted."
  }
  extracted <- is.finite(lower) & is.finite(upper)
  data.frame(model = model, term = names(co), estimate = unname(as.numeric(co)),
             bootstrap_std_error = se, ci_lower = lower, ci_upper = upper, ci_level = 0.95,
             ci_method = "btergm percentile bootstrap (confint type=perc)",
             ci_status = ifelse(extracted, "extracted", "not_extractable"),
             ci_message = paste(c(ci_message, unique(warnings)), collapse = " | "),
             bootstrap_reps_requested = reps, bootstrap_reps_finite = finite_reps,
             interpretation = "MPLE conditional score estimator only; never forecasts; no simulated probabilities",
             stringsAsFactors = FALSE)
}

tbe_fit_one <- function(spec, networks, covariates, config) {
  formula <- tbe_formula_context(spec, networks, covariates)
  warnings <- character()
  started <- proc.time()[["elapsed"]]
  set.seed(config$seed)
  fit <- withCallingHandlers(
    tryCatch(btergm::btergm(formula, R = config[["bootstrap-reps"]], parallel = config$parallel,
                           ncpus = config$ncpus, verbose = FALSE), error = function(e) e),
    warning = function(w) { warnings <<- c(warnings, conditionMessage(w)); invokeRestart("muffleWarning") }
  )
  status <- "fit_succeeded"
  message <- ""
  coefficients <- tbe_empty_coefficients()
  if (inherits(fit, "error")) {
    status <- "fit_failed"
    message <- conditionMessage(fit)
    fit <- NULL
  } else {
    extracted <- tryCatch(tbe_extract_coefficients(spec$model[[1L]], fit, config[["bootstrap-reps"]]), error = function(e) e)
    if (inherits(extracted, "error")) {
      status <- "coefficient_extraction_failed"
      message <- conditionMessage(extracted)
    } else {
      coefficients <- extracted
      if (any(!is.finite(coefficients$estimate))) {
        status <- "fit_nonfinite_coefficients"
        message <- "Nonfinite MPLE coefficients; inspect numerical identification and separation."
      }
    }
  }
  row <- data.frame(model = spec$model[[1L]], formula = paste("networks ~", spec$rhs[[1L]]),
                    status = status, message = message, warnings = paste(unique(warnings), collapse = " | "),
                    response_panels = length(networks) - 1L, bootstrap_reps = config[["bootstrap-reps"]],
                    elapsed_seconds = proc.time()[["elapsed"]] - started,
                    interpretation = spec$interpretation[[1L]], stringsAsFactors = FALSE)
  list(status = row, coefficients = coefficients, fit = fit)
}

tbe_json_string <- function(x) {
  # Base-R JSON string encoding also works if jsonlite itself is missing.
  escaped <- vapply(utf8ToInt(enc2utf8(as.character(x))), function(code) {
    if (code == 34L) return('\\"')
    if (code == 92L) return("\\\\")
    if (code < 32L) return(sprintf("\\u%04x", code))
    intToUtf8(code)
  }, character(1L))
  paste0('"', paste0(escaped, collapse = ""), '"')
}

tbe_failure_manifest <- function(path, status, message, options, missing_packages = character()) {
  option_text <- paste(vapply(names(options), function(nm) {
    paste0(tbe_json_string(nm), ":", tbe_json_string(paste(options[[nm]], collapse = ",")))
  }, character(1L)), collapse = ",")
  packages <- paste(vapply(missing_packages, tbe_json_string, character(1L)), collapse = ",")
  writeLines(c("{", paste0('  "status": ', tbe_json_string(status), ","),
               paste0('  "message": ', tbe_json_string(message), ","),
               '  "script": "r/models/temporal_btergm_ladder.R",',
               '  "estimator": "btergm MPLE with temporal bootstrap; estimator, not competitor",',
               '  "forecasts": false, "simulated_probabilities": false,',
               paste0('  "missing_packages": [', packages, "],"),
               paste0('  "options": {', option_text, "}"), "}"), path, useBytes = TRUE)
}

tbe_output_dir <- function(path, overwrite) {
  if (dir.exists(path)) {
    if (length(list.files(path, all.files = TRUE, no.. = TRUE)) && !overwrite) {
      stop("Output directory is non-empty; pass --overwrite=TRUE to reuse it: ", path, call. = FALSE)
    }
  } else if (!dir.create(path, recursive = TRUE, showWarnings = FALSE)) {
    stop("Unable to create output directory: ", path, call. = FALSE)
  }
  path <- normalizePath(path, winslash = "/", mustWork = TRUE)
  # Remove only artifacts owned by this driver, preventing stale fits on reruns.
  if (overwrite) unlink(file.path(path, c("model_specs.csv", "model_status.csv", "coefficients.csv",
                                        "input_summary.csv", "panel_summary.csv", "lag_alignment.csv",
                                        "diagnostics.txt", "model_objects.rds", "run_manifest.json")))
  path
}

tbe_run <- function(config, output_dir) {
  input_path <- normalizePath(config$input, winslash = "/", mustWork = FALSE)
  nodes_path <- normalizePath(config$nodes, winslash = "/", mustWork = FALSE)
  specs <- tbe_ladder_specs(config[["degree-decay"]], config[["esp-decay"]])
  specs <- specs[match(config$models, specs$model), , drop = FALSE]
  write_csv <- function(x, name) utils::write.csv(x, file.path(output_dir, name), row.names = FALSE, na = "")
  write_csv(specs, "model_specs.csv")
  write_csv(tbe_empty_coefficients(), "coefficients.csv")
  write_csv(data.frame(model = specs$model, formula = paste("networks ~", specs$rhs),
                       status = "not_started", message = "", warnings = "", stringsAsFactors = FALSE), "model_status.csv")

  panel <- tbe_read_panel(input_path, tbe_read_nodes(nodes_path))
  dyads <- tbe_validate_bounds(panel, config)
  adj <- tbe_adjacencies(panel)
  input_summary <- data.frame(nodes = length(panel$node_ids), panels = length(panel$times),
                              transitions = length(panel$times) - 1L, response_dyad_time_rows = dyads,
                              input_rows = panel$input_rows, cadence = panel$cadence,
                              first_time = panel$times[[1L]], last_time = tail(panel$times, 1L),
                              duplicate_rows_dropped = 0L, self_loops_dropped = 0L, stringsAsFactors = FALSE)
  write_csv(input_summary, "input_summary.csv")
  write_csv(data.frame(time = panel$times, nodes = length(panel$node_ids),
                       directed_edges = vapply(adj, sum, numeric(1L)),
                       role = c("history_only", rep("response_and_history", length(adj) - 1L)),
                       stringsAsFactors = FALSE), "panel_summary.csv")
  alignment <- data.frame(response_time = panel$times[-1L], lag_time = head(panel$times, -1L),
                          lag = 1L, stringsAsFactors = FALSE)
  write_csv(alignment, "lag_alignment.csv")

  packages <- c("btergm", "network", "jsonlite")
  missing <- packages[!vapply(packages, requireNamespace, logical(1L), quietly = TRUE)]
  if (length(missing)) {
    message <- paste("Missing required R package(s):", paste(missing, collapse = ", "), ". Run Rscript r/bootstrap_renv.R first.")
    write_csv(data.frame(model = specs$model, formula = paste("networks ~", specs$rhs),
                         status = "failure_missing_packages", message = message, warnings = "", stringsAsFactors = FALSE), "model_status.csv")
    tbe_failure_manifest(file.path(output_dir, "run_manifest.json"), "failure_missing_packages", message, config, missing)
    stop(structure(list(message = message, call = NULL), class = c("tbe_missing_packages", "error", "condition")))
  }

  networks <- tbe_networks(adj)
  covariates <- tbe_lag_covariates(adj)
  results <- list()
  status <- data.frame(model = specs$model, formula = paste("networks ~", specs$rhs),
                       status = "not_started", message = "", warnings = "",
                       response_panels = length(networks) - 1L, bootstrap_reps = config[["bootstrap-reps"]],
                       elapsed_seconds = NA_real_, interpretation = specs$interpretation, stringsAsFactors = FALSE)
  write_csv(status, "model_status.csv")
  for (i in seq_len(nrow(specs))) {
    message("Fitting ", specs$model[[i]], " by btergm MPLE/bootstrap only.")
    results[[specs$model[[i]]]] <- tbe_fit_one(specs[i, , drop = FALSE], networks, covariates, config)
    status[i, ] <- results[[specs$model[[i]]]]$status
    write_csv(status, "model_status.csv")
    write_csv(do.call(rbind, lapply(results, `[[`, "coefficients")), "coefficients.csv")
  }
  saveRDS(lapply(results, `[[`, "fit"), file.path(output_dir, "model_objects.rds"))
  diagnostics <- unlist(lapply(names(results), function(model) {
    x <- results[[model]]
    c(paste0("===== ", model, " ====="), paste("Status:", x$status$status),
      paste("Message:", x$status$message), paste("Warnings:", x$status$warnings),
      if (!is.null(x$fit)) tryCatch(capture.output(summary(x$fit)), error = function(e) paste("Summary failed:", conditionMessage(e))),
      paste("Interval extraction:", paste(unique(x$coefficients$ci_status), collapse = ", ")),
      paste(unique(x$coefficients$ci_message), collapse = " | "), "")
  }))
  writeLines(c("MPLE conditional score estimators only; never forecasts; no simulated probabilities.",
               "Temporal bootstrap is an estimator, not a competitor. No MCMC diagnostics apply.", diagnostics),
             file.path(output_dir, "diagnostics.txt"))
  manifest <- list(
    status = if (all(status$status == "fit_succeeded")) "completed" else if (!any(status$status == "fit_succeeded")) "failure_all_models" else "completed_with_model_failures",
    script = "r/models/temporal_btergm_ladder.R", generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(panel_csv = input_path, nodes_csv = nodes_path, columns = c("time", "from", "to"), node_column = "id",
                 panel_md5 = unname(tools::md5sum(input_path)), nodes_md5 = unname(tools::md5sum(nodes_path)),
                 node_ids_in_order = panel$node_ids, times_in_order = panel$times, cadence = panel$cadence,
                 exact_consecutive_periods = TRUE),
    output_dir = output_dir, input_summary = input_summary, selected_models = config$models,
    estimation = list(engine = "btergm", method = "MPLE with temporal bootstrap", bootstrap_role = "estimator, not a competitor",
                      bootstrap_reps = config[["bootstrap-reps"]], degree_decay = config[["degree-decay"]],
                      esp_decay = config[["esp-decay"]], fixed_decays = TRUE, parallel = config$parallel, ncpus = config$ncpus,
                      seed = config$seed, seed_reset_per_model = TRUE, interval_level = 0.95, interval_type = "perc"),
    interpretation = list(T1 = "MPLE conditional score estimator only", T2 = "MPLE conditional score estimator only",
                          T2_minus_H = "MPLE conditional score estimator only", forecasts = FALSE, simulated_probabilities = FALSE),
    bounds = config[c("max-nodes", "max-transitions", "max-dyads")],
    lag_alignment = list(response_times = panel$times[-1L], lag_times = head(panel$times, -1L),
                         temporal_models = "Full lists; btergm memory/delrecip drop the first response and explicit-covariate placeholder.",
                         other_models = "Explicitly trimmed to response times 2..T; first placeholder never fitted."),
    lag_covariate_definitions = list(lag_oi = "A[t-1] %*% A[t-1]", lag_oo = "A[t-1] %*% t(A[t-1])",
                                    lag_ii = "t(A[t-1]) %*% A[t-1]", lag_total_CN = "lag_oi + lag_oo + lag_ii",
                                    lag_outdegree_source = "rowSums(A[t-1])[i] for dyad i->j",
                                    lag_indegree_target = "colSums(A[t-1])[j] for dyad i->j"),
    package_versions = setNames(lapply(packages, function(p) as.character(utils::packageVersion(p))), packages),
    model_status = status,
    limitations = c("Bounded pilot only: 20 bootstrap replicates and few response panels are not adequate for confirmatory uncertainty estimates.",
                    "T1/T2/T2_minus_H contain contemporaneous dependence and are MPLE conditional score estimators only, never forecasts or simulated probabilities.",
                    "Temporal bootstrap is the estimator and uncertainty procedure, not a prediction competitor.",
                    "Absent ties are zeros only within the supplied complete node universe and listed periods; completely empty panels cannot be represented by this edge-list contract, and gaps are rejected.",
                    "Unsupported terms, separation, collinearity, and non-extractable intervals remain visible; no statistic or estimator is substituted.")
  )
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), pretty = TRUE, auto_unbox = TRUE, na = "null", null = "null")
  message("Temporal btergm ladder complete: ", output_dir)
  if (!any(status$status == "fit_succeeded")) stop("No model produced a finite, extractable MPLE coefficient set; inspect model_status.csv.", call. = FALSE)
  invisible(manifest)
}

tbe_main <- function(args = commandArgs(trailingOnly = TRUE)) {
  options <- tbe_parse_cli(args)
  if (isTRUE(options$help)) { cat(tbe_usage(), "\n"); return(invisible(NULL)) }
  # Never clobber an existing output merely to report an invalid CLI.
  if (is.null(options[["output-dir"]])) stop(tbe_usage(), call. = FALSE)
  overwrite <- tbe_flag(if (is.null(options$overwrite)) "FALSE" else options$overwrite, "overwrite")
  output_dir <- tbe_output_dir(options[["output-dir"]], overwrite)
  tryCatch({
    config <- tbe_config(options)
    tbe_run(config, output_dir)
  }, error = function(e) {
    # Keep richer package/all-model failure manifests already written by tbe_run.
    if (!file.exists(file.path(output_dir, "run_manifest.json"))) {
      status_path <- file.path(output_dir, "model_status.csv")
      if (file.exists(status_path)) {
        rows <- utils::read.csv(status_path, colClasses = "character", check.names = FALSE,
                                stringsAsFactors = FALSE, na.strings = NULL)
        pending <- rows$status == "not_started"
        rows$status[pending] <- "failure_validation_or_runtime"
        rows$message[pending] <- conditionMessage(e)
        utils::write.csv(rows, status_path, row.names = FALSE, na = "")
      }
      tbe_failure_manifest(file.path(output_dir, "run_manifest.json"), "failure_validation_or_runtime", conditionMessage(e), options)
    }
    stop(e)
  })
}

if (sys.nframe() == 0L) tbe_main()
