#!/usr/bin/env Rscript

# Bounded temporal check for an analysis-ready directed panel edge list.
# The factorized models intentionally use lagged regressors only:
#   T_tt: y_ij,t (the observed tie at time t)
#   T0:   logit P(T_tt=1) = beta_0
#   T1:   T0 + beta_1 * y_ij,t-1
#   T2:   T1 + beta_2 * CN_out(i,j,t-1)
# No contemporaneous network statistic is placed on a right-hand side. This is
# a diagnostic/factorized conditional model, not a temporal ERGM simulation.
#
# Example:
# Rscript r/models/temporal_lagged_check.R \
#   --input=data/processed/example/monthly_edges.csv \
#   --output-dir=results/models/example_temporal_check \
#   --time-col=month --source-col=from --target-col=to

script_usage <- function() {
  paste(
    "Usage: Rscript r/models/temporal_lagged_check.R --input=PANEL.csv --output-dir=DIR [options]",
    "",
    "Required machine-readable inputs:",
    "  --input=PATH                 CSV with time, source, and target columns; each row is a directed tie.",
    "  --output-dir=PATH            New or explicitly overwritable output directory.",
    "",
    "Input contract and bounds:",
    "  --time-col=time              Panel/time column. Values are sorted lexically unless --time-order=numeric.",
    "  --source-col=from            Source-node column.",
    "  --target-col=to              Target-node column.",
    "  --nodes=PATH                 Optional CSV of all actors; preserves isolates throughout every panel.",
    "  --node-col=id                Actor-ID column in --nodes.",
    "  --drop-loops=TRUE            Drop self-loops (FALSE rejects them).",
    "  --time-order=lexical         lexical (default) or numeric ordering of time values.",
    "  --max-nodes=100              Hard bound; input exceeding it fails rather than being silently subset.",
    "  --max-transitions=2          Hard bound on adjacent panel transitions.",
    "  --max-dyads=50000            Hard bound on rows in the factorized design.",
    "",
    "Optional package checks (not forecasts):",
    "  --btergm=check               off, check (default), or fit. A fit is labelled bootstrap coefficients, never a forecast.",
    "  --btergm-reps=100            Positive bootstrap replications for --btergm=fit.",
    "  --tergm=check                off, check (default), or fit. fit fails visibly: temporal specification is intentionally not guessed.",
    "  --seed=20261013              Random seed.",
    "  --overwrite=FALSE            Refuse a non-empty output directory unless TRUE.",
    "",
    "Outputs include factorized_coefficients.csv, factorized_model_status.csv,",
    "feature_summary.csv, proposition6_identity.csv, package_placeholder_status.csv,",
    "and temporal_manifest.json.",
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
      if (i == length(args) || startsWith(args[[i + 1L]], "--")) stop("Argument --", item, " requires a value.", call. = FALSE)
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

as_positive_integer <- function(x, name) {
  value <- suppressWarnings(as.numeric(x))
  if (length(value) != 1L || is.na(value) || !is.finite(value) || value <= 0 || value != as.integer(value)) {
    stop("--", name, " must be a positive integer.", call. = FALSE)
  }
  as.integer(value)
}

json_escape <- function(x) {
  x <- gsub("\\\\", "\\\\\\\\", x)
  x <- gsub("\"", "\\\\\"", x)
  x <- gsub("\n", "\\\\n", x, fixed = TRUE)
  x
}

write_base_failure_manifest <- function(path, status, message, options) {
  opt <- paste(vapply(names(options), function(nm) {
    paste0("\"", json_escape(nm), "\":\"", json_escape(as.character(options[[nm]])), "\"")
  }, character(1L)), collapse = ",")
  writeLines(c(
    "{",
    paste0("  \"status\": \"", json_escape(status), "\","),
    paste0("  \"message\": \"", json_escape(message), "\","),
    paste0("  \"options\": {", opt, "}"),
    "}"
  ), path, useBytes = TRUE)
}

prepare_output_dir <- function(output_dir, overwrite) {
  if (dir.exists(output_dir)) {
    entries <- list.files(output_dir, all.files = TRUE, no.. = TRUE)
    if (length(entries) > 0L && !overwrite) {
      stop("Output directory is non-empty; pass --overwrite=TRUE to reuse it: ", output_dir, call. = FALSE)
    }
  } else if (!dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)) {
    stop("Unable to create output directory: ", output_dir, call. = FALSE)
  }
  normalizePath(output_dir, winslash = "/", mustWork = TRUE)
}

read_node_ids <- function(nodes_path, node_col) {
  if (!file.exists(nodes_path)) stop("--nodes does not exist: ", nodes_path, call. = FALSE)
  nodes <- utils::read.csv(nodes_path, stringsAsFactors = FALSE, check.names = FALSE,
                           colClasses = "character", na.strings = "NA")
  if (!(node_col %in% names(nodes))) stop("Node CSV is missing --node-col '", node_col, "'.", call. = FALSE)
  ids <- as.character(nodes[[node_col]])
  if (anyNA(ids) || any(!nzchar(ids))) stop("Node IDs may not be missing or empty.", call. = FALSE)
  if (anyDuplicated(ids)) stop("Node CSV contains duplicate node IDs.", call. = FALSE)
  ids
}

order_time_values <- function(values, time_order) {
  if (identical(time_order, "lexical")) return(sort(unique(values)))
  numeric_values <- suppressWarnings(as.numeric(values))
  if (anyNA(numeric_values)) stop("--time-order=numeric requires all time values to parse as numbers.", call. = FALSE)
  unique(values[order(numeric_values, values)])
}

read_panel_edges <- function(input_path, time_col, source_col, target_col, drop_loops, node_ids = NULL, time_order = "lexical") {
  if (!file.exists(input_path)) stop("--input does not exist: ", input_path, call. = FALSE)
  raw <- utils::read.csv(input_path, stringsAsFactors = FALSE, check.names = FALSE,
                         colClasses = "character", na.strings = "NA")
  required <- c(time_col, source_col, target_col)
  if (!all(required %in% names(raw))) {
    stop("Panel CSV must contain --time-col '", time_col, "', --source-col '", source_col,
         "', and --target-col '", target_col, "'.", call. = FALSE)
  }
  edges <- data.frame(
    time = as.character(raw[[time_col]]),
    from = as.character(raw[[source_col]]),
    to = as.character(raw[[target_col]]),
    stringsAsFactors = FALSE
  )
  if (anyNA(edges$time) || anyNA(edges$from) || anyNA(edges$to) ||
      any(!nzchar(edges$time)) || any(!nzchar(edges$from)) || any(!nzchar(edges$to))) {
    stop("Time and edge endpoints may not be missing or empty.", call. = FALSE)
  }
  loops <- edges$from == edges$to
  if (any(loops) && !drop_loops) stop("Self-loops found and --drop-loops=FALSE.", call. = FALSE)
  edges <- edges[!loops, , drop = FALSE]
  duplicate_count <- sum(duplicated(edges))
  edges <- unique(edges)
  times <- order_time_values(edges$time, time_order)
  if (length(times) < 2L) stop("At least two distinct, ordered panel times are required.", call. = FALSE)
  observed_nodes <- unique(c(edges$from, edges$to))
  if (is.null(node_ids)) {
    node_ids <- observed_nodes
  } else {
    absent <- setdiff(observed_nodes, node_ids)
    if (length(absent) > 0L) stop("Panel edges reference node IDs absent from --nodes: ", paste(head(absent, 10L), collapse = ", "), call. = FALSE)
  }
  if (length(node_ids) < 2L) stop("At least two nodes are required after applying the input contract.", call. = FALSE)
  list(edges = edges, node_ids = node_ids, times = times, input_rows = nrow(raw),
       self_loops_dropped = sum(loops), duplicate_rows_dropped = duplicate_count)
}

build_adjacency_panels <- function(panel_info) {
  n <- length(panel_info$node_ids)
  panels <- vector("list", length(panel_info$times))
  names(panels) <- panel_info$times
  for (idx in seq_along(panel_info$times)) {
    time_value <- panel_info$times[[idx]]
    panel_edges <- panel_info$edges[panel_info$edges$time == time_value, , drop = FALSE]
    adjacency <- matrix(0L, nrow = n, ncol = n,
                        dimnames = list(panel_info$node_ids, panel_info$node_ids))
    if (nrow(panel_edges) > 0L) {
      adjacency[cbind(match(panel_edges$from, panel_info$node_ids), match(panel_edges$to, panel_info$node_ids))] <- 1L
    }
    panels[[idx]] <- adjacency
  }
  panels
}

build_lagged_design <- function(panels, times) {
  n <- nrow(panels[[1L]])
  dyads <- which(row(matrix(TRUE, n, n)) != col(matrix(TRUE, n, n)), arr.ind = TRUE)
  rows <- vector("list", length(panels) - 1L)
  for (t in 2:length(panels)) {
    lag <- panels[[t - 1L]]
    current <- panels[[t]]
    # CN_out(i,j,t-1) = sum_k y_i,k,t-1 * y_j,k,t-1: shared outgoing neighbours.
    lag_cn_out <- lag %*% t(lag)
    rows[[t - 1L]] <- data.frame(
      transition = paste0(times[[t - 1L]], "->", times[[t]]),
      time_lag = times[[t - 1L]],
      time_current = times[[t]],
      from = rownames(lag)[dyads[, 1L]],
      to = colnames(lag)[dyads[, 2L]],
      y_tt = as.integer(current[dyads]),
      lag_tie = as.integer(lag[dyads]),
      lag_cn_out = as.numeric(lag_cn_out[dyads]),
      stringsAsFactors = FALSE
    )
  }
  do.call(rbind, rows)
}

factorized_model_specs <- function() {
  data.frame(
    model = c("T0", "T1", "T2"),
    formula = c("y_tt ~ 1", "y_tt ~ lag_tie", "y_tt ~ lag_tie + lag_cn_out"),
    right_hand_side = c(
      "Intercept only.",
      "Lagged tie y_ij,t-1 only.",
      "Lagged tie plus lagged shared outgoing common-neighbour count only."
    ),
    stringsAsFactors = FALSE
  )
}

fit_factorized_glm <- function(spec, design) {
  if (length(unique(design$y_tt)) < 2L) {
    return(list(status = "skipped_no_response_variation", message = "y_tt has only one value across bounded design rows.", fit = NULL))
  }
  model_formula <- stats::as.formula(spec$formula)
  warnings <- character()
  fit <- withCallingHandlers(
    tryCatch(stats::glm(model_formula, family = stats::binomial(), data = design), error = function(e) e),
    warning = function(w) {
      warnings <<- c(warnings, conditionMessage(w))
      invokeRestart("muffleWarning")
    }
  )
  if (inherits(fit, "error")) {
    return(list(status = "fit_failed", message = paste(c(conditionMessage(fit), warnings), collapse = " | "), fit = NULL))
  }
  list(status = "fit_succeeded", message = paste(unique(warnings), collapse = " | "), fit = fit)
}

coefficient_rows <- function(model_id, fit) {
  tab <- summary(fit)$coefficients
  data.frame(
    model = model_id,
    term = rownames(tab),
    estimate = unname(tab[, "Estimate"]),
    std_error = unname(tab[, "Std. Error"]),
    z_value = unname(tab[, "z value"]),
    p_value = unname(tab[, "Pr(>|z|)"]),
    stringsAsFactors = FALSE
  )
}

# Numerical form of the Proposition 6 ranking identity used in this project:
# if p_ij,t = logistic(alpha + beta * CN_ij,t-1) with beta > 0, then
# p_ij,t > p_kl,t exactly when CN_ij,t-1 > CN_kl,t-1. The check is deliberately
# separate from fitted data so it can run without statnet or an input CSV.
proposition6_lagged_cn_identity <- function(alpha = -2, beta = 0.7, tolerance = 1e-12) {
  if (!is.finite(alpha) || !is.finite(beta) || beta <= 0) stop("Proposition 6 identity requires finite alpha and beta > 0.", call. = FALSE)
  # Toy lag panel: rows are senders, columns are recipients. Nodes 1 and 2
  # share two out-neighbours; 1 and 3 share one; 4 and 5 share none.
  lag <- matrix(0L, nrow = 5L, ncol = 5L,
                dimnames = list(as.character(1:5), as.character(1:5)))
  lag[1L, c(4L, 5L)] <- 1L
  lag[2L, c(4L, 5L)] <- 1L
  lag[3L, 4L] <- 1L
  common <- lag %*% t(lag)
  candidates <- rbind(c(1L, 2L), c(1L, 3L), c(3L, 1L), c(4L, 5L))
  cn <- as.numeric(common[candidates])
  eta <- alpha + beta * cn
  probability <- stats::plogis(eta)
  recovered_eta <- stats::qlogis(probability)
  pair_cn <- outer(cn, cn, "-")
  pair_probability <- outer(probability, probability, "-")
  strictly_ranked <- pair_cn != 0
  rank_identity <- all(sign(pair_cn[strictly_ranked]) == sign(pair_probability[strictly_ranked]))
  logit_identity <- isTRUE(all.equal(recovered_eta, eta, tolerance = tolerance))
  odds_step_identity <- isTRUE(all.equal(
    (probability[cn == 2L][[1L]] / (1 - probability[cn == 2L][[1L]])) /
      (probability[cn == 1L][[1L]] / (1 - probability[cn == 1L][[1L]])),
    exp(beta), tolerance = tolerance
  ))
  table <- data.frame(
    dyad = paste0(rownames(lag)[candidates[, 1L]], "->", colnames(lag)[candidates[, 2L]]),
    lagged_common_neighbors = cn,
    linear_predictor = eta,
    probability = probability,
    stringsAsFactors = FALSE
  )
  list(pass = logit_identity && rank_identity && odds_step_identity,
       logit_identity = logit_identity, rank_identity = rank_identity,
       odds_step_identity = odds_step_identity, alpha = alpha, beta = beta, table = table)
}

write_package_placeholders <- function(output_dir, btergm_mode, tergm_mode, network_list, btergm_reps, seed) {
  rows <- list()
  fits <- list()
  if (identical(btergm_mode, "off")) {
    rows[[length(rows) + 1L]] <- data.frame(engine = "btergm", requested_mode = "off", status = "not_requested",
                                             message = "No btergm package check or fit requested.", stringsAsFactors = FALSE)
  } else if (!requireNamespace("btergm", quietly = TRUE)) {
    rows[[length(rows) + 1L]] <- data.frame(engine = "btergm", requested_mode = btergm_mode, status = "failure_missing_package",
                                             message = "Package 'btergm' is absent. Run r/bootstrap_renv.R; no coefficient was produced.", stringsAsFactors = FALSE)
  } else if (identical(btergm_mode, "check")) {
    rows[[length(rows) + 1L]] <- data.frame(engine = "btergm", requested_mode = "check", status = "available_not_fit",
                                             message = "Package and bounded panel list are available. No bootstrap coefficient was fit in check mode.", stringsAsFactors = FALSE)
  } else {
    if (!requireNamespace("network", quietly = TRUE)) {
      rows[[length(rows) + 1L]] <- data.frame(engine = "btergm", requested_mode = "fit", status = "failure_missing_package",
                                               message = "Package 'network' is required to construct btergm panel networks.", stringsAsFactors = FALSE)
    } else {
      set.seed(seed)
      btergm_fit <- tryCatch(
        btergm::btergm(network_list ~ edges + mutual, R = btergm_reps, verbose = FALSE),
        error = function(e) e
      )
      if (inherits(btergm_fit, "error")) {
        rows[[length(rows) + 1L]] <- data.frame(engine = "btergm", requested_mode = "fit", status = "fit_failed",
                                                 message = conditionMessage(btergm_fit), stringsAsFactors = FALSE)
      } else {
        fits$btergm <- btergm_fit
        rows[[length(rows) + 1L]] <- data.frame(engine = "btergm", requested_mode = "fit", status = "fit_succeeded_not_a_forecast",
                                                 message = "Bootstrap coefficients only; they are descriptive estimates, never a simulated forecast.", stringsAsFactors = FALSE)
        co <- tryCatch(stats::coef(btergm_fit), error = function(e) numeric())
        if (length(co) > 0L) {
          utils::write.csv(data.frame(term = names(co), bootstrap_coefficient = unname(co),
                                      interpretation = "descriptive bootstrap coefficient; never a simulated forecast",
                                      stringsAsFactors = FALSE),
                           file.path(output_dir, "btergm_bootstrap_coefficients_not_forecasts.csv"), row.names = FALSE, na = "")
        }
      }
    }
  }

  if (identical(tergm_mode, "off")) {
    rows[[length(rows) + 1L]] <- data.frame(engine = "tergm", requested_mode = "off", status = "not_requested",
                                             message = "No tergm package check requested.", stringsAsFactors = FALSE)
  } else if (!requireNamespace("tergm", quietly = TRUE)) {
    rows[[length(rows) + 1L]] <- data.frame(engine = "tergm", requested_mode = tergm_mode, status = "failure_missing_package",
                                             message = "Package 'tergm' is absent. Run r/bootstrap_renv.R; no temporal ERGM was fit.", stringsAsFactors = FALSE)
  } else if (identical(tergm_mode, "check")) {
    rows[[length(rows) + 1L]] <- data.frame(engine = "tergm", requested_mode = "check", status = "available_placeholder_not_fit",
                                             message = "Package is available, but this bounded driver does not guess a Form/Diss temporal specification or networkDynamic input.", stringsAsFactors = FALSE)
  } else {
    rows[[length(rows) + 1L]] <- data.frame(engine = "tergm", requested_mode = "fit", status = "failure_explicit_specification_required",
                                             message = "tergm fit deliberately not run: supply an explicit temporal formation/dissolution specification outside this lagged-only factorized check.", stringsAsFactors = FALSE)
  }
  status <- do.call(rbind, rows)
  utils::write.csv(status, file.path(output_dir, "package_placeholder_status.csv"), row.names = FALSE, na = "")
  saveRDS(fits, file.path(output_dir, "package_placeholder_objects.rds"))
  status
}

as_network_list <- function(panels) {
  if (!requireNamespace("network", quietly = TRUE)) return(NULL)
  lapply(panels, function(adjacency) {
    nw <- network::network(adjacency, directed = TRUE, matrix.type = "adjacency", loops = FALSE,
                           ignore.eval = TRUE, names.eval = "na")
    network::network.vertex.names(nw) <- rownames(adjacency)
    nw
  })
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
  allowed <- c(required, "time-col", "source-col", "target-col", "nodes", "node-col", "drop-loops", "time-order",
               "max-nodes", "max-transitions", "max-dyads", "btergm", "btergm-reps", "tergm", "seed", "overwrite")
  unknown <- setdiff(names(options), allowed)
  if (length(unknown) > 0L) stop("Unknown option(s): ", paste(paste0("--", unknown), collapse = ", "), call. = FALSE)

  overwrite <- as_flag(option_value(options, "overwrite", "FALSE"), "overwrite")
  output_dir <- prepare_output_dir(option_value(options, "output-dir"), overwrite)
  input_path <- normalizePath(option_value(options, "input"), winslash = "/", mustWork = FALSE)
  time_col <- option_value(options, "time-col", "time")
  source_col <- option_value(options, "source-col", "from")
  target_col <- option_value(options, "target-col", "to")
  node_col <- option_value(options, "node-col", "id")
  nodes_path <- option_value(options, "nodes", NULL)
  drop_loops <- as_flag(option_value(options, "drop-loops", "TRUE"), "drop-loops")
  time_order <- tolower(option_value(options, "time-order", "lexical"))
  if (!time_order %in% c("lexical", "numeric")) stop("--time-order must be lexical or numeric.", call. = FALSE)
  max_nodes <- as_positive_integer(option_value(options, "max-nodes", "100"), "max-nodes")
  max_transitions <- as_positive_integer(option_value(options, "max-transitions", "2"), "max-transitions")
  max_dyads <- as_positive_integer(option_value(options, "max-dyads", "50000"), "max-dyads")
  btergm_mode <- tolower(option_value(options, "btergm", "check"))
  tergm_mode <- tolower(option_value(options, "tergm", "check"))
  if (!btergm_mode %in% c("off", "check", "fit")) stop("--btergm must be off, check, or fit.", call. = FALSE)
  if (!tergm_mode %in% c("off", "check", "fit")) stop("--tergm must be off, check, or fit.", call. = FALSE)
  btergm_reps <- as_positive_integer(option_value(options, "btergm-reps", "100"), "btergm-reps")
  seed <- as_positive_integer(option_value(options, "seed", "20261013"), "seed")
  set.seed(seed)

  node_ids <- if (!is.null(nodes_path)) read_node_ids(normalizePath(nodes_path, winslash = "/", mustWork = FALSE), node_col) else NULL
  panel_info <- read_panel_edges(input_path, time_col, source_col, target_col, drop_loops, node_ids, time_order)
  transitions <- length(panel_info$times) - 1L
  if (length(panel_info$node_ids) > max_nodes) {
    message_text <- paste0("Input has ", length(panel_info$node_ids), " nodes, exceeding --max-nodes=", max_nodes, ". No subsetting was performed.")
    write_base_failure_manifest(file.path(output_dir, "temporal_manifest.json"), "failure_bound_nodes", message_text, options)
    stop(message_text, call. = FALSE)
  }
  if (transitions > max_transitions) {
    message_text <- paste0("Input has ", transitions, " adjacent transitions, exceeding --max-transitions=", max_transitions, ". No subsetting was performed.")
    write_base_failure_manifest(file.path(output_dir, "temporal_manifest.json"), "failure_bound_transitions", message_text, options)
    stop(message_text, call. = FALSE)
  }
  planned_dyads <- length(panel_info$node_ids) * (length(panel_info$node_ids) - 1L) * transitions
  if (planned_dyads > max_dyads) {
    message_text <- paste0("Factorized design would have ", planned_dyads, " dyad-time rows, exceeding --max-dyads=", max_dyads, ". No subsetting was performed.")
    write_base_failure_manifest(file.path(output_dir, "temporal_manifest.json"), "failure_bound_dyads", message_text, options)
    stop(message_text, call. = FALSE)
  }

  panels <- build_adjacency_panels(panel_info)
  design <- build_lagged_design(panels, panel_info$times)
  specs <- factorized_model_specs()
  utils::write.csv(specs, file.path(output_dir, "factorized_model_specs.csv"), row.names = FALSE, na = "")
  feature_summary <- data.frame(
    nodes = length(panel_info$node_ids), panels = length(panel_info$times), transitions = transitions,
    factorized_dyad_rows = nrow(design), positive_outcomes = sum(design$y_tt),
    outcome_rate = mean(design$y_tt), mean_lag_tie = mean(design$lag_tie),
    mean_lag_cn_out = mean(design$lag_cn_out), input_rows = panel_info$input_rows,
    self_loops_dropped = panel_info$self_loops_dropped, duplicate_rows_dropped = panel_info$duplicate_rows_dropped,
    stringsAsFactors = FALSE
  )
  utils::write.csv(feature_summary, file.path(output_dir, "feature_summary.csv"), row.names = FALSE, na = "")

  fit_results <- lapply(seq_len(nrow(specs)), function(i) fit_factorized_glm(specs[i, , drop = FALSE], design))
  names(fit_results) <- specs$model
  factorized_status <- do.call(rbind, lapply(seq_len(nrow(specs)), function(i) data.frame(
    model = specs$model[[i]], formula = specs$formula[[i]], status = fit_results[[i]]$status,
    message = fit_results[[i]]$message, stringsAsFactors = FALSE
  )))
  utils::write.csv(factorized_status, file.path(output_dir, "factorized_model_status.csv"), row.names = FALSE, na = "")
  coefficient_list <- lapply(seq_len(nrow(specs)), function(i) {
    fit <- fit_results[[i]]$fit
    if (is.null(fit)) return(NULL)
    coefficient_rows(specs$model[[i]], fit)
  })
  coefficient_list <- Filter(Negate(is.null), coefficient_list)
  factorized_coefficients <- if (length(coefficient_list) > 0L) do.call(rbind, coefficient_list) else data.frame(
    model = character(), term = character(), estimate = numeric(), std_error = numeric(), z_value = numeric(), p_value = numeric(), stringsAsFactors = FALSE
  )
  utils::write.csv(factorized_coefficients, file.path(output_dir, "factorized_coefficients.csv"), row.names = FALSE, na = "")
  saveRDS(lapply(fit_results, `[[`, "fit"), file.path(output_dir, "factorized_model_objects.rds"))

  proposition <- proposition6_lagged_cn_identity()
  proposition_table <- cbind(proposition$table,
                             proposition6_pass = proposition$pass,
                             logit_identity = proposition$logit_identity,
                             rank_identity = proposition$rank_identity,
                             odds_step_identity = proposition$odds_step_identity)
  utils::write.csv(proposition_table, file.path(output_dir, "proposition6_identity.csv"), row.names = FALSE, na = "")
  if (!proposition$pass) stop("Internal Proposition 6 numerical identity check failed; no interpretation should proceed.", call. = FALSE)

  network_list <- if (identical(btergm_mode, "fit")) as_network_list(panels) else NULL
  placeholder_status <- write_package_placeholders(output_dir, btergm_mode, tergm_mode, network_list, btergm_reps, seed)
  if (identical(btergm_mode, "fit") && any(placeholder_status$engine == "btergm" & placeholder_status$status == "failure_missing_package")) {
    stop("--btergm=fit requested but required package/input support is absent; see package_placeholder_status.csv.", call. = FALSE)
  }
  if (identical(tergm_mode, "fit")) {
    stop("--tergm=fit deliberately fails until an explicit temporal ERGM specification is supplied; see package_placeholder_status.csv.", call. = FALSE)
  }

  manifest <- list(
    status = "completed",
    script = "r/models/temporal_lagged_check.R",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(panel_csv = normalizePath(input_path, winslash = "/", mustWork = FALSE), time_column = time_col,
                 source_column = source_col, target_column = target_col, nodes_csv = if (is.null(nodes_path)) NULL else normalizePath(nodes_path, winslash = "/", mustWork = FALSE),
                 node_column = if (is.null(nodes_path)) NULL else node_col, time_order = time_order, drop_loops = drop_loops),
    bounds = list(max_nodes = max_nodes, max_transitions = max_transitions, max_dyads = max_dyads),
    factorization = list(
      response = "T_tt = y_ij,t",
      T0 = "logit P(y_ij,t=1) = beta_0",
      T1 = "T0 + beta_1*y_ij,t-1",
      T2 = "T1 + beta_2*CN_out(i,j,t-1)",
      common_neighbor_definition = "CN_out(i,j,t-1) = sum_k y_i,k,t-1 * y_j,k,t-1"
    ),
    package_placeholders = list(btergm_mode = btergm_mode, btergm_reps = btergm_reps, tergm_mode = tergm_mode),
    proposition6_identity_pass = proposition$pass,
    limitations = c(
      "The factorized logistic fits condition on observed lagged panels and do not represent a jointly normalized temporal ERGM or a causal effect.",
      "Without --nodes, the actor universe is the union of observed endpoints; actors absent from all supplied ties cannot be recovered.",
      "btergm bootstrap coefficients, when explicitly fitted, are labelled descriptive estimates and are never simulated forecasts.",
      "The tergm path is an intentionally visible placeholder because a defensible Form/Diss specification and dynamic-network object cannot be inferred from an edge-list CSV."
    )
  )
  if (requireNamespace("jsonlite", quietly = TRUE)) {
    jsonlite::write_json(manifest, file.path(output_dir, "temporal_manifest.json"), auto_unbox = TRUE, pretty = TRUE, null = "null")
  } else {
    write_base_failure_manifest(file.path(output_dir, "temporal_manifest.json"), "completed_jsonlite_absent",
                                "Factorized outputs completed; install jsonlite for the full manifest.", options)
  }
  message("Bounded temporal check complete. Output: ", output_dir)
}

if (sys.nframe() == 0L) main()
