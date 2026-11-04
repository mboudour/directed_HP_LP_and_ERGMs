suppressMessages(library(ergm))
M <- as.matrix(read.csv("inc.csv", header = FALSE)); A <- as.matrix(read.csv("attr.csv", header = FALSE))
n <- nrow(M); E <- ncol(M)
net <- network(M, bipartite = n, directed = FALSE)
set.vertex.attribute(net, "party", c(A[, 1], rep(NA, E)))
set.vertex.attribute(net, "state", c(A[, 2], rep(NA, E)))
m <- ergmMPLE(net ~ edges + gwb1degree(1, fixed = TRUE) + gwb2degree(1, fixed = TRUE) + cycle(4) + b1nodematch("party") + b1nodematch("state"), output = "dyadlist", expand.bipartite = TRUE)
P <- m$predictor
ours <- as.matrix(read.csv("ours.csv", header = FALSE))
idx <- (P[, "tail"] - 1) * E + (P[, "head"] - n)  # actor-major row of ours
D <- P[, -(1:2)] - ours[idx, ]
print(colnames(P)[-(1:2)]); print(apply(abs(D), 2, max)); cat("rows", nrow(P), "\n")
