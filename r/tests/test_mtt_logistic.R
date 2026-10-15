# Dependency-light contract test for the Mtt transitive-triple logistic driver.

source("r/models/fit_mtt_logistic.R")

adjacency <- matrix(
  c(
    0, 1, 1,
    0, 0, 1,
    0, 0, 0
  ),
  nrow = 3,
  byrow = TRUE
)
statistics <- mtt_change_statistics(adjacency)
stopifnot(statistics$oi[1, 3] == 1)
stopifnot(statistics$oo[1, 3] == 0)
stopifnot(statistics$ii[1, 3] == 0)
stopifnot(statistics$total[1, 3] == 1)
stopifnot(is.na(statistics$total[1, 1]))

design <- mtt_design(adjacency)
stopifnot(nrow(design) == 6L)
stopifnot(all(design$response %in% c(0L, 1L)))
stopifnot(max(design$common_neighbor_total) == 1)

positive_row <- data.frame(
  mechanism = "mcar",
  completed_masks = 2L,
  positive_theta_masks = 2L,
  negative_theta_masks = 0L,
  zero_theta_masks = 0L,
  theta_triple_mean = 0.2,
  theta_triple_sd = 0.1,
  theta_triple_min = 0.1,
  theta_triple_max = 0.3,
  rank_relation = "increasing_same_order_as_directed_CN",
  stringsAsFactors = FALSE
)
stopifnot(identical(positive_row$rank_relation[[1L]], "increasing_same_order_as_directed_CN"))

cat("PASS: Mtt common-neighbour change statistics and design contract.\n")
