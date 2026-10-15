#!/usr/bin/env Rscript

# Fit the exact MPLE/logistic representation of the edges + unweighted
# transitive-triple ERGM on each event-first observed projection. The driver
# emits actor-free split and mechanism aggregates only.

mtt_usage <- function() {
  paste(
    "Usage: Rscript r/models/fit_mtt_logistic.R --input-dir=DIR --output-dir=DIR --dataset-id=ID [options]",
    "",
    "Input contract:",
    "  DIR/nodes.csv                                      CSV with unique id column.",
    "  DIR/splits/<mechanism>_replicate_NNN/train_edges.csv       CSV with from,to.",
    "",
    "Options:",
    "  --overwrite=FALSE           Refuse a non-empty output directory unless TRUE.",
    "",
    "Outputs: split_coefficients.csv, mechanism_summary.csv, summary.md, and run_manifest.json.",
    "The fitted logistic model is y_ij ~ 1 + s_CN, where s_CN is the exact",
    "change statistic for the unweighted directed transitive-triple term.",
    sep = "\n"
  )
}

mtt_parse_cli <- function(args) {
  options <- list()
  index <- 1L
  while (index <= length(args)) {
    argument <- args[[index]]
    if (!startsWith(argument, "--")) stop("Unexpected argument: ", argument, call. = FALSE)
    item <- substring(argument, 3L)
    if (item %in% c("help", "h")) {
      options$help <- "TRUE"
      index <- index + 1L
      next
    }
    if (grepl("=", item, fixed = TRUE)) {
      pieces <- strsplit(item, "=", fixed = TRUE)[[1L]]
      key <- pieces[[1L]]
      value <- paste(pieces[-1L], collapse = "=")
    } else {
      if (index == length(args) || startsWith(args[[index + 1L]], "--")) {
        stop("Argument --", item, " requires a value.", call. = FALSE)
      }
      key <- item
      value <- args[[index + 1L]]
      index <- index + 1L
    }
    if (!nzchar(key) || !nzchar(value)) stop("Empty option or value in ", argument, call. = FALSE)
    options[[key]] <- value
    index <- index + 1L
  }
  options
}

mtt_option <- function(options, name, default = NULL) {
  if (!is.null(options[[name]])) options[[name]] else default
}

mtt_as_flag <- function(value, name) {
  normalized <- tolower(as.character(value))
  if (normalized %in% c("true", "t", "1", "yes", "y")) return(TRUE)
  if (normalized %in% c("false", "f", "0", "no", "n")) return(FALSE)
  stop("--", name, " must be TRUE or FALSE.", call. = FALSE)
}

mtt_prepare_output_dir <- function(path, overwrite) {
  if (dir.exists(path)) {
    contents <- list.files(path, all.files = TRUE, no.. = TRUE)
    if (length(contents) > 0L && !overwrite) {
      stop("Output directory is non-empty; pass --overwrite=TRUE: ", path, call. = FALSE)
    }
  } else if (!dir.create(path, recursive = TRUE, showWarnings = FALSE)) {
    stop("Unable to create output directory: ", path, call. = FALSE)
  }
  normalizePath(path, winslash = "/", mustWork = TRUE)
}

mtt_read_nodes <- function(path) {
  nodes <- utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE, colClasses = "character")
  if (!("id" %in% names(nodes))) stop("nodes.csv lacks id column: ", path, call. = FALSE)
  ids <- as.character(nodes$id)
  if (length(ids) < 2L || anyNA(ids) || any(!nzchar(ids)) || anyDuplicated(ids)) {
    stop("nodes.csv must contain at least two unique, non-empty IDs.", call. = FALSE)
  }
  ids
}

mtt_read_edges <- function(path, node_ids) {
  edges <- utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE, colClasses = "character")
  if (!all(c("from", "to") %in% names(edges))) {
    stop("train_edges.csv lacks from,to columns: ", path, call. = FALSE)
  }
  from <- as.character(edges$from)
  to <- as.character(edges$to)
  if (anyNA(from) || anyNA(to) || any(!nzchar(from)) || any(!nzchar(to))) {
    stop("train_edges.csv has missing or empty endpoints: ", path, call. = FALSE)
  }
  if (any(from == to)) stop("train_edges.csv has self-loops: ", path, call. = FALSE)
  if (length(setdiff(unique(c(from, to)), node_ids)) > 0L) {
    stop("train_edges.csv refers to nodes outside nodes.csv: ", path, call. = FALSE)
  }
  unique(data.frame(from = from, to = to, stringsAsFactors = FALSE))
}

