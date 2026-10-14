#!/usr/bin/env Rscript

# Portable directed ERGM ladder.  This script intentionally consumes only an
# analysis-ready edge-list CSV supplied by --input; it never infers a raw-data
# location or a dataset-specific direction convention.
#
# Example:
# Rscript r/models/static_directed_ergm_ladder.R \
#   --input=data/processed/example/static_edges.csv \
#   --output-dir=results/models/example_static_ladder \
#   --source-col=from --target-col=to --estimate=MPLE

script_usage <- function() {
  paste(
    "Usage: Rscript r/models/static_directed_ergm_ladder.R --input=EDGES.csv --output-dir=DIR [options]",
    "",
    "Required machine-readable inputs:",
    "  --input=PATH                 CSV edge list (one directed tie per row).",
    "  --output-dir=PATH            New or explicitly overwritable output directory.",
    "",
    "Optional input contract:",
    "  --source-col=from            Name of source column in --input.",
    "  --target-col=to              Name of target column in --input.",
    "  --nodes=PATH                 Optional CSV of the full node universe, preserving isolates.",
    "  --node-col=id                Node-ID column in --nodes.",
    "  --drop-loops=TRUE            Drop self-loops (FALSE rejects them).",
    "",
    "Estimation and reproducibility:",
    "  --estimate=MPLE              MPLE (default) or MCMLE.",
    "  --degree-decay=0.5           Fixed decay for gwidegree/gwodegree.",
    "  --esp-decay=0.5              Fixed decay for directed gwesp terms.",
    "  --mcmc-burnin=10000          MCMC burn-in passed to control.ergm.",
    "  --mcmc-interval=1000         MCMC interval passed to control.ergm.",
    "  --mcmle-maxit=20             Maximum MCMLE iterations when --estimate=MCMLE.",
    "  --seed=20261013              Random seed.",
    "  --overwrite=FALSE            Refuse a non-empty output directory unless TRUE.",
    "",
    "Outputs include model_specs.csv, model_status.csv, coefficients.csv,",
    "diagnostics.txt, diagnostics.csv, model_objects.rds, and run_manifest.json.",
    sep = "\n"
  )
}

parse_cli <- function(args) {
  out <- list()
  i <- 1L
  while (i <= length(args)) {
    arg <- args[[i]]
    if (!startsWith(arg, "--")) stop("Unexpected argument: ", arg, call. = FALSE)
    item <- substring(arg, 3L)
    if (item %in% c("help", "h")) {
      out$help <- "TRUE"
      i <- i + 1L
      next
    }
    if (grepl("=", item, fixed = TRUE)) {
      pieces <- strsplit(item, "=", fixed = TRUE)[[1L]]
      key <- pieces[[1L]]
      value <- paste(pieces[-1L], collapse = "=")
    } else {
      if (i == length(args) || startsWith(args[[i + 1L]], "--")) {
        stop("Argument --", item, " requires a value.", call. = FALSE)
      }
      key <- item
      value <- args[[i + 1L]]
      i <- i + 1L
    }
    if (!nzchar(key) || !nzchar(value)) stop("Empty option or value in ", arg, call. = FALSE)
    out[[key]] <- value
    i <- i + 1L
  }
  out
}

option_value <- function(options, name, default = NULL) {
  if (!is.null(options[[name]])) options[[name]] else default
}

as_flag <- function(x, name) {
  x <- tolower(as.character(x))
  if (x %in% c("true", "t", "1", "yes", "y")) return(TRUE)
  if (x %in% c("false", "f", "0", "no", "n")) return(FALSE)
  stop("--", name, " must be TRUE or FALSE.", call. = FALSE)
}

as_positive_number <- function(x, name, integer = FALSE) {
  value <- suppressWarnings(as.numeric(x))
  if (length(value) != 1L || is.na(value) || !is.finite(value) || value <= 0 ||
      (integer && value != as.integer(value))) {
    stop("--", name, " must be a positive", if (integer) " integer." else " number.", call. = FALSE)
  }
  if (integer) as.integer(value) else value
}

json_escape <- function(x) {
  x <- gsub("\\\\", "\\\\\\\\", x)
  x <- gsub("\"", "\\\\\"", x)
  x <- gsub("\n", "\\\\n", x, fixed = TRUE)
  x
}

