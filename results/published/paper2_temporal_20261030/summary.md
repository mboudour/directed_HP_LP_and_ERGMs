# Enron conditional-RHEM sampled-risk-set sensitivities

## Design

The primary task is receiver-set choice conditional on the observed sender and observed receiver-set size. It is evaluated in four expanding 2001 quarters on a 50-actor universe selected from pre-2001 participation only. Every displayed metric is calculated within Eventnet's same-size sampled candidate sets; it is not a probability of an email event, sender, timing, or set size.

The sensitivity runs include a second sampled-control seed, a reverse deterministic order within identical timestamps, and a source-record representation sensitivity that collapses identical timestamp/sender/receiver-set footprints. Each requests 100 non-events per observed event, while an event with a singleton receiver may have fewer than 100 eligible alternatives in the 50-actor universe.

## Pooled discrimination by sensitivity variant

| Variant | Model | Scope | Choice sets | Mean log score | Top-1 | MRR | Mean rank |
|:---|:---|:---|---:|---:|---:|---:|---:|
| collapsed_timestamp_footprints_seed_20261030 | DYADIC_HISTORY | all | 1,411 | -1.8298 | 0.5708 | 0.7221 | 2.853 |
| collapsed_timestamp_footprints_seed_20261030 | DYADIC_HISTORY | head_size_1 | 1,363 | -1.8105 | 0.5672 | 0.7212 | 2.789 |
| collapsed_timestamp_footprints_seed_20261030 | DYADIC_HISTORY | head_size_ge_2 | 48 | -2.3780 | 0.6750 | 0.7473 | 4.646 |
| collapsed_timestamp_footprints_seed_20261030 | GROUP_AUGMENTED | all | 1,411 | -1.9133 | 0.5707 | 0.7225 | 2.799 |
| collapsed_timestamp_footprints_seed_20261030 | GROUP_AUGMENTED | head_size_1 | 1,363 | -1.8655 | 0.5642 | 0.7189 | 2.803 |
| collapsed_timestamp_footprints_seed_20261030 | GROUP_AUGMENTED | head_size_ge_2 | 48 | -3.2714 | 0.7542 | 0.8230 | 2.688 |
| descending_order_seed_20261030 | DYADIC_HISTORY | all | 2,797 | -1.4839 | 0.6452 | 0.7807 | 2.124 |
| descending_order_seed_20261030 | DYADIC_HISTORY | head_size_1 | 2,689 | -1.4674 | 0.6400 | 0.7788 | 2.118 |
| descending_order_seed_20261030 | DYADIC_HISTORY | head_size_ge_2 | 108 | -1.8952 | 0.7729 | 0.8272 | 2.282 |
| descending_order_seed_20261030 | GROUP_AUGMENTED | all | 2,797 | -1.4429 | 0.6487 | 0.7838 | 2.163 |
| descending_order_seed_20261030 | GROUP_AUGMENTED | head_size_1 | 2,689 | -1.4637 | 0.6400 | 0.7789 | 2.187 |
| descending_order_seed_20261030 | GROUP_AUGMENTED | head_size_ge_2 | 108 | -0.9244 | 0.8655 | 0.9075 | 1.579 |
| primary_ascending_seed_20261030 | DYADIC_HISTORY | all | 2,797 | -1.4829 | 0.6440 | 0.7803 | 2.125 |
| primary_ascending_seed_20261030 | DYADIC_HISTORY | head_size_1 | 2,689 | -1.4671 | 0.6397 | 0.7786 | 2.118 |
| primary_ascending_seed_20261030 | DYADIC_HISTORY | head_size_ge_2 | 108 | -1.8772 | 0.7531 | 0.8218 | 2.296 |
| primary_ascending_seed_20261030 | GROUP_AUGMENTED | all | 2,797 | -1.4469 | 0.6523 | 0.7856 | 2.226 |
| primary_ascending_seed_20261030 | GROUP_AUGMENTED | head_size_1 | 2,689 | -1.4671 | 0.6437 | 0.7805 | 2.252 |
| primary_ascending_seed_20261030 | GROUP_AUGMENTED | head_size_ge_2 | 108 | -0.9431 | 0.8642 | 0.9116 | 1.602 |
| sampling_seed_20261031 | DYADIC_HISTORY | all | 2,797 | -1.4830 | 0.6425 | 0.7794 | 2.128 |
| sampling_seed_20261031 | DYADIC_HISTORY | head_size_1 | 2,689 | -1.4670 | 0.6393 | 0.7784 | 2.119 |
| sampling_seed_20261031 | DYADIC_HISTORY | head_size_ge_2 | 108 | -1.8794 | 0.7238 | 0.8037 | 2.366 |
| sampling_seed_20261031 | GROUP_AUGMENTED | all | 2,797 | -1.4648 | 0.6521 | 0.7854 | 2.272 |
| sampling_seed_20261031 | GROUP_AUGMENTED | head_size_1 | 2,689 | -1.4715 | 0.6437 | 0.7803 | 2.305 |
| sampling_seed_20261031 | GROUP_AUGMENTED | head_size_ge_2 | 108 | -1.2979 | 0.8611 | 0.9110 | 1.458 |