mtt_split_identity <- function(name) {
  parts <- strsplit(name, "_replicate_", fixed = TRUE)[[1L]]
  if (length(parts) != 2L || !grepl("^[0-9]+$", parts[[2L]])) {
    stop("Invalid split directory name: ", name, call. = FALSE)
  }
  list(mechanism = parts[[1L]], replicate = as.integer(parts[[2L]]))
}

mtt_discover_splits <- function(input_dir) {
  splits_dir <- file.path(input_dir, "splits")
  if (!dir.exists(splits_dir)) stop("Input directory lacks splits/: ", splits_dir, call. = FALSE)
  names <- sort(list.dirs(splits_dir, recursive = FALSE, full.names = FALSE))
  complete <- names[file.exists(file.path(splits_dir, names, "train_edges.csv"))]
  if (length(complete) == 0L) stop("No split train_edges.csv files found in: ", splits_dir, call. = FALSE)
  data.frame(
    split = complete,
    train_edges_path = file.path(splits_dir, complete, "train_edges.csv"),
    stringsAsFactors = FALSE
  )
}

mtt_adjacency <- function(node_ids, edges) {
  adjacency <- matrix(0, nrow = length(node_ids), ncol = length(node_ids))
  if (nrow(edges) > 0L) {
    adjacency[cbind(match(edges$from, node_ids), match(edges$to, node_ids))] <- 1
  }
  adjacency
}

mtt_change_statistics <- function(adjacency) {
  if (!is.matrix(adjacency) || nrow(adjacency) != ncol(adjacency)) {
    stop("adjacency must be a square matrix.", call. = FALSE)
  }
  if (any(diag(adjacency) != 0) || any(!adjacency %in% c(0, 1))) {
    stop("adjacency must be loopless and binary.", call. = FALSE)
  }
  oi <- adjacency %*% adjacency
  oo <- adjacency %*% t(adjacency)
  ii <- t(adjacency) %*% adjacency
  total <- oi + oo + ii
  diag(total) <- NA_real_
  list(oi = oi, oo = oo, ii = ii, total = total)
}

mtt_design <- function(adjacency) {
  statistics <- mtt_change_statistics(adjacency)
  index <- which(row(adjacency) != col(adjacency), arr.ind = TRUE)
  data.frame(
    response = as.integer(adjacency[index]),
    common_neighbor_total = as.numeric(statistics$total[index]),
    stringsAsFactors = FALSE
  )
}

mtt_fit_split <- function(node_ids, edges) {
  adjacency <- mtt_adjacency(node_ids, edges)
  design <- mtt_design(adjacency)
  warnings <- character()
  fit <- withCallingHandlers(
    tryCatch(
      stats::glm(response ~ common_neighbor_total, family = stats::binomial(), data = design),
      error = function(error) error
    ),
    warning = function(warning) {
      warnings <<- c(warnings, conditionMessage(warning))
      invokeRestart("muffleWarning")
    }
  )
  if (inherits(fit, "error")) {
    return(list(status = "fit_failed", message = conditionMessage(fit), warnings = warnings))
  }
  coefficients <- stats::coef(fit)
  covariance <- tryCatch(stats::vcov(fit), error = function(error) NULL)
  theta_edges <- unname(coefficients[["(Intercept)"]])
  theta_triple <- unname(coefficients[["common_neighbor_total"]])
  if (!is.finite(theta_edges) || !is.finite(theta_triple)) {
    return(list(
      status = "nonfinite_coefficients",
      message = "glm returned non-finite coefficient(s).",
      warnings = warnings
    ))
  }
  theta_se <- if (!is.null(covariance) && "common_neighbor_total" %in% rownames(covariance)) {
    sqrt(max(0, covariance["common_neighbor_total", "common_neighbor_total"]))
  } else {
    NA_real_
  }
  theta_z <- if (is.finite(theta_se) && theta_se > 0) theta_triple / theta_se else NA_real_
  theta_p <- if (is.finite(theta_z)) 2 * stats::pnorm(abs(theta_z), lower.tail = FALSE) else NA_real_
  relation <- if (theta_triple > 0) {
    "increasing_same_order_as_directed_CN"
  } else if (theta_triple < 0) {
    "decreasing_reverse_order_of_directed_CN"
  } else {
    "constant_no_CN_ordering"
  }
  list(
    status = "fit_succeeded",
    message = "",
    warnings = warnings,
    theta_edges = theta_edges,
    theta_triple = theta_triple,
    theta_triple_se = theta_se,
    theta_triple_z = theta_z,
    theta_triple_p = theta_p,
    rank_relation = relation,
    nodes = length(node_ids),
    directed_edges = nrow(edges),
    dyads = nrow(design),
    cn_min = min(design$common_neighbor_total),
    cn_max = max(design$common_neighbor_total)
  )
}

