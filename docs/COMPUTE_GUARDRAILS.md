# Local computational guardrails

## Purpose

Some ERGM MCMC-MLE fits can adaptively enlarge their simulation work when the
estimating equations remain outside the convergence tolerance. This is useful in
batch computing, but inappropriate for an unattended interactive terminal.

`scripts/40_run_bounded_command.py` runs one command under a wall-clock limit,
captures all output in a specified log, and terminates the complete child process
group on timeout. It returns exit code `124` on timeout.

## Required use for exploratory MCMC-MLE fits

Use the runner for every newly introduced local MCMC-MLE feasibility run until
its expected duration is known. A timeout is a **computational gate outcome**,
not a reason to repeat the command with an arbitrary larger limit.

Example:

```zsh
python3 scripts/40_run_bounded_command.py \
  --timeout-seconds=120 \
  --log=results/models/example_mcmle_feasibility.txt \
  -- Rscript r/models/simulate_joint_footprint_ergm.R \
  --input-dir=results/phase2/enron_native_event_ergm_inputs \
  --output-dir=results/models/example_mcmle \
  --models=M2 --estimate=MCMLE --overwrite=TRUE
```

Read and retain the log after both a completed run and a timeout. The log reports
the command, elapsed time, exit status, and all output produced before the
process ended.

## Scientific boundary

A completed command is not evidence that an MCMC-MLE is acceptable. Convergence,
non-degeneracy, diagnostics, and the planned posterior-predictive checks remain
separate requirements. A timeout or non-convergence is recorded as a pilot-gate
failure; it is never silently replaced with a different estimator.
