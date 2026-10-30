# Paper 2 RHEM source notes

## Lerner and Lomi 2023

- Source: https://academic.oup.com/jrsssa/article/186/3/577/6998599
- Title: *Relational hyperevent models for polyadic interaction networks*.
- Retrieved: 2026-10-30.
- Verified methodological points:
  - A relational hyperevent model specifies counting-process intensities for directed polyadic events consisting of a sender and a receiver set. Covariates may be actor attributes or functions of the event history and need not decompose into dyadic sender--receiver contributions.
  - The full RHEM partial likelihood sums over candidate receiver subsets. For nontrivial actor sets this risk set is exponentially large.
  - The paper proposes case--control sampling of non-events to obtain a tractable sampled-risk-set partial likelihood. It notes limitations of uniform sampling for sparse higher-order statistics and identifies stratified sampling or MCMC alternatives as possible extensions.
  - The publisher page links the empirical data, software, scripts, and a tutorial through the Eventnet wiki.

## Eventnet software

- Source: https://github.com/juergenlerner/eventnet
- Title: Event network analyzer.
- Retrieved: 2026-10-30.
- Verified software points:
  - Eventnet supports both dyadic relational event models and relational hyperevent models in one Java JAR (version 1.0 or later; the repository identifies eventnet-1.3.jar).
  - It is GPL-3.0 licensed and requires Java 8 or later.
  - It can run from a fully specified XML configuration in non-GUI mode: `java -jar eventnet-x.y.jar <configuration_filename.xml>`.
  - The repository directs users to its wiki tutorials and RHEM-effects reference guide.

## Paper 2 implication

The existing Enron custodian event table has a UTC event time, a unique sender, and a receiver set. It is structurally compatible with an RHEM input after an explicit actor-universe, chronology/tie policy, risk-set/case-control policy, and event-history covariate specification are frozen. The project has now completed a first seeded sampled-risk-set conditional-likelihood feasibility analysis; this source note does not treat those initial fits as a completed batch-history or substantive-mechanism analysis.

## Directed multicast RHEM estimand and fitting contract

- Source: Eventnet directed multicast tutorial,
  https://github.com/juergenlerner/eventnet/wiki/Directed-RHEM-for-multicast-interaction-%28tutorial%29
  (retrieved 2026-10-30); Lerner and Lomi (2023), pp. 577--599.
- For a sender \(i\) and receiver set \(J\), the conditional-sender,
  conditional-size estimand ranks \(J\) against alternative receiver sets of
  the same cardinality for the observed sender. It is a receiver-set choice
  model, not a model for event timing, sender selection, or receiver-set size.
- Eventnet's `COND_SIZE_DHE_OBS` emits one observed event and sampled same-size
  non-events per choice set. The directed tutorial's configuration uses 100
  controls and supplies both sender-conditioned and sender-unconditioned
  observations. The completed initial analysis uses two fixed Eventnet XML
  seeds with 100 requested controls, plus an order and representation
  sensitivity. It remains a sampled-risk-set feasibility analysis.
- Eventnet exports covariate tables rather than an estimator. The documented
  workflow estimates RHEM parameters using `survival::coxph` with each unique
  event/choice-set interval as the matching stratum. The public tutorial has a
  code-block inconsistency, so the project evaluator must use the exported
  `EVENT_INTERVAL` field explicitly rather than copy that snippet unchanged.
- Same-time event ties are a first-order design choice. Eventnet's
  `EVENT_INTERVAL` implementation updates histories in an input order. The
  2023 Enron example had comparatively few ties and arbitrarily ordered them;
  that does not justify assuming this archive's much more numerous ties are
  harmless. The current Paper 2 evidence includes multiple within-time order
  variants but still requires a batch-history sensitivity before final
  interpretation.