mtt_empty_split_rows <- function() {
  data.frame(
    split = character(), mechanism = character(), replicate = integer(), status = character(),
    theta_edges = numeric(), theta_triple = numeric(), theta_triple_se = numeric(),
    theta_triple_z = numeric(), theta_triple_p = numeric(), rank_relation = character(),
    nodes = integer(), directed_edges = integer(), dyads = integer(), cn_min = numeric(), cn_max = numeric(),
    message = character(), warnings = character(), stringsAsFactors = FALSE
  )
}

mtt_summary <- function(rows) {
  successful <- rows[rows$status == "fit_succeeded", , drop = FALSE]
  if (nrow(successful) == 0L) {
    return(data.frame(
      mechanism = character(), completed_masks = integer(), positive_theta_masks = integer(),
      negative_theta_masks = integer(), zero_theta_masks = integer(), theta_triple_mean = numeric(),
      theta_triple_sd = numeric(), theta_triple_min = numeric(), theta_triple_max = numeric(),
      rank_relation = character(), stringsAsFactors = FALSE
    ))
  }
  grouped <- split(successful, successful$mechanism)
  do.call(rbind, lapply(names(grouped), function(mechanism) {
    frame <- grouped[[mechanism]]
    data.frame(
      mechanism = mechanism,
      completed_masks = nrow(frame),
      positive_theta_masks = sum(frame$theta_triple > 0),
      negative_theta_masks = sum(frame$theta_triple < 0),
      zero_theta_masks = sum(frame$theta_triple == 0),
      theta_triple_mean = mean(frame$theta_triple),
      theta_triple_sd = if (nrow(frame) > 1L) stats::sd(frame$theta_triple) else 0,
      theta_triple_min = min(frame$theta_triple),
      theta_triple_max = max(frame$theta_triple),
      rank_relation = paste(sort(unique(frame$rank_relation)), collapse = "; "),
      stringsAsFactors = FALSE
    )
  }))
}

mtt_write_summary <- function(path, dataset_id, rows, summary) {
  fit_count <- sum(rows$status == "fit_succeeded")
  lines <- c(
    "# Auxiliary Mtt transitive-triple logistic fits",
    "",
    paste0("- Dataset: `", dataset_id, "`"),
    "- Each split fits `y_ij ~ 1 + s_CN,ij` across every nonloop dyad in its observed projection.",
    "- `s_CN` is the exact unweighted directed transitive-triple change statistic: OI + OO + II.",
    "- This is the MPLE/logistic representation of an edges-plus-transitive-triple ERGM.",
    "- The fit verifies the sign and induced arc-level ordering only; it is not a native-event score or a joint footprint probability.",
    "",
    "## Completion",
    "",
    paste0("- Fits succeeded: ", fit_count, "/", nrow(rows)),
    "",
    "| Mechanism | Fits | Positive $\\hat\\theta_{tr}$ | Negative | Zero | Mean | SD | Range | Arc-level relation |",
    "|---|---:|---:|---:|---:|---:|---:|---|---|"
  )
  if (nrow(summary) == 0L) {
    lines <- c(lines, "| — | 0 | 0 | 0 | 0 | — | — | — | — |")
  } else {
    for (index in seq_len(nrow(summary))) {
      row <- summary[index, , drop = FALSE]
      lines <- c(lines, sprintf(
        "| %s | %d | %d | %d | %d | %.4f | %.4f | [%.4f, %.4f] | %s |",
        row$mechanism, row$completed_masks, row$positive_theta_masks,
        row$negative_theta_masks, row$zero_theta_masks, row$theta_triple_mean,
        row$theta_triple_sd, row$theta_triple_min, row$theta_triple_max, row$rank_relation
      ))
    }
  }
  writeLines(lines, path, useBytes = TRUE)
}