write_failure_manifest <- function(path, status, message, options) {
  # This minimal writer intentionally works before jsonlite is available.
  option_text <- paste(
    vapply(names(options), function(nm) {
      paste0("\"", json_escape(nm), "\":\"", json_escape(as.character(options[[nm]])), "\"")
    }, character(1L)),
    collapse = ","
  )
  lines <- c(
    "{",
    paste0("  \"status\": \"", json_escape(status), "\","),
    paste0("  \"message\": \"", json_escape(message), "\","),
    paste0("  \"options\": {", option_text, "}"),
    "}"
  )
  writeLines(lines, path, useBytes = TRUE)
}

prepare_output_dir <- function(output_dir, overwrite) {
  if (dir.exists(output_dir)) {
    entries <- list.files(output_dir, all.files = TRUE, no.. = TRUE)
    if (length(entries) > 0L && !overwrite) {
      stop("Output directory is non-empty; pass --overwrite=TRUE to reuse it: ", output_dir,
           call. = FALSE)
    }
  } else if (!dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)) {
    stop("Unable to create output directory: ", output_dir, call. = FALSE)
  }
  normalizePath(output_dir, winslash = "/", mustWork = TRUE)
}

read_node_ids <- function(nodes_path, node_col) {
  if (!file.exists(nodes_path)) stop("--nodes does not exist: ", nodes_path, call. = FALSE)
  # IDs are labels, not quantities: preserving character input avoids silently
  # changing labels such as "001" before an edge/candidate join.
  nodes <- utils::read.csv(nodes_path, stringsAsFactors = FALSE, check.names = FALSE,
                           colClasses = "character", na.strings = "NA")
  if (!(node_col %in% names(nodes))) {
    stop("Node CSV is missing --node-col '", node_col, "'.", call. = FALSE)
  }
  ids <- as.character(nodes[[node_col]])
  if (anyNA(ids) || any(!nzchar(ids))) stop("Node IDs may not be missing or empty.", call. = FALSE)
  if (anyDuplicated(ids)) stop("Node CSV contains duplicate node IDs.", call. = FALSE)
  ids
}

read_directed_edges <- function(input_path, source_col, target_col, drop_loops, node_ids = NULL) {
  if (!file.exists(input_path)) stop("--input does not exist: ", input_path, call. = FALSE)
  # Endpoint values are opaque actor IDs. Read them as character before
  # validation so leading zeros and other nonnumeric labels remain exact.
  edges <- utils::read.csv(input_path, stringsAsFactors = FALSE, check.names = FALSE,
                           colClasses = "character", na.strings = "NA")
  if (!all(c(source_col, target_col) %in% names(edges))) {
    stop("Edge CSV must contain --source-col '", source_col, "' and --target-col '", target_col, "'.",
         call. = FALSE)
  }
  edge_frame <- data.frame(
    from = as.character(edges[[source_col]]),
    to = as.character(edges[[target_col]]),
    stringsAsFactors = FALSE
  )
  if (anyNA(edge_frame$from) || anyNA(edge_frame$to) ||
      any(!nzchar(edge_frame$from)) || any(!nzchar(edge_frame$to))) {
    stop("Edge endpoints may not be missing or empty.", call. = FALSE)
  }
  loops <- edge_frame$from == edge_frame$to
  if (any(loops) && !drop_loops) stop("Self-loops found and --drop-loops=FALSE.", call. = FALSE)
  edge_frame <- edge_frame[!loops, , drop = FALSE]
  duplicate_count <- sum(duplicated(edge_frame))
  edge_frame <- unique(edge_frame)

  observed_nodes <- unique(c(edge_frame$from, edge_frame$to))
  if (is.null(node_ids)) {
    node_ids <- observed_nodes
  } else {
    missing_nodes <- setdiff(observed_nodes, node_ids)
    if (length(missing_nodes) > 0L) {
      stop("Edges reference node IDs absent from --nodes: ", paste(head(missing_nodes, 10L), collapse = ", "),
           call. = FALSE)
    }
  }
  if (length(node_ids) < 2L) stop("At least two nodes are required after applying the input contract.", call. = FALSE)
  list(
    edges = edge_frame,
    node_ids = node_ids,
    input_rows = nrow(edges),
    self_loops_dropped = sum(loops),
    duplicate_rows_dropped = duplicate_count
  )
}