## Group-augmented minus dyadic-history contrast

| Variant | Scope | Choice sets | Δ log score | Δ Top-1 | Δ MRR | Δ mean rank |
|:---|:---|---:|---:|---:|---:|---:|
| collapsed_timestamp_footprints_seed_20261030 | all | 1,411 | -0.0836 | -0.0001 | +0.0003 | -0.053 |
| collapsed_timestamp_footprints_seed_20261030 | head_size_1 | 1,363 | -0.0550 | -0.0029 | -0.0023 | +0.014 |
| collapsed_timestamp_footprints_seed_20261030 | head_size_ge_2 | 48 | -0.8934 | +0.0792 | +0.0757 | -1.958 |
| descending_order_seed_20261030 | all | 2,797 | +0.0410 | +0.0036 | +0.0031 | +0.039 |
| descending_order_seed_20261030 | head_size_1 | 2,689 | +0.0036 | +0.0000 | +0.0001 | +0.069 |
| descending_order_seed_20261030 | head_size_ge_2 | 108 | +0.9707 | +0.0926 | +0.0803 | -0.704 |
| primary_ascending_seed_20261030 | all | 2,797 | +0.0360 | +0.0082 | +0.0053 | +0.102 |
| primary_ascending_seed_20261030 | head_size_1 | 2,689 | -0.0000 | +0.0041 | +0.0019 | +0.134 |
| primary_ascending_seed_20261030 | head_size_ge_2 | 108 | +0.9341 | +0.1111 | +0.0898 | -0.694 |
| sampling_seed_20261031 | all | 2,797 | +0.0181 | +0.0096 | +0.0060 | +0.144 |
| sampling_seed_20261031 | head_size_1 | 2,689 | -0.0045 | +0.0045 | +0.0020 | +0.186 |
| sampling_seed_20261031 | head_size_ge_2 | 108 | +0.5815 | +0.1373 | +0.1073 | -0.907 |

## Interpretation boundary

The multi-recipient scope is small. Its results are a targeted feasibility signal, not an estimate of a stable higher-order effect. The time-order sensitivity is an Eventnet interval-order check; a batch-history analysis that prevents same-time records from entering one another's covariates remains required before final interpretation. The observed group-model contrast also depends on the declared decay half-life, candidate eligibility rule, and selected 50-actor universe.

## Run provenance

- `collapsed_timestamp_footprints_seed_20261030`: Eventnet seed `20261030`; requested controls `100`; choice sets `2,345`.
- `descending_order_seed_20261030`: Eventnet seed `20261030`; requested controls `100`; choice sets `5,231`.
- `primary_ascending_seed_20261030`: Eventnet seed `20261030`; requested controls `100`; choice sets `5,231`.
- `sampling_seed_20261031`: Eventnet seed `20261031`; requested controls `100`; choice sets `5,231`.
