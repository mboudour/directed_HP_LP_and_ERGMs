# Verified political-network sources for the Network Science manuscript

This note records citations verified on 25 October 2026 for the Network Science political-networks version of the directed LP/HP--ERGM benchmark. It is a source-selection record, not a substitute for the manuscript bibliography. Each source should be cited only for the scoped use described below.

## Legislative co-sponsorship and political-network framing

- Fowler, J. H. (2006). *Legislative cosponsorship networks in the US House and Senate*. **Social Networks, 28**(4), 454--465. https://doi.org/10.1016/j.socnet.2005.11.003. Use to motivate the sponsor--co-sponsor relation as a legislative network and to position projection-based analysis. A co-sponsorship tie is observable public support, not proof of a durable alliance.
- Talbert, J. C., & Potoski, M. (2002). *Setting the Legislative Agenda: The Dimensional Structure of Bill Cosponsoring and Floor Voting*. **The Journal of Politics, 64**(3), 864--891. https://doi.org/10.1111/0022-3816.00150. Use for the relationship between bill co-sponsoring and legislative policy-alignment structure.
- Zhang, Y., Friend, A. J., Traud, A. L., Porter, M. A., Fowler, J. H., & Mucha, P. J. (2008). *Community structure in Congressional cosponsorship networks*. **Physica A, 387**(7), 1705--1712. https://doi.org/10.1016/j.physa.2007.11.004. Use as a network-science precedent for community structure in congressional co-sponsorship.
- Aref, S., & Neal, Z. P. (2021). *Identifying hidden coalitions in the US House of Representatives by optimally partitioning signed networks based on generalized balance*. **Scientific Reports, 11**, 19939. https://doi.org/10.1038/s41598-021-98139-w. Use only when discussing signed political relations or coalition-identification extensions; it does not establish a result about unsigned co-sponsorship.

## ERGMs and political networks

- Hunter, D. R., Handcock, M. S., Butts, C. T., Goodreau, S. M., & Morris, M. (2008). *ergm: A Package to Fit, Simulate and Diagnose Exponential-Family Models for Networks*. **Journal of Statistical Software, 24**(3). https://doi.org/10.18637/jss.v024.i03. Core computational ERGM citation.
- Cranmer, S. J., & Desmarais, B. A. (2011). *Inferential Network Analysis with Exponential Random Graph Models*. **Political Analysis, 19**(1), 66--86. https://doi.org/10.1093/pan/mpq037. Use for political-science ERGM framing and inferential cautions.
- Scott, T. A. (2015). *Analyzing Policy Networks Using Valued Exponential Random Graph Models*. **Policy Studies Journal, 44**(2), 215--244. https://doi.org/10.1111/psj.12118. Use only when motivating valued policy-network extensions.
- Lee, Y., Lee, I. W., & Feiock, R. C. (2012). *Interorganizational Collaboration Networks in Economic Development Policy: An Exponential Random Graph Model Analysis*. **Policy Studies Journal, 40**(3), 547--573. https://doi.org/10.1111/j.1541-0072.2012.00464.x. Use as a policy-network ERGM application reference.

## Incomplete networks and link prediction

- Wu, Q., Zhang, Z., Ma, T., Waltz, J., Milton, D., & Chen, S. (2021). *Link predictions for incomplete network data with outcome misclassification*. **Statistical Medicine, 40**(6), 1519--1534. https://doi.org/10.1002/sim.8856. Use to distinguish latent/misclassified ties from confirmed nonedges.
- Zhao, Y., Wu, Y.-J., Levina, E., & Zhu, J. (2017). *Link Prediction for Partially Observed Networks*. **Journal of Computational and Graphical Statistics, 26**(3), 725--733. https://doi.org/10.1080/10618600.2017.1286243. Use for candidate ranking when absent dyads are not reliable negatives.
- Ghasemian, A., Hosseinmardi, H., Galstyan, A., Airoldi, E. M., & Clauset, A. (2020). *Stacking models for nearly optimal link prediction in complex networks*. **PNAS, 117**(38), 23393--23400. https://doi.org/10.1073/pnas.1914950117. Use for the network-dependence of predictor performance, not for a specific political result.
- Ribeiro, H. V., Alves, L. G. A., Martins, A. F., Lenzi, E. K., & Perc, M. (2018). *The dynamical structure of political corruption networks*. **Journal of Complex Networks, 6**(6), 989--1003. https://doi.org/10.1093/comnet/cny002. Use as a political-network prediction precedent while keeping forecasting separate from missing-data inference.

## Directed higher-order and event-level comparison literature

- Yadati, N., Nitin, V., Nimishakavi, M., Yadav, P., Louis, A., & Talukdar, P. (2020). *NHP: Neural Hypergraph Link Prediction*. In **CIKM '20**, 1705--1714. https://doi.org/10.1145/3340531.3411870. Cite only for directed hyperlink-prediction background when the manuscript needs an architecture reference; do not imply that the paper's method was reproduced here.
- Ma, Z., Zhao, W., & Yang, Z. (2024). *Directed Hypergraph Representation Learning for Link Prediction*. In **AISTATS 2024**, PMLR 238, 3268--3276. https://proceedings.mlr.press/v238/ma24b.html. Use for recent directed-hypergraph representation-learning background.
- Butts, C. T., Lomi, A., Snijders, T. A. B., & Stadtfeld, C. (2023). *Relational event models in network science*. **Network Science, 11**(2), 175--183. https://doi.org/10.1017/nws.2023.9. Use to distinguish time-ordered relational-event targets from static missingness.
- Lerner, J., & Lomi, A. (2023). *Relational hyperevent models for polyadic interaction networks*. **Journal of the Royal Statistical Society Series A, 186**(3), 577--600. https://doi.org/10.1093/jrsssa/qnac012. Use to position relational hyperevents as a distinct future forecasting benchmark rather than a replacement for this paper's static missingness target.

## Official source and venue records

- GovInfo Bill Status directory, 118th Congress, Senate bills: https://www.govinfo.gov/bulkdata/json/BILLSTATUS/118/s. The public directory provides individual Bill Status XML records and links.
- U.S. Government Publishing Office Bill Status XML User Guide: https://github.com/usgpo/bill-status/blob/main/BILLSTATUS-XML_User_User-Guide.md. Use for XML fields, including `bioguideId`, `isOriginalCosponsor`, sponsorship dates, and withdrawal dates.
- Congressional Research Service, *Sponsorship and Cosponsorship of Senate Bills*: https://www.congress.gov/crs_external_products/RS/HTML/98-279.web.html. Use for the one-sponsor/multiple-co-sponsor procedural distinction.
- Network Science, *Political Networks: Theory, Methods, and Applications* call: https://www.cambridge.org/core/journals/network-science/announcements/call-for-papers/call-for-papers-political-networks-theory-methods-and-applications. The call explicitly includes legislative processes, requires a double-blind main document and title page, and gives 13 November 2026 as the collection deadline.