static_ladder_specs <- function(degree_decay = 0.5, esp_decay = 0.5) {
  number <- function(x) format(x, scientific = FALSE, trim = TRUE)
  d <- number(degree_decay)
  e <- number(esp_decay)
  degree_terms <- paste0("gwodegree(", d, ", fixed=TRUE) + gwidegree(", d, ", fixed=TRUE)")
  base <- paste("edges + mutual +", degree_terms)
  data.frame(
    model = c("M0", "M1", "M2", "M3a", "M3b", "M3c", "M4a", "M4b", "M4c"),
    rhs = c(
      "edges",
      "edges + mutual",
      base,
      paste(base, "+ gwesp(", e, ", fixed=TRUE, type='OTP')", sep = ""),
      paste(base, "+ gwesp(", e, ", fixed=TRUE, type='ITP')", sep = ""),
      paste(base, "+ gwesp(", e, ", fixed=TRUE, type='RTP')", sep = ""),
      paste(base, "+ gwesp(", e, ", fixed=TRUE, type='OTP') + ttriple", sep = ""),
      paste(base, "+ gwesp(", e, ", fixed=TRUE, type='OTP') + ctriple", sep = ""),
      paste(base, "+ gwesp(", e, ", fixed=TRUE, type='OTP') + ttriple + ctriple", sep = "")
    ),
    description = c(
      "Density baseline.",
      "Density plus mutual directed ties.",
      "Mutuality plus fixed-decay in- and out-degree heterogeneity.",
      "M2 plus outgoing two-path (OTP) directed edgewise shared partners.",
      "M2 plus incoming two-path (ITP) directed edgewise shared partners.",
      "M2 plus reciprocated two-path (RTP) directed edgewise shared partners.",
      "M3a plus directed transitive triples.",
      "M3a plus directed cyclic triples.",
      "M3a plus directed transitive and cyclic triples."
    ),
    required_terms = c(
      "edges", "edges; mutual", "edges; mutual; gwodegree; gwidegree",
      "edges; mutual; gwodegree; gwidegree; gwesp(OTP)",
      "edges; mutual; gwodegree; gwidegree; gwesp(ITP)",
      "edges; mutual; gwodegree; gwidegree; gwesp(RTP)",
      "edges; mutual; gwodegree; gwidegree; gwesp(OTP); ttriple",
      "edges; mutual; gwodegree; gwidegree; gwesp(OTP); ctriple",
      "edges; mutual; gwodegree; gwidegree; gwesp(OTP); ttriple; ctriple"
    ),
    stringsAsFactors = FALSE
  )
}

make_network <- function(edge_info) {
  n <- length(edge_info$node_ids)
  nw <- network::network.initialize(n, directed = TRUE, loops = FALSE, multiple = FALSE)
  network::network.vertex.names(nw) <- edge_info$node_ids
  if (nrow(edge_info$edges) > 0L) {
    network::add.edges(
      nw,
      tail = match(edge_info$edges$from, edge_info$node_ids),
      head = match(edge_info$edges$to, edge_info$node_ids)
    )
  }
  nw
}

network_summary_row <- function(edge_info) {
  n <- length(edge_info$node_ids)
  adj <- matrix(FALSE, nrow = n, ncol = n)
  if (nrow(edge_info$edges) > 0L) {
    adj[cbind(match(edge_info$edges$from, edge_info$node_ids), match(edge_info$edges$to, edge_info$node_ids))] <- TRUE
  }
  reciprocal_edge_count <- sum(adj & t(adj))
  data.frame(
    nodes = n,
    directed_edges = nrow(edge_info$edges),
    possible_directed_edges = n * (n - 1L),
    density = if (n > 1L) nrow(edge_info$edges) / (n * (n - 1L)) else NA_real_,
    reciprocal_pairs = reciprocal_edge_count / 2,
    reciprocated_edge_fraction = if (nrow(edge_info$edges) > 0L) reciprocal_edge_count / nrow(edge_info$edges) else NA_real_,
    input_rows = edge_info$input_rows,
    self_loops_dropped = edge_info$self_loops_dropped,
    duplicate_rows_dropped = edge_info$duplicate_rows_dropped,
    stringsAsFactors = FALSE
  )
}

fit_one_ergm <- function(spec, nw, estimate, control) {
  formula_text <- paste("nw ~", spec$rhs)
  formula_environment <- list2env(list(nw = nw), parent = parent.frame())
  model_formula <- stats::as.formula(formula_text, env = formula_environment)
  warnings <- character()
  fit <- withCallingHandlers(
    tryCatch(
      ergm::ergm(model_formula, estimate = estimate, control = control),
      error = function(e) e
    ),
    warning = function(w) {
      warnings <<- c(warnings, conditionMessage(w))
      invokeRestart("muffleWarning")
    }
  )
  if (inherits(fit, "error")) {
    return(list(
      model = spec$model,
      formula = formula_text,
      status = "fit_failed",
      message = conditionMessage(fit),
      warnings = warnings,
      fit = NULL
    ))
  }
  list(
    model = spec$model,
    formula = formula_text,
    status = "fit_succeeded",
    message = "",
    warnings = warnings,
    fit = fit
  )
}

