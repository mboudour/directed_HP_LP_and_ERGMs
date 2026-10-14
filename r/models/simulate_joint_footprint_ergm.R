#!/usr/bin/env Rscript

# Conditional joint-footprint ERGM simulation for the plan's L3-F score.
#
# Each candidate's unobserved footprint dyads are marked missing in an otherwise
# fully observed split-specific network. Statnet's observed constraint therefore
# fixes every other dyad and samples only that candidate's unknown footprint
# dyads. This is a graph-footprint calculation, never a probability that a
# native email event occurred.

joint_usage <- function() {
  paste(
    "Usage: Rscript r/models/simulate_joint_footprint_ergm.R --input-dir=DIR --output-dir=DIR [options]",
    "",
    "Required input contract created by scripts/39_export_native_event_ergm_inputs.py:",
    "  DIR/nodes.csv",
    "  DIR/splits/<split>/train_edges.csv",
    "  DIR/splits/<split>/candidate_footprints.csv",
    "",
    "Bounded pilot options:",
    "  --models=M1,M4                    MCMLE specifications; M1 is the factorization check.",
    "  --split=all                       One exact split ID, or all available splits.",
    "  --max-candidates-per-label=5       Maximum deterministic sample per panel and label.",
    "  --max-unobserved-dyads=2           Admit only candidates with at most this many unknown arcs.",
    "  --nsim=500                         Conditional completions per simulated candidate.",
    "  --mcmc-burnin=1000                 Conditional-simulation MCMC burn-in.",
    "  --mcmc-interval=100                Conditional-simulation MCMC interval.",
    "  --fit-mcmc-burnin=5000             MCMLE fit burn-in (not conditional simulation burn-in).",
    "  --fit-mcmc-interval=500            MCMLE fit interval.",
    "  --fit-mcmc-samplesize=512          MCMLE fit sample size per iteration.",
    "  --mcmle-maxit=10                   Maximum MCMLE iterations.",
    "  --seed=20261013                    Reproducibility seed.",
    "  --overwrite=FALSE                  Refuse a nonempty output directory unless TRUE.",
    "",
    "Outputs: candidate_simulation_scores.csv, selected_candidates.csv, model_status.csv,",
    "split_status.csv, diagnostics/, fitted_models/, summary.md, and run_manifest.json.",
    "",
    "This is a bounded dependence/feasibility pilot. It deliberately does not emit",
    "ranking metrics: candidate sampling and low-probability Monte Carlo truncation",
    "are not a final performance evaluation.",
    sep = "\n"
  )
}

joint_locate_driver <- function(filename) {
  command_file <- commandArgs(trailingOnly = FALSE)
  command_file <- sub("^--file=", "", command_file[startsWith(command_file, "--file=")])
  source_files <- unlist(lapply(sys.frames(), function(frame) {
    if (exists("ofile", envir = frame, inherits = FALSE)) {
      as.character(get("ofile", envir = frame, inherits = FALSE))
    } else {
      character()
    }
  }), use.names = FALSE)
  candidate_dirs <- unique(c(
    dirname(c(command_file, source_files)),
    file.path(getwd(), "r", "models"),
    file.path(getwd(), "..", "models"),
    file.path(getwd(), "..", "r", "models")
  ))
  candidates <- file.path(candidate_dirs, filename)
  found <- candidates[file.exists(candidates)]
  if (length(found) == 0L) stop("Cannot locate sibling driver ", filename, ".", call. = FALSE)
  normalizePath(found[[1L]], winslash = "/", mustWork = TRUE)
}

# This imports strict CSV readers, static model specifications, fitting helpers,
# and native-event split/footprint parsing. All are pure definitions while this
# file is sourced for its smoke tests.
source(joint_locate_driver("score_native_event_footprints.R"))