mtt_main <- function() {
  options <- mtt_parse_cli(commandArgs(trailingOnly = TRUE))
  if (!is.null(options$help)) {
    cat(mtt_usage(), "\n")
    return(invisible(NULL))
  }
  required <- c("input-dir", "output-dir", "dataset-id")
  missing <- required[!required %in% names(options)]
  if (length(missing) > 0L) {
    cat(mtt_usage(), "\n", file = stderr())
    stop("Missing required options: ", paste(paste0("--", missing), collapse = ", "), call. = FALSE)
  }
  allowed <- c(required, "overwrite")
  unknown <- setdiff(names(options), allowed)
  if (length(unknown) > 0L) {
    stop("Unknown option(s): ", paste(paste0("--", unknown), collapse = ", "), call. = FALSE)
  }
  input_dir <- normalizePath(mtt_option(options, "input-dir"), winslash = "/", mustWork = TRUE)
  output_dir <- mtt_prepare_output_dir(
    mtt_option(options, "output-dir"),
    mtt_as_flag(mtt_option(options, "overwrite", "FALSE"), "overwrite")
  )
  dataset_id <- mtt_option(options, "dataset-id")
  node_ids <- mtt_read_nodes(file.path(input_dir, "nodes.csv"))
  splits <- mtt_discover_splits(input_dir)
  rows <- list()
  for (index in seq_len(nrow(splits))) {
    split <- splits$split[[index]]
    identity <- mtt_split_identity(split)
    result <- tryCatch(
      mtt_fit_split(node_ids, mtt_read_edges(splits$train_edges_path[[index]], node_ids)),
      error = function(error) list(status = "input_or_fit_failed", message = conditionMessage(error), warnings = character())
    )
    defaults <- list(
      theta_edges = NA_real_, theta_triple = NA_real_, theta_triple_se = NA_real_,
      theta_triple_z = NA_real_, theta_triple_p = NA_real_, rank_relation = "", nodes = NA_integer_,
      directed_edges = NA_integer_, dyads = NA_integer_, cn_min = NA_real_, cn_max = NA_real_
    )
    values <- modifyList(defaults, result)
    rows[[length(rows) + 1L]] <- data.frame(
      split = split,
      mechanism = identity$mechanism,
      replicate = identity$replicate,
      status = result$status,
      theta_edges = values$theta_edges,
      theta_triple = values$theta_triple,
      theta_triple_se = values$theta_triple_se,
      theta_triple_z = values$theta_triple_z,
      theta_triple_p = values$theta_triple_p,
      rank_relation = values$rank_relation,
      nodes = values$nodes,
      directed_edges = values$directed_edges,
      dyads = values$dyads,
      cn_min = values$cn_min,
      cn_max = values$cn_max,
      message = result$message,
      warnings = paste(unique(result$warnings), collapse = " | "),
      stringsAsFactors = FALSE
    )
  }
  split_rows <- if (length(rows) > 0L) do.call(rbind, rows) else mtt_empty_split_rows()
  summary <- mtt_summary(split_rows)
  utils::write.csv(split_rows, file.path(output_dir, "split_coefficients.csv"), row.names = FALSE, na = "")
  utils::write.csv(summary, file.path(output_dir, "mechanism_summary.csv"), row.names = FALSE, na = "")
  mtt_write_summary(file.path(output_dir, "summary.md"), dataset_id, split_rows, summary)
  manifest <- list(
    status = if (nrow(split_rows) > 0L && all(split_rows$status == "fit_succeeded")) "completed" else "completed_with_failures",
    script = "r/models/fit_mtt_logistic.R",
    dataset_id = dataset_id,
    input = list(
      contract = "nodes.csv[id]; splits/<mechanism>_replicate_NNN/train_edges.csv[from,to]"
    ),
    model = list(
      label = "M_tt",
      formula = "y_ij ~ 1 + s_CN,ij",
      interpretation = "Exact MPLE/logistic form of edges plus unweighted directed transitive triples."
    ),
    privacy = "Outputs are split-level coefficient summaries without actors, dyads, candidates, or records."
  )
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    stop("jsonlite is required to write run_manifest.json.", call. = FALSE)
  }
  jsonlite::write_json(manifest, file.path(output_dir, "run_manifest.json"), auto_unbox = TRUE, pretty = TRUE)
  message("Mtt logistic fits complete. Output: ", output_dir)
}

if (sys.nframe() == 0L) mtt_main()
