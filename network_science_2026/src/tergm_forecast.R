# Fit a TERGM by bootstrapped MPLE (btergm) to quarterly networks and forecast the target window.
# Usage: Rscript tergm_forecast.R DIR NPERIODS BIPARTITE(0/1)
# DIR contains net_t.csv (t = 1..NPERIODS), lag_t_<k>.csv, exo_<k>.csv, lag_target_<k>.csv.
suppressMessages({library(network); library(btergm)})
args <- commandArgs(TRUE)
dir <- args[1]; Tn <- as.integer(args[2]); bip <- as.integer(args[3]) == 1
rd <- function(f) as.matrix(read.csv(file.path(dir, f), header = FALSE))
lagk <- sub("^lag_1_(.*)\\.csv$", "\\1", list.files(dir, pattern = "^lag_1_.*\\.csv$"))
exok <- sub("^exo_(.*)\\.csv$", "\\1", list.files(dir, pattern = "^exo_.*\\.csv$"))
nets <- lapply(1:Tn, function(t) {
  M <- rd(sprintf("net_%d.csv", t))
  if (bip) network(M, bipartite = nrow(M), directed = FALSE) else network(M, directed = TRUE)
})
covs <- list()
for (k in lagk) covs[[k]] <- lapply(1:Tn, function(t) rd(sprintf("lag_%d_%s.csv", t, k)))
for (k in exok) { E <- rd(sprintf("exo_%s.csv", k)); covs[[k]] <- lapply(1:Tn, function(t) E) }
for (k in names(covs)) assign(paste0("cv_", k), covs[[k]])
rhs <- paste(c("edges", sprintf("edgecov(cv_%s)", names(covs))), collapse = " + ")
f <- as.formula(paste("nets ~", rhs))
set.seed(20261104)
nboot <- if (length(args) > 3) as.integer(args[4]) else 500
fit <- btergm(f, R = nboot, verbose = FALSE)
co <- coef(fit)
ci <- confint(fit)
write.csv(data.frame(term = names(co), estimate = co, ci[, c(ncol(ci) - 1, ncol(ci))]), file.path(dir, "tergm_coef.csv"), row.names = FALSE)
eta <- co[1]
for (j in seq_along(names(covs))) {
  k <- names(covs)[j]
  X <- if (k %in% exok) rd(sprintf("exo_%s.csv", k)) else rd(sprintf("lag_target_%s.csv", k))
  eta <- eta + co[j + 1] * X
}
P <- plogis(eta)
if (!bip) diag(P) <- 0
write.table(P, file.path(dir, "forecast_P.csv"), sep = ",", row.names = FALSE, col.names = FALSE)
print(cbind(estimate = round(co, 3), round(ci[, c(ncol(ci) - 1, ncol(ci))], 3)))
