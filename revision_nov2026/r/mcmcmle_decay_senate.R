# MCMC maximum likelihood for M5 on the complete 118th Senate 2-section with a
# given decay for all geometrically weighted terms, and simulated adequacy.
#
# Usage: Rscript r/mcmcmle_decay_senate.R <export-dir> <output-dir> <decay>

suppressPackageStartupMessages({
  library(network)
  library(ergm)
})
args <- commandArgs(trailingOnly = TRUE)
in_dir <- args[[1]]
out_dir <- args[[2]]
decay <- as.numeric(args[[3]])
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
set.seed(20261104)

nodes <- read.csv(file.path(in_dir, "nodes.csv"))
arcs <- read.csv(file.path(in_dir, "complete_arcs.csv"))
n <- nrow(nodes)
nw <- network.initialize(n, directed = TRUE, loops = FALSE)
nw <- add.edges(nw, tail = arcs$tail + 1L, head = arcs$head + 1L)
for (v in c("party", "state", "nominate", "majority", "seniority")) nw %v% v <- nodes[[v]]

rhs <- paste(
  "edges + mutual + gwodegree(D, fixed = TRUE) + gwidegree(D, fixed = TRUE) +",
  "dgwesp(D, fixed = TRUE, type = 'OTP') + dgwesp(D, fixed = TRUE, type = 'OSP') +",
  "dgwesp(D, fixed = TRUE, type = 'ISP') + ctriple +",
  "nodematch('party') + nodematch('state') + absdiff('nominate')"
)
f <- as.formula(paste("nw ~", gsub("D", format(decay), rhs, fixed = TRUE)))
pl <- ergm(f, estimate = "MPLE")
ctrl <- control.ergm(MCMLE.maxit = 30, MCMC.burnin = 100000, MCMC.interval = 2048,
                     MCMC.samplesize = 2048, parallel = 0, seed = 20261104)
ml <- tryCatch(ergm(f, control = ctrl), error = function(e) e)
if (inherits(ml, "error")) {
  writeLines(conditionMessage(ml), file.path(out_dir, "M5_ERROR.txt"))
  quit(status = 0)
}
co <- data.frame(term = names(coef(ml)), mple = unname(coef(pl)), mcmcmle = unname(coef(ml)),
                 mcmcmle_se = unname(sqrt(diag(vcov(ml)))))
write.csv(co, file.path(out_dir, "M5_coefficients.csv"), row.names = FALSE)
monitor <- ~ edges + mutual + ttriple + ctriple
obs <- summary(nw ~ edges + mutual + ttriple + ctriple)
sims <- as.data.frame(simulate(ml, nsim = 100, output = "stats", monitor = monitor,
                               control = control.simulate.ergm(MCMC.burnin = 200000, MCMC.interval = 10000)))
keep <- names(obs)
res <- data.frame(statistic = keep, observed = unname(obs),
                  sim_mean = sapply(keep, function(k) mean(sims[[k]])),
                  sim_q025 = sapply(keep, function(k) quantile(sims[[k]], 0.025)),
                  sim_q975 = sapply(keep, function(k) quantile(sims[[k]], 0.975)))
write.csv(res, file.path(out_dir, "M5_simulation.csv"), row.names = FALSE)
message("Finished")