joint_fit_mcmle <- function(spec, nw, control) {
  # `MCMLE` names the estimation algorithm, but `ergm()` selects it with
  # `estimate = "MLE"`. Disabling bridge likelihood calculation is essential:
  # L3-F requires a fitted parameter vector and conditional samples, not AIC,
  # BIC, or a normalizing-constant estimate. Bridge sampling is otherwise an
  # avoidable, expensive post-fit calculation.
  formula_text <- paste("nw ~", spec$rhs)
  formula_environment <- list2env(list(nw = nw), parent = parent.frame())
  model_formula <- stats::as.formula(formula_text, env = formula_environment)
  warnings <- character()
  fit <- withCallingHandlers(
    tryCatch(
      ergm::ergm(
        model_formula,
        estimate = "MLE",
        control = control,
        eval.loglik = FALSE
      ),
      error = function(error) error
    ),
    warning = function(warning) {
      warnings <<- c(warnings, conditionMessage(warning))
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

joint_empty_scores <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), panel = character(),
    candidate_id = character(), label = integer(), tail_arity = integer(), head_arity = integer(),
    footprint_size = integer(), observed_footprint_arcs = integer(), unobserved_footprint_arcs = integer(),
    model = character(), status = character(), simulation_draws = integer(), L1 = numeric(),
    L1g = numeric(), L2 = numeric(), log_L2 = numeric(), L3_F = numeric(), L3_F_mcse = numeric(),
    L3_F_zero_upper95 = numeric(), delta_dep = numeric(), delta_dep_status = character(),
    factorization_gap = numeric(), message = character(), stringsAsFactors = FALSE
  )
}

joint_empty_model_status <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), model = character(),
    formula = character(), status = character(), message = character(), warnings = character(),
    selected_candidates = integer(), candidates_requiring_simulation = integer(),
    candidates_scored = integer(), diagnostics_file = character(), fitted_model_file = character(),
    stringsAsFactors = FALSE
  )
}

joint_empty_split_status <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), status = character(),
    message = character(), nodes = integer(), training_edges = integer(), candidate_footprints = integer(),
    candidates_eligible = integer(), candidates_selected = integer(), stringsAsFactors = FALSE
  )
}