coefficient_rows <- function(model_id, fit) {
  estimates <- tryCatch(stats::coef(fit), error = function(e) numeric())
  if (length(estimates) == 0L) {
    return(data.frame(model = character(), term = character(), estimate = numeric(), std_error = numeric(), stringsAsFactors = FALSE))
  }
  covariance <- tryCatch(fit$covar, error = function(e) NULL)
  std_error <- rep(NA_real_, length(estimates))
  if (!is.null(covariance) && is.matrix(covariance) && nrow(covariance) == length(estimates)) {
    std_error <- sqrt(pmax(0, diag(covariance)))
  }
  data.frame(
    model = model_id,
    term = names(estimates),
    estimate = unname(as.numeric(estimates)),
    std_error = unname(as.numeric(std_error)),
    stringsAsFactors = FALSE
  )
}

capture_fit_diagnostics <- function(model_id, fit, estimate) {
  summary_lines <- tryCatch(capture.output(summary(fit)), error = function(e) paste("summary failed:", conditionMessage(e)))
  if (identical(estimate, "MCMLE")) {
    mcmc_lines <- tryCatch(
      capture.output(ergm::mcmc.diagnostics(fit)),
      error = function(e) paste("mcmc.diagnostics failed:", conditionMessage(e))
    )
    mcmc_status <- if (any(grepl("failed:", mcmc_lines, fixed = TRUE))) "failed" else "captured"
  } else {
    mcmc_lines <- "MCMC diagnostics are not applicable to MPLE estimation."
    mcmc_status <- "not_applicable_mple"
  }
  list(
    text = c(paste0("===== ", model_id, " ====="), "-- summary --", summary_lines, "-- MCMC diagnostics --", mcmc_lines, ""),
    row = data.frame(model = model_id, diagnostic = "mcmc_diagnostics", status = mcmc_status, stringsAsFactors = FALSE)
  )
}

