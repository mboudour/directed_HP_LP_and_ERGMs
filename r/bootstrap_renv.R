#!/usr/bin/env Rscript

# Bootstrap the project-local R/statnet environment. Run from any directory with:
#   Rscript r/bootstrap_renv.R

args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args, value = TRUE)
if (length(script_arg) != 1L) {
  stop("Run this script with Rscript r/bootstrap_renv.R", call. = FALSE)
}
project_root <- normalizePath(file.path(dirname(sub("^--file=", "", script_arg)), ".."))
setwd(project_root)

repos <- getOption("repos")
repos["CRAN"] <- Sys.getenv("CRAN_MIRROR", "https://cloud.r-project.org")
options(repos = repos)

if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv")
}

renv::consent(provided = TRUE)
renv::init(bare = TRUE)

packages <- c(
  "network",
  "ergm",
  "ergm.count",
  "tergm",
  "btergm",
  "survival",
  "sna",
  "statnet.common",
  "data.table",
  "jsonlite",
  "yaml",
  "digest",
  "optparse",
  "testthat"
)

renv::install(packages)
renv::snapshot(prompt = FALSE)
message("R environment initialized and renv.lock written at: ", project_root)
