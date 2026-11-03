# MCMC-MLE of one model on the complete 118th Senate projection from a
# contrastive-divergence start, followed by simulated goodness of fit.
# Usage: Rscript r/mcmcmle_cd_senate.R <export-dir> <output-dir> <model: M2|M4c|M5>
suppressPackageStartupMessages({
  library(network)
  library(ergm)
})
args <- commandArgs(trailingOnly = TRUE)
in_dir <- args[[1]]; out_dir <- args[[2]]; m <- args[[3]]
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
set.seed(20261103)
nodes <- read.csv(file.path(in_dir, "nodes.csv"))
arcs <- read.csv(file.path(in_dir, "complete_arcs.csv"))
nw <- network.initialize(nrow(nodes), directed = TRUE, loops = FALSE)
nw <- add.edges(nw, tail = arcs$tail + 1L, head = arcs$head + 1L)
for (v in c("party", "state", "nominate", "majority", "seniority")) nw %v% v <- nodes[[v]]
base <- paste("edges + mutual + gwodegree(0.5, fixed = TRUE) + gwidegree(0.5, fixed = TRUE)")
closure <- paste("dgwesp(0.5, fixed = TRUE, type = 'OTP') + dgwesp(0.5, fixed = TRUE, type = 'OSP') +",
                 "dgwesp(0.5, fixed = TRUE, type = 'ISP') + ctriple")
cov <- "nodematch('party') + nodematch('state') + absdiff('nominate')"
rhs <- switch(m, M2 = base, M4c = paste(base, "+", closure), M5 = paste(base, "+", closure, "+", cov))
f <- as.formula(paste("nw ~", rhs))
t0 <- Sys.time()
fit <- tryCatch(ergm(f, control = control.ergm(init.method = "CD", MCMLE.maxit = 25,
                                                 MCMC.samplesize = 2048, seed = 20261103)),
                error = function(e) e)
if (inherits(fit, "error")) {
  writeLines(conditionMessage(fit), file.path(out_dir, paste0(m, "_ERROR.txt")))
} else {
  pl <- ergm(f, estimate = "MPLE")
  write.csv(data.frame(term = names(coef(fit)), mple = unname(coef(pl)), mcmcmle = unname(coef(fit)),
                       mcmcmle_se = unname(sqrt(diag(vcov(fit))))),
            file.path(out_dir, paste0(m, "_coefficients.csv")), row.names = FALSE)
  p1 <- predict(pl, conditional = TRUE, output = "matrix")
  p2 <- predict(fit, conditional = TRUE, output = "matrix")
  off <- row(p1) != col(p1)
  writeLines(sprintf("spearman_conditional=%.4f minutes=%.1f", cor(p1[off], p2[off], method = "spearman"),
                     as.numeric(difftime(Sys.time(), t0, units = "mins"))),
             file.path(out_dir, paste0(m, "_comparison.txt")))
  g <- gof(fit, GOF = ~ idegree + odegree + espartners + distance + model,
           control = control.gof.ergm(nsim = 100, seed = 20261103))
  capture.output(print(g), file = file.path(out_dir, paste0(m, "_gof.txt")))
  pdf(file.path(out_dir, paste0(m, "_gof.pdf")), width = 10, height = 7)
  par(mfrow = c(2, 3)); plot(g); dev.off()
}