main <- function() {
  options <- parse_cli(commandArgs(trailingOnly = TRUE))
  if (!is.null(options$help)) {
    cat(script_usage(), "\n")
    return(invisible(NULL))
  }
  required <- c("input", "output-dir")
  missing <- required[!required %in% names(options)]
  if (length(missing) > 0L) {
    cat(script_usage(), "\n", file = stderr())
    stop("Missing required options: ", paste(paste0("--", missing), collapse = ", "), call. = FALSE)
  }
  allowed <- c(required, "source-col", "target-col", "nodes", "node-col", "drop-loops", "estimate",
               "degree-decay", "esp-decay", "mcmc-burnin", "mcmc-interval", "mcmle-maxit", "seed", "overwrite")
  unknown <- setdiff(names(options), allowed)
  if (length(unknown) > 0L) stop("Unknown option(s): ", paste(paste0("--", unknown), collapse = ", "), call. = FALSE)

  overwrite <- as_flag(option_value(options, "overwrite", "FALSE"), "overwrite")
  output_dir <- prepare_output_dir(option_value(options, "output-dir"), overwrite)
  input_path <- normalizePath(option_value(options, "input"), winslash = "/", mustWork = FALSE)
  source_col <- option_value(options, "source-col", "from")
  target_col <- option_value(options, "target-col", "to")
  node_col <- option_value(options, "node-col", "id")
  nodes_path <- option_value(options, "nodes", NULL)
  drop_loops <- as_flag(option_value(options, "drop-loops", "TRUE"), "drop-loops")
  estimate <- toupper(option_value(options, "estimate", "MPLE"))
  if (!estimate %in% c("MPLE", "MCMLE")) stop("--estimate must be MPLE or MCMLE.", call. = FALSE)
  degree_decay <- as_positive_number(option_value(options, "degree-decay", "0.5"), "degree-decay")
  esp_decay <- as_positive_number(option_value(options, "esp-decay", "0.5"), "esp-decay")
  mcmc_burnin <- as_positive_number(option_value(options, "mcmc-burnin", "10000"), "mcmc-burnin", integer = TRUE)
  mcmc_interval <- as_positive_number(option_value(options, "mcmc-interval", "1000"), "mcmc-interval", integer = TRUE)
  mcmle_maxit <- as_positive_number(option_value(options, "mcmle-maxit", "20"), "mcmle-maxit", integer = TRUE)
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

  node_ids <- if (!is.null(nodes_path)) read_node_ids(normalizePath(nodes_path, winslash = "/", mustWork = FALSE), node_col) else NULL
  edge_info <- read_directed_edges(input_path, source_col, target_col, drop_loops, node_ids)
  nw <- make_network(edge_info)
  specs <- static_ladder_specs(degree_decay, esp_decay)
  utils::write.csv(specs, file.path(output_dir, "model_specs.csv"), row.names = FALSE, na = "")
  utils::write.csv(network_summary_row(edge_info), file.path(output_dir, "network_summary.csv"), row.names = FALSE, na = "")

  control <- do.call(ergm::control.ergm, list(
    MCMC.burnin = mcmc_burnin,
    MCMC.interval = mcmc_interval,
    MCMLE.maxit = mcmle_maxit
  ))
  results <- vector("list", nrow(specs))
  names(results) <- specs$model
  for (i in seq_len(nrow(specs))) {
    message("Fitting ", specs$model[[i]], ": ", specs$rhs[[i]])
    results[[i]] <- fit_one_ergm(specs[i, , drop = FALSE], nw, estimate, control)
  }

  status <- do.call(rbind, lapply(results, function(x) data.frame(
    model = x$model, formula = x$formula, status = x$status, message = x$message,
    warnings = paste(unique(x$warnings), collapse = " | "), stringsAsFactors = FALSE
  )))
  utils::write.csv(status, file.path(output_dir, "model_status.csv"), row.names = FALSE, na = "")

  succeeded <- Filter(function(x) identical(x$status, "fit_succeeded"), results)
  coefficients <- if (length(succeeded) > 0L) {
    do.call(rbind, lapply(succeeded, function(x) coefficient_rows(x$model, x$fit)))
  } else {
    data.frame(model = character(), term = character(), estimate = numeric(), std_error = numeric(), stringsAsFactors = FALSE)
  }
  utils::write.csv(coefficients, file.path(output_dir, "coefficients.csv"), row.names = FALSE, na = "")

  diagnostic_sections <- lapply(succeeded, function(x) capture_fit_diagnostics(x$model, x$fit, estimate))
  if (length(diagnostic_sections) == 0L) {
    writeLines("No model fit succeeded; see model_status.csv for visible failure details.", file.path(output_dir, "diagnostics.txt"))
    diagnostic_rows <- data.frame(model = status$model, diagnostic = "fit", status = status$status, stringsAsFactors = FALSE)
  } else {
    writeLines(unlist(lapply(diagnostic_sections, `[[`, "text")), file.path(output_dir, "diagnostics.txt"))
    diagnostic_rows <- do.call(rbind, lapply(diagnostic_sections, `[[`, "row"))
  }
  utils::write.csv(diagnostic_rows, file.path(output_dir, "diagnostics.csv"), row.names = FALSE, na = "")
  saveRDS(lapply(results, `[[`, "fit"), file.path(output_dir, "model_objects.rds"))

  manifest <- list(
    status = if (all(status$status == "fit_succeeded")) "completed" else "completed_with_model_failures",
    script = "r/models/static_directed_ergm_ladder.R",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(edge_csv = normalizePath(input_path, winslash = "/", mustWork = FALSE), source_column = source_col,
                 target_column = target_col, nodes_csv = if (is.null(nodes_path)) NULL else normalizePath(nodes_path, winslash = "/", mustWork = FALSE),
                 node_column = if (is.null(nodes_path)) NULL else node_col, drop_loops = drop_loops),
    output_dir = output_dir,
    estimation = list(estimate = estimate, seed = seed, degree_decay = degree_decay, esp_decay = esp_decay,
                      mcmc_burnin = mcmc_burnin, mcmc_interval = mcmc_interval, mcmle_maxit = mcmle_maxit),
    package_versions = lapply(package_names, function(p) as.character(utils::packageVersion(p))),
    limitations = c(
      "Models treat the supplied edge list as a binary directed cross-section; weights, time, and unobserved actors are not inferred.",
      "Directed gwesp types and ttriple/ctriple are attempted only through the installed ergm version; unsupported or non-estimable models remain visibly failed in model_status.csv.",
      "MPLE is fast but does not supply MCMLE convergence diagnostics; MCMLE may be computationally demanding or degenerate."
    )
  )
  names(manifest$package_versions) <- package_names
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), auto_unbox = TRUE, pretty = TRUE, null = "null")
  message("Static ERGM ladder complete. Output: ", output_dir)
}

if (sys.nframe() == 0L) main()
