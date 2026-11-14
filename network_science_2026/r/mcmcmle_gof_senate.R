# MCMC-MLE versus MPLE and simulated goodness of fit for M4c and M5.
#
# Input: the CSV files written by scripts/export_networks_for_r.py
#   <dir>/<network>_arcs.csv   (columns: tail, head; 0-based node indices)
#   <dir>/nodes.csv            (columns: idx, party, state, nominate, majority, seniority)
# Networks: complete 118th Senate cap-eligible projection, plus the training
# projection of mask 1 under MCAR and under MNAR-out.
#
# Usage: Rscript r/mcmcmle_gof_senate.R <export-dir> <output-dir>
# Requires: ergm (>= 4.6), network. Runtime: roughly 10-40 minutes per network.

suppressPackageStartupMessages({
  library(network)
  library(ergm)
})

args <- commandArgs(trailingOnly = TRUE)
in_dir <- if (length(args) >= 1) args[[1]] else "results/revision/r_export"
out_dir <- if (length(args) >= 2) args[[2]] else "results/revision/mcmcmle"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
set.seed(20261103)

nodes <- read.csv(file.path(in_dir, "nodes.csv"), stringsAsFactors = FALSE)
n <- nrow(nodes)

build_net <- function(arcs) {
  nw <- network.initialize(n, directed = TRUE, loops = FALSE)
  if (nrow(arcs) > 0) nw <- add.edges(nw, tail = arcs$tail + 1L, head = arcs$head + 1L)
  nw %v% "party" <- nodes$party
  nw %v% "state" <- nodes$state
  nw %v% "nominate" <- nodes$nominate
  nw %v% "majority" <- nodes$majority
  nw %v% "seniority" <- nodes$seniority
  nw
}

# Fixed decays (alpha = beta = 0.5) exactly as in the Python MPLE ladder.
f_m4c <- ~ edges + mutual +
  gwodegree(0.5, fixed = TRUE) + gwidegree(0.5, fixed = TRUE) +
  dgwesp(0.5, fixed = TRUE, type = "OTP") +
  dgwesp(0.5, fixed = TRUE, type = "OSP") +
  dgwesp(0.5, fixed = TRUE, type = "ISP") +
  ctriple
f_m5 <- update(f_m4c, ~ . + nodematch("party") + nodematch("state") + absdiff("nominate"))

ctrl <- control.ergm(
  MCMLE.maxit = 40,
  MCMC.burnin = 50000,
  MCMC.interval = 1024,
  MCMC.samplesize = 2048,
  MCMLE.effectiveSize = NULL,
  parallel = 0,
  seed = 20261103
)

networks <- sub("_arcs.csv$", "", list.files(in_dir, pattern = "_arcs.csv$"))
networks <- networks[order(networks != "complete")]
if (length(args) >= 3) networks <- intersect(networks, strsplit(args[[3]], ",")[[1]])
summary_rows <- list()

for (net_name in networks) {
  arcs <- read.csv(file.path(in_dir, paste0(net_name, "_arcs.csv")))
  nw <- build_net(arcs)
  for (model_name in c("M4c", "M5")) {
    f <- if (model_name == "M4c") f_m4c else f_m5
    f <- update(f, nw ~ .)
    environment(f) <- environment()
    message("Fitting ", model_name, " on ", net_name)
    fit_pl <- ergm(f, estimate = "MPLE")
    fit_ml <- tryCatch(ergm(f, control = ctrl), error = function(e) e)
    tag <- paste(net_name, model_name, sep = "_")
    if (inherits(fit_ml, "error")) {
      writeLines(conditionMessage(fit_ml), file.path(out_dir, paste0(tag, "_ERROR.txt")))
      next
    }
    co <- data.frame(
      term = names(coef(fit_ml)),
      mple = unname(coef(fit_pl)),
      mple_se = unname(sqrt(diag(vcov(fit_pl)))),
      mcmcmle = unname(coef(fit_ml)),
      mcmcmle_se = unname(sqrt(diag(vcov(fit_ml))))
    )
    write.csv(co, file.path(out_dir, paste0(tag, "_coefficients.csv")), row.names = FALSE)

    # Conditional tie probabilities under both estimates, for every ordered dyad.
    pl_pred <- predict(fit_pl, conditional = TRUE, output = "matrix")
    ml_pred <- predict(fit_ml, conditional = TRUE, output = "matrix")
    off <- row(pl_pred) != col(pl_pred)
    rho <- cor(pl_pred[off], ml_pred[off], method = "spearman")
    write.csv(data.frame(i = row(pl_pred)[off] - 1L, j = col(pl_pred)[off] - 1L,
                         p_mple = pl_pred[off], p_mcmcmle = ml_pred[off]),
              file.path(out_dir, paste0(tag, "_conditional_probs.csv")), row.names = FALSE)

    # MCMC diagnostics and goodness of fit.
    pdf(file.path(out_dir, paste0(tag, "_mcmc_diagnostics.pdf")))
    try(mcmc.diagnostics(fit_ml), silent = TRUE)
    dev.off()
    g <- gof(fit_ml, GOF = ~ idegree + odegree + espartners + dspartners + distance + model,
             control = control.gof.ergm(nsim = 100, seed = 20261103))
    saveRDS(g, file.path(out_dir, paste0(tag, "_gof.rds")))
    pdf(file.path(out_dir, paste0(tag, "_gof.pdf")), width = 10, height = 8)
    par(mfrow = c(2, 3)); plot(g); dev.off()
    capture.output(print(g), file = file.path(out_dir, paste0(tag, "_gof.txt")))

    summary_rows[[tag]] <- data.frame(network = net_name, model = model_name,
                                      spearman_conditional = rho,
                                      aic_mcmcmle = AIC(fit_ml), bic_mcmcmle = BIC(fit_ml))
  }
}
write.csv(do.call(rbind, summary_rows), file.path(out_dir, "summary.csv"), row.names = FALSE)
message("Done. Outputs in ", out_dir)