joint_candidate_table <- function(footprints, observed_edges) {
  observed_keys <- paste(observed_edges$from, observed_edges$to, sep = "\r")
  candidate_key <- paste(footprints$panel, footprints$candidate_id, sep = "\r")
  groups <- split(seq_len(nrow(footprints)), candidate_key)
  rows <- lapply(groups, function(indices) {
    group <- footprints[indices, , drop = FALSE]
    if (nrow(group) != group$footprint_size[[1L]]) {
      stop("Candidate footprint row count differs from its declared footprint size.", call. = FALSE)
    }
    dyad_keys <- paste(group$candidate_tail, group$candidate_head, sep = "\r")
    observed <- dyad_keys %in% observed_keys
    data.frame(
      panel = group$panel[[1L]],
      candidate_id = group$candidate_id[[1L]],
      label = group$label[[1L]],
      tail_nodes_json = group$tail_nodes_json[[1L]],
      head_nodes_json = group$head_nodes_json[[1L]],
      tail_arity = group$tail_arity[[1L]],
      head_arity = group$head_arity[[1L]],
      footprint_size = group$footprint_size[[1L]],
      observed_footprint_arcs = sum(observed),
      unobserved_footprint_arcs = sum(!observed),
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

joint_select_candidates <- function(candidates, max_unknown, max_per_label, seed) {
  if (max_unknown < 0L || max_per_label < 1L) stop("Invalid candidate-selection bounds.", call. = FALSE)
  eligible <- candidates[candidates$unobserved_footprint_arcs <= max_unknown, , drop = FALSE]
  if (nrow(eligible) == 0L) return(eligible)
  group_id <- paste(eligible$panel, eligible$label, sep = "\r")
  groups <- split(seq_len(nrow(eligible)), group_id)
  set.seed(seed)
  chosen <- unlist(lapply(groups, function(indices) {
    if (length(indices) <= max_per_label) return(indices)
    sample(indices, size = max_per_label, replace = FALSE)
  }), use.names = FALSE)
  selected <- eligible[sort(chosen), , drop = FALSE]
  selected[order(selected$panel, selected$label, selected$candidate_id), , drop = FALSE]
}

joint_candidate_dyads <- function(footprints, candidate) {
  rows <- footprints[
    footprints$panel == candidate$panel & footprints$candidate_id == candidate$candidate_id,
    c("candidate_tail", "candidate_head"),
    drop = FALSE
  ]
  if (nrow(rows) != candidate$footprint_size) {
    stop("Candidate footprint rows are missing or duplicated.", call. = FALSE)
  }
  rows[order(rows$candidate_tail, rows$candidate_head), , drop = FALSE]
}

joint_mark_missing <- function(nw, unknown_dyads, node_ids) {
  basis <- nw
  if (nrow(unknown_dyads) == 0L) return(basis)
  tails <- match(unknown_dyads$candidate_tail, node_ids)
  heads <- match(unknown_dyads$candidate_head, node_ids)
  if (anyNA(tails) || anyNA(heads)) stop("Unknown footprint dyad references absent node.", call. = FALSE)
  for (index in seq_len(nrow(unknown_dyads))) {
    basis[tails[[index]], heads[[index]], add.edges = TRUE] <- NA
  }
  if (network::network.naedgecount(basis) != nrow(unknown_dyads)) {
    stop("Candidate missing-dyad contract was not materialized exactly.", call. = FALSE)
  }
  basis
}

joint_network_list <- function(simulations) {
  if (inherits(simulations, "network")) return(list(simulations))
  result <- as.list(simulations)
  if (!all(vapply(result, inherits, logical(1L), what = "network"))) {
    stop("Conditional simulation did not return network objects.", call. = FALSE)
  }
  result
}

joint_simulation_scores <- function(fit, nw, candidate, footprint_dyads, observed_edges, node_ids,
                                    nsim, mcmc_burnin, mcmc_interval, seed) {
  observed_keys <- paste(observed_edges$from, observed_edges$to, sep = "\r")
  footprint_keys <- paste(footprint_dyads$candidate_tail, footprint_dyads$candidate_head, sep = "\r")
  observed <- footprint_keys %in% observed_keys
  unknown_dyads <- footprint_dyads[!observed, , drop = FALSE]
  known_count <- sum(observed)
  unknown_count <- nrow(unknown_dyads)
  if (unknown_count == 0L) {
    return(list(
      status = "fixed_complete_footprint", simulation_draws = 0L, L1 = 1, L1g = 1, L2 = 1,
      log_L2 = 0, L3_F = 1, L3_F_mcse = 0, L3_F_zero_upper95 = NA_real_, delta_dep = 0,
      delta_dep_status = "exact_fixed_observation", factorization_gap = 0, message = ""
    ))
  }
  basis <- joint_mark_missing(nw, unknown_dyads, node_ids)
  simulation <- tryCatch(
    withCallingHandlers(
      stats::simulate(
        fit,
        nsim = nsim,
        seed = seed,
        basis = basis,
        constraints = ~observed,
        output = "network",
        sequential = TRUE,
        control = ergm::control.simulate.ergm(
          MCMC.burnin = mcmc_burnin,
          MCMC.interval = mcmc_interval
        )
      ),
      warning = function(warning) invokeRestart("muffleWarning")
    ),
    error = function(error) error
  )
  if (inherits(simulation, "error")) {
    return(list(
      status = "simulation_failed", simulation_draws = 0L, L1 = NA_real_, L1g = NA_real_,
      L2 = NA_real_, log_L2 = NA_real_, L3_F = NA_real_, L3_F_mcse = NA_real_,
      L3_F_zero_upper95 = NA_real_, delta_dep = NA_real_, delta_dep_status = "not_estimable",
      factorization_gap = NA_real_, message = conditionMessage(simulation)
    ))
  }
  simulations <- tryCatch(joint_network_list(simulation), error = function(error) error)
  if (inherits(simulations, "error")) {
    return(list(
      status = "simulation_failed", simulation_draws = 0L, L1 = NA_real_, L1g = NA_real_,
      L2 = NA_real_, log_L2 = NA_real_, L3_F = NA_real_, L3_F_mcse = NA_real_,
      L3_F_zero_upper95 = NA_real_, delta_dep = NA_real_, delta_dep_status = "not_estimable",
      factorization_gap = NA_real_, message = conditionMessage(simulations)
    ))
  }
  tails <- match(unknown_dyads$candidate_tail, node_ids)
  heads <- match(unknown_dyads$candidate_head, node_ids)
  states <- vapply(simulations, function(simulated_network) {
    vapply(seq_along(tails), function(index) {
      isTRUE(network::is.adjacent(simulated_network, tails[[index]], heads[[index]]))
    }, logical(1L))
  }, logical(length(tails)))
  if (is.null(dim(states))) states <- matrix(states, nrow = length(tails))
  marginal <- rowMeans(states)
  footprint_complete <- colSums(states) == length(tails)
  l3_f <- mean(footprint_complete)
  l3_mcse <- sqrt(l3_f * (1 - l3_f) / length(footprint_complete))
  log_l2 <- sum(log(marginal))
  l2 <- if (is.finite(log_l2) && log_l2 >= log(.Machine$double.xmin)) exp(log_l2) else 0
  l1 <- (known_count + sum(marginal)) / candidate$footprint_size
  l1g <- exp(sum(log(marginal)) / candidate$footprint_size)
  estimable_delta <- l3_f > 0 && l2 > 0 && is.finite(log_l2)
  list(
    status = "simulated", simulation_draws = as.integer(length(footprint_complete)), L1 = l1,
    L1g = l1g, L2 = l2, log_L2 = log_l2, L3_F = l3_f, L3_F_mcse = l3_mcse,
    L3_F_zero_upper95 = if (l3_f == 0) 3 / length(footprint_complete) else NA_real_,
    delta_dep = if (estimable_delta) log(l3_f) - log_l2 else NA_real_,
    delta_dep_status = if (estimable_delta) "estimated" else "not_estimable_zero_monte_carlo_score",
    factorization_gap = l3_f - l2,
    message = ""
  )
}

joint_score_row <- function(split, identity, candidate, model, outcome) {
  data.frame(
    split = split, mechanism = identity$mechanism, replicate = identity$replicate,
    panel = candidate$panel, candidate_id = candidate$candidate_id, label = candidate$label,
    tail_arity = candidate$tail_arity, head_arity = candidate$head_arity,
    footprint_size = candidate$footprint_size,
    observed_footprint_arcs = candidate$observed_footprint_arcs,
    unobserved_footprint_arcs = candidate$unobserved_footprint_arcs,
    model = model, status = outcome$status, simulation_draws = outcome$simulation_draws,
    L1 = outcome$L1, L1g = outcome$L1g, L2 = outcome$L2, log_L2 = outcome$log_L2,
    L3_F = outcome$L3_F, L3_F_mcse = outcome$L3_F_mcse,
    L3_F_zero_upper95 = outcome$L3_F_zero_upper95, delta_dep = outcome$delta_dep,
    delta_dep_status = outcome$delta_dep_status, factorization_gap = outcome$factorization_gap,
    message = outcome$message, stringsAsFactors = FALSE
  )
}

joint_write_summary <- function(path, dataset_id, model_status, split_status, scores, options) {
  completed_models <- model_status[model_status$status == "scored", , drop = FALSE]
  simulated <- scores[scores$status == "simulated", , drop = FALSE]
  zero_scores <- simulated[simulated$delta_dep_status != "estimated", , drop = FALSE]
  lines <- c(
    "# Conditional joint ERGM footprint-simulation pilot",
    "",
    paste0("- Dataset/input bundle: `", dataset_id, "`"),
    "- Model fits are split-specific MCMLE fits; candidate simulations condition on every observed split dyad.",
    "- A candidate arc already present because another event type induced it remains fixed at one.",
    paste0("- Bounded eligibility: at most ", options$max_unknown, " unobserved footprint dyads; at most ",
           options$max_per_label, " selected candidates per panel/label."),
    paste0("- Conditional completions per sampled candidate: ", options$nsim, "."),
    "- `L2` is the product of candidate-specific simulation marginals; `L3-F` is the joint completion frequency from the same draws.",
    "",
    "## Completion status",
    "",
    paste0("- Split/model outcomes scored: ", nrow(completed_models), "/", nrow(model_status)),
    paste0("- Candidate/model rows: ", nrow(scores), "; simulated rows: ", nrow(simulated), "."),
    paste0("- Simulated rows with a zero Monte Carlo joint score: ", nrow(zero_scores), "."),
    "",
    "`delta_dep = log(L3-F) - log(L2)` is reported only when both Monte Carlo estimates are positive. A zero L3-F is not treated as an exact zero probability; `L3_F_zero_upper95` records the rule-of-three upper bound (3/nsim).",
    "",
    "## Required interpretation boundary",
    "",
    "This output is a bounded conditional-simulation and MCMLE-feasibility diagnostic. It is not a final ranking comparison, native-event probability, model goodness-of-fit approval, or coefficient-inference table. Inspect `model_status.csv`, `diagnostics/`, and every nonempty `message` before interpreting any candidate value.",
    ""
  )
  writeLines(lines, path, useBytes = TRUE)
}

joint_main <- function() {
  options <- parse_cli(commandArgs(trailingOnly = TRUE))
  if (!is.null(options$help)) {
    cat(joint_usage(), "\n")
    return(invisible(NULL))
  }
  required <- c("input-dir", "output-dir")
  missing <- required[!required %in% names(options)]
  if (length(missing) > 0L) {
    cat(joint_usage(), "\n", file = stderr())
    stop("Missing required options: ", paste(paste0("--", missing), collapse = ", "), call. = FALSE)
  }
  allowed <- c(
    required, "models", "split", "max-candidates-per-label", "max-unobserved-dyads", "nsim",
    "mcmc-burnin", "mcmc-interval", "fit-mcmc-burnin", "fit-mcmc-interval",
    "fit-mcmc-samplesize", "mcmle-maxit", "seed", "overwrite"
  )
  unknown <- setdiff(names(options), allowed)
  if (length(unknown) > 0L) stop("Unknown option(s): ", paste(paste0("--", unknown), collapse = ", "), call. = FALSE)
  output_dir <- prepare_output_dir(option_value(options, "output-dir"), as_flag(option_value(options, "overwrite", "FALSE"), "overwrite"))
  input_dir <- normalizePath(option_value(options, "input-dir"), winslash = "/", mustWork = TRUE)
  models_text <- option_value(options, "models", "M1,M4")
  selected_specs <- score_select_models(models_text)
  max_per_label <- as_positive_number(option_value(options, "max-candidates-per-label", "5"), "max-candidates-per-label", integer = TRUE)
  max_unknown <- suppressWarnings(as.integer(option_value(options, "max-unobserved-dyads", "2")))
  if (is.na(max_unknown) || max_unknown < 0L) stop("--max-unobserved-dyads must be a nonnegative integer.", call. = FALSE)
  nsim <- as_positive_number(option_value(options, "nsim", "500"), "nsim", integer = TRUE)
  mcmc_burnin <- as_positive_number(option_value(options, "mcmc-burnin", "1000"), "mcmc-burnin", integer = TRUE)
  mcmc_interval <- as_positive_number(option_value(options, "mcmc-interval", "100"), "mcmc-interval", integer = TRUE)
  fit_burnin <- as_positive_number(option_value(options, "fit-mcmc-burnin", "5000"), "fit-mcmc-burnin", integer = TRUE)
  fit_interval <- as_positive_number(option_value(options, "fit-mcmc-interval", "500"), "fit-mcmc-interval", integer = TRUE)
  fit_samplesize <- as_positive_number(option_value(options, "fit-mcmc-samplesize", "512"), "fit-mcmc-samplesize", integer = TRUE)
  mcmle_maxit <- as_positive_number(option_value(options, "mcmle-maxit", "10"), "mcmle-maxit", integer = TRUE)
  seed <- as_positive_number(option_value(options, "seed", "20261013"), "seed", integer = TRUE)
  set.seed(seed)

  package_names <- c("network", "ergm", "jsonlite")
  missing_packages <- package_names[!vapply(package_names, requireNamespace, logical(1L), quietly = TRUE)]
  if (length(missing_packages) > 0L) {
    message_text <- paste("Missing required R package(s):", paste(missing_packages, collapse = ", "), ". Run Rscript r/bootstrap_renv.R first.")
    write_failure_manifest(file.path(output_dir, "run_manifest.json"), "failure_missing_packages", message_text, options)
    stop(message_text, call. = FALSE)
  }
  if (utils::packageVersion("ergm") < "4.12.0") {
    message_text <- paste0("ergm >= 4.12.0 is required; found ", utils::packageVersion("ergm"), ".")
    write_failure_manifest(file.path(output_dir, "run_manifest.json"), "failure_unsupported_ergm_version", message_text, options)
    stop(message_text, call. = FALSE)
  }

  node_ids <- read_node_ids(file.path(input_dir, "nodes.csv"), "id")
  split_files <- native_discover_splits(input_dir)
  requested_split <- option_value(options, "split", "all")
  if (!identical(requested_split, "all")) {
    if (!requested_split %in% split_files$split) {
      stop(
        "Unknown --split=", requested_split, ". Available split IDs: ",
        paste(split_files$split, collapse = ", "), call. = FALSE
      )
    }
    split_files <- split_files[split_files$split == requested_split, , drop = FALSE]
  }
  diagnostics_dir <- file.path(output_dir, "diagnostics")
  fitted_dir <- file.path(output_dir, "fitted_models")
  dir.create(diagnostics_dir)
  dir.create(fitted_dir)
  fit_control <- do.call(ergm::control.ergm, list(
    MCMLE.burnin = fit_burnin,
    MCMLE.interval = fit_interval,
    MCMLE.samplesize = fit_samplesize,
    MCMLE.maxit = mcmle_maxit
  ))
  all_scores <- list()
  all_model_status <- list()
  all_split_status <- list()
  all_selected <- list()

  for (split_index in seq_len(nrow(split_files))) {
    split <- split_files$split[[split_index]]
    identity <- native_split_identity(split)
    edges <- tryCatch(read_directed_edges(split_files$train_edges_path[[split_index]], "from", "to", TRUE, node_ids), error = function(error) error)
    footprints <- tryCatch(native_read_footprints(split_files$candidate_footprints_path[[split_index]], node_ids), error = function(error) error)
    input_error <- if (inherits(edges, "error")) edges else if (inherits(footprints, "error")) footprints else NULL
    if (!is.null(input_error)) {
      all_split_status[[length(all_split_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        status = "input_failed", message = conditionMessage(input_error), nodes = length(node_ids),
        training_edges = NA_integer_, candidate_footprints = NA_integer_, candidates_eligible = NA_integer_,
        candidates_selected = NA_integer_, stringsAsFactors = FALSE
      )
      next
    }
    nw <- tryCatch(make_network(edges), error = function(error) error)
    if (inherits(nw, "error")) {
      all_split_status[[length(all_split_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        status = "network_failed", message = conditionMessage(nw), nodes = length(node_ids),
        training_edges = nrow(edges$edges), candidate_footprints = NA_integer_, candidates_eligible = NA_integer_,
        candidates_selected = NA_integer_, stringsAsFactors = FALSE
      )
      next
    }
    candidates <- tryCatch(joint_candidate_table(footprints, edges$edges), error = function(error) error)
    if (inherits(candidates, "error")) {
      all_split_status[[length(all_split_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        status = "candidate_failed", message = conditionMessage(candidates), nodes = length(node_ids),
        training_edges = nrow(edges$edges), candidate_footprints = NA_integer_, candidates_eligible = NA_integer_,
        candidates_selected = NA_integer_, stringsAsFactors = FALSE
      )
      next
    }
    selected <- joint_select_candidates(
      candidates, max_unknown, max_per_label, seed + 1009L * split_index
    )
    candidate_export <- cbind(
      data.frame(split = split, mechanism = identity$mechanism, replicate = identity$replicate, stringsAsFactors = FALSE),
      selected
    )
    if (nrow(candidate_export) > 0L) all_selected[[length(all_selected) + 1L]] <- candidate_export
    model_outcomes <- character(nrow(selected_specs))

    for (model_index in seq_len(nrow(selected_specs))) {
      spec <- selected_specs[model_index, , drop = FALSE]
      if (nrow(selected) == 0L) {
        all_model_status[[length(all_model_status) + 1L]] <- data.frame(
          split = split, mechanism = identity$mechanism, replicate = identity$replicate,
          model = spec$model, formula = paste("nw ~", spec$rhs), status = "not_run_no_eligible_candidates",
          message = "No candidate satisfied the bounded unknown-dyad rule.", warnings = "",
          selected_candidates = 0L, candidates_requiring_simulation = 0L, candidates_scored = 0L,
          diagnostics_file = "", fitted_model_file = "", stringsAsFactors = FALSE
        )
        model_outcomes[[model_index]] <- "not_run_no_eligible_candidates"
        next
      }
      set.seed(seed + 100000L * split_index + model_index)
      fit_result <- joint_fit_mcmle(spec, nw, fit_control)
      safe_id <- gsub("[^A-Za-z0-9_.-]", "_", paste(split, spec$model, sep = "__"))
      diagnostics_file <- file.path("diagnostics", paste0(safe_id, ".txt"))
      fitted_file <- file.path("fitted_models", paste0(safe_id, ".rds"))
      if (!identical(fit_result$status, "fit_succeeded")) {
        all_model_status[[length(all_model_status) + 1L]] <- data.frame(
          split = split, mechanism = identity$mechanism, replicate = identity$replicate,
          model = spec$model, formula = fit_result$formula, status = "fit_failed", message = fit_result$message,
          warnings = paste(unique(fit_result$warnings), collapse = " | "), selected_candidates = nrow(selected),
          candidates_requiring_simulation = sum(selected$unobserved_footprint_arcs > 0L), candidates_scored = 0L,
          diagnostics_file = "", fitted_model_file = "", stringsAsFactors = FALSE
        )
        model_outcomes[[model_index]] <- "fit_failed"
        next
      }
      diagnostics <- capture_fit_diagnostics(spec$model, fit_result$fit, "MCMLE")
      writeLines(diagnostics$text, file.path(output_dir, diagnostics_file), useBytes = TRUE)
      saveRDS(fit_result$fit, file.path(output_dir, fitted_file))
      scored <- 0L
      for (candidate_index in seq_len(nrow(selected))) {
        candidate <- selected[candidate_index, , drop = FALSE]
        dyads <- tryCatch(joint_candidate_dyads(footprints, candidate), error = function(error) error)
        outcome <- if (inherits(dyads, "error")) {
          list(
            status = "input_failed", simulation_draws = 0L, L1 = NA_real_, L1g = NA_real_, L2 = NA_real_,
            log_L2 = NA_real_, L3_F = NA_real_, L3_F_mcse = NA_real_, L3_F_zero_upper95 = NA_real_,
            delta_dep = NA_real_, delta_dep_status = "not_estimable", factorization_gap = NA_real_,
            message = conditionMessage(dyads)
          )
        } else {
          joint_simulation_scores(
            fit_result$fit, nw, candidate, dyads, edges$edges, node_ids, nsim, mcmc_burnin,
            mcmc_interval, seed + 10000000L * split_index + 10000L * model_index + candidate_index
          )
        }
        all_scores[[length(all_scores) + 1L]] <- joint_score_row(split, identity, candidate, spec$model, outcome)
        if (outcome$status %in% c("simulated", "fixed_complete_footprint")) scored <- scored + 1L
      }
      all_model_status[[length(all_model_status) + 1L]] <- data.frame(
        split = split, mechanism = identity$mechanism, replicate = identity$replicate,
        model = spec$model, formula = fit_result$formula, status = "scored", message = "",
        warnings = paste(unique(fit_result$warnings), collapse = " | "), selected_candidates = nrow(selected),
        candidates_requiring_simulation = sum(selected$unobserved_footprint_arcs > 0L), candidates_scored = scored,
        diagnostics_file = diagnostics_file, fitted_model_file = fitted_file, stringsAsFactors = FALSE
      )
      model_outcomes[[model_index]] <- if (scored == nrow(selected)) "scored" else "completed_with_simulation_failures"
    }
    all_split_status[[length(all_split_status) + 1L]] <- data.frame(
      split = split, mechanism = identity$mechanism, replicate = identity$replicate,
      status = if (length(model_outcomes) > 0L && all(model_outcomes == "scored")) "completed" else "completed_with_model_or_simulation_failures",
      message = if (length(model_outcomes) > 0L && all(model_outcomes == "scored")) "" else "Inspect model_status.csv and candidate_simulation_scores.csv.",
      nodes = length(node_ids), training_edges = nrow(edges$edges), candidate_footprints = nrow(candidates),
      candidates_eligible = sum(candidates$unobserved_footprint_arcs <= max_unknown),
      candidates_selected = nrow(selected), stringsAsFactors = FALSE
    )
  }

  scores <- if (length(all_scores) > 0L) do.call(rbind, all_scores) else joint_empty_scores()
  model_status <- if (length(all_model_status) > 0L) do.call(rbind, all_model_status) else joint_empty_model_status()
  split_status <- if (length(all_split_status) > 0L) do.call(rbind, all_split_status) else joint_empty_split_status()
  selected_candidates <- if (length(all_selected) > 0L) do.call(rbind, all_selected) else data.frame()
  utils::write.csv(scores, file.path(output_dir, "candidate_simulation_scores.csv"), row.names = FALSE, na = "")
  utils::write.csv(model_status, file.path(output_dir, "model_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(split_status, file.path(output_dir, "split_status.csv"), row.names = FALSE, na = "")
  utils::write.csv(selected_candidates, file.path(output_dir, "selected_candidates.csv"), row.names = FALSE, na = "")
  summary_options <- list(max_unknown = max_unknown, max_per_label = max_per_label, nsim = nsim)
  joint_write_summary(file.path(output_dir, "summary.md"), basename(input_dir), model_status, split_status, scores, summary_options)
  manifest <- list(
    status = if (nrow(split_status) > 0L && all(split_status$status == "completed")) "completed" else "completed_with_failures",
    script = "r/models/simulate_joint_footprint_ergm.R",
    generated_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input = list(
      input_dir = input_dir,
      requested_split = requested_split,
      contract = "native-event ERGM export; split-specific observed projection and candidate footprints"
    ),
    models = as.list(selected_specs$model),
    estimation = list(
      fit = "split-specific MCMLE, selected with ergm estimate='MLE', eval.loglik=FALSE",
      fit_mcmc_burnin = fit_burnin, fit_mcmc_interval = fit_interval,
      fit_mcmc_samplesize = fit_samplesize, mcmle_maxit = mcmle_maxit,
      candidate_simulation = "simulate(fit, basis=network_with_candidate_unknown_dyads_as_NA, constraints=~observed)",
      simulation_draws = nsim, simulation_mcmc_burnin = mcmc_burnin, simulation_mcmc_interval = mcmc_interval,
      seed = seed
    ),
    selection = list(max_candidates_per_panel_label = max_per_label, max_unobserved_footprint_dyads = max_unknown),
    scores = list(
      L2 = "product of conditional-simulation marginal probabilities; observed footprint arcs contribute one",
      L3_F = "conditional-simulation footprint-completion frequency; observed footprint arcs remain fixed",
      delta_dep = "log(L3_F)-log(L2), reported only when both Monte Carlo estimates are positive"
    ),
    limitations = c(
      "A candidate subset and unknown-dyad cap are computational pilot bounds, not the final evaluation universe.",
      "The likelihood normalizing constant is deliberately not evaluated; no AIC, BIC, or likelihood-based model comparison is available in this pilot.",
      "A zero Monte Carlo L3-F is not interpreted as an exact zero probability; its rule-of-three upper bound is retained.",
      "MCMLE diagnostic text is captured per split/model but no automatic goodness-of-fit approval is claimed.",
      "Scores concern graph-footprint completion, never the probability of a recorded native event."
    ),
    package_versions = lapply(package_names, function(package) as.character(utils::packageVersion(package)))
  )
  names(manifest$package_versions) <- package_names
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), auto_unbox = TRUE, pretty = TRUE, null = "null")
  message("Conditional joint ERGM footprint simulation pilot complete. Output: ", output_dir)
}

if (sys.nframe() == 0L) joint_main()
