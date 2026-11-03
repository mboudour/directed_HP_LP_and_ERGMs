# Adequacy of the sender-receiver ERGMs on the complete 118th Senate projection:
# MPLE fit, simulated statistics and simulation-based goodness of fit.
# Usage: Rscript r/gof_sender_receiver_senate.R <export-dir> <output-dir>
suppressPackageStartupMessages({ library(network); library(ergm) })
args <- commandArgs(trailingOnly = TRUE)
in_dir <- args[[1]]; out_dir <- args[[2]]
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
set.seed(20261103)
nodes <- read.csv(file.path(in_dir, "nodes.csv"))
arcs <- read.csv(file.path(in_dir, "complete_arcs.csv"))
nw <- network.initialize(nrow(nodes), directed = TRUE, loops = FALSE)
nw <- add.edges(nw, tail = arcs$tail + 1L, head = arcs$head + 1L)
for (v in c("party", "state", "nominate")) nw %v% v <- nodes[[v]]
cov <- "nodematch('party') + nodematch('state') + absdiff('nominate')"
specs <- list(S0 = "edges + mutual + sender + receiver",
              S1 = paste("edges + mutual + sender + receiver +", cov),
              S2 = paste("edges + mutual + sender + receiver + dgwesp(0.5, fixed = TRUE, type = 'OTP') +", cov))
obs <- summary(nw ~ edges + mutual + ttriple + ctriple)
rows <- list()
for (m in names(specs)) {
  f <- as.formula(paste("nw ~", specs[[m]]))
  pl <- ergm(f, estimate = "MPLE")
  ctrl <- control.simulate.formula(MCMC.burnin = 200000, MCMC.interval = 10000)
  sims <- simulate(pl, nsim = 100, output = "stats", monitor = ~ edges + mutual + ttriple + ctriple,
                   control = ctrl)
  st <- as.data.frame(sims)
  for (k in names(obs)) {
    rows[[paste(m, k)]] <- data.frame(model = m, statistic = k, observed = unname(obs[k]),
                                      sim_mean = mean(st[[k]]), sim_q025 = quantile(st[[k]], 0.025),
                                      sim_q975 = quantile(st[[k]], 0.975))
  }
  write.csv(do.call(rbind, rows), file.path(out_dir, "simulation_summary.csv"), row.names = FALSE)
  g <- gof(pl, GOF = ~ idegree + odegree + espartners + distance + model,
           control = control.gof.ergm(nsim = 100, MCMC.burnin = 200000, MCMC.interval = 10000,
                                      seed = 20261103))
  capture.output(print(g), file = file.path(out_dir, paste0(m, "_gof.txt")))
  pdf(file.path(out_dir, paste0(m, "_gof.pdf")), width = 11, height = 7)
  par(mfrow = c(2, 3)); plot(g); dev.off()
  message("done ", m)
}
