# Simulate networks from the MPLE estimates of the ladder on the complete
# 118th Senate projection and compare simulated with observed statistics.
# A model whose MPLE generates networks far from the observed one (or that
# drifts to empty or complete graphs) is near-degenerate: its MPLE is usable
# as a source of conditional tie scores but not as a likelihood estimate.
#
# Usage: Rscript r/simulate_from_mple_senate.R <export-dir> <output-dir>

suppressPackageStartupMessages({
  library(network)
  library(ergm)
})
args <- commandArgs(trailingOnly = TRUE)
in_dir <- if (length(args) >= 1) args[[1]] else "results/revision/r_export"
out_dir <- if (length(args) >= 2) args[[2]] else "results/revision/mple_simulation"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
set.seed(20261103)

nodes <- read.csv(file.path(in_dir, "nodes.csv"))
arcs <- read.csv(file.path(in_dir, "complete_arcs.csv"))
n <- nrow(nodes)
nw <- network.initialize(n, directed = TRUE, loops = FALSE)
nw <- add.edges(nw, tail = arcs$tail + 1L, head = arcs$head + 1L)
for (v in c("party", "state", "nominate", "majority", "seniority")) nw %v% v <- nodes[[v]]

rhs <- list(
  M1 = "edges + mutual",
  M2 = "edges + mutual + gwodegree(0.5, fixed = TRUE) + gwidegree(0.5, fixed = TRUE)",
  M4c = paste("edges + mutual + gwodegree(0.5, fixed = TRUE) + gwidegree(0.5, fixed = TRUE) +",
              "dgwesp(0.5, fixed = TRUE, type = 'OTP') + dgwesp(0.5, fixed = TRUE, type = 'OSP') +",
              "dgwesp(0.5, fixed = TRUE, type = 'ISP') + ctriple"),
  M5 = paste("edges + mutual + gwodegree(0.5, fixed = TRUE) + gwidegree(0.5, fixed = TRUE) +",
             "dgwesp(0.5, fixed = TRUE, type = 'OTP') + dgwesp(0.5, fixed = TRUE, type = 'OSP') +",
             "dgwesp(0.5, fixed = TRUE, type = 'ISP') + ctriple +",
             "nodematch('party') + nodematch('state') + absdiff('nominate')")
)
monitor <- ~ edges + mutual + ttriple + idegree(0:3) + odegree(0:3)
obs <- summary(as.formula(paste("nw ~ edges + mutual + ttriple + idegree(0:3) + odegree(0:3)")))

rows <- list()
for (m in names(rhs)) {
  f <- as.formula(paste("nw ~", rhs[[m]]))
  pl <- ergm(f, estimate = "MPLE")
  write.csv(data.frame(term = names(coef(pl)), mple = unname(coef(pl)),
                       se = unname(sqrt(diag(vcov(pl))))),
            file.path(out_dir, paste0(m, "_mple.csv")), row.names = FALSE)
  sims <- simulate(pl, nsim = 100, output = "stats", monitor = monitor,
                   control = control.simulate.formula(MCMC.burnin = 200000, MCMC.interval = 10000))
  st <- as.data.frame(sims)
  keep <- names(obs)
  sm <- sapply(keep, function(k) mean(st[[k]]))
  lo <- sapply(keep, function(k) quantile(st[[k]], 0.025))
  hi <- sapply(keep, function(k) quantile(st[[k]], 0.975))
  rows[[m]] <- data.frame(model = m, statistic = keep, observed = unname(obs[keep]),
                          sim_mean = unname(sm), sim_q025 = unname(lo), sim_q975 = unname(hi))
  write.csv(do.call(rbind, rows), file.path(out_dir, "simulation_summary.csv"), row.names = FALSE)
  message("done ", m)
}
message("Finished")
