# Citation topic: formal concept analysis, Galois connections, and maximal bicliques

## Recommended sources

### [1] Ganter and Wille (1999)

**Bibliographic record:** Bernhard Ganter and Rudolf Wille. 1999. *Formal Concept Analysis: Mathematical Foundations*. Springer-Verlag, Berlin Heidelberg. DOI: [10.1007/978-3-642-59830-2](https://doi.org/10.1007/978-3-642-59830-2). Publisher record: [Springer](https://link.springer.com/book/10.1007/978-3-642-59830-2). The Springer record identifies the authors, first-edition year/copyright, publisher, DOI, and chapters **Order-theoretic Foundations** and **Concept Lattices of Contexts**; Crossref independently records the same title, authors, 1999 publication year, publisher, and DOI.

**What it supports in the manuscript:** Use this as the canonical textbook citation for the definitions and order-theoretic machinery of a formal context, derivation operators, formal concepts, and the concept lattice, including the fact that the construction is a lattice-theoretic treatment of object–attribute incidence data. It is the appropriate source for a careful statement that a binary incidence relation induces a Galois connection/closure operators and that the fixed points form formal concepts ordered as a concept lattice. It can also support terminology such as “formal concept analysis” and “concept lattice.”

**Claim boundary:** The book is a mathematical foundations text, not a source for directed-link prediction, missing-data mechanisms, ERGMs, MPLE, Enron/MathOverflow, or temporal forecasting. Do not cite it for empirical link-prediction performance or for a claim that formal concepts are native directed events. If the manuscript states the maximal-biclique equivalence explicitly, cite [2] for the formal-context construction and [3] for the bipartite-graph/maximal-biclique interpretation, rather than attributing a link-prediction result to this book.

### [2] Wille (1982)

**Bibliographic record:** Rudolf Wille. 1982. “Restructuring Lattice Theory: An Approach Based on Hierarchies of Concepts.” In Ivan Rival (ed.), *Ordered Sets*, NATO Advanced Study Institutes Series, vol. 83, pp. 445–470. Springer, Dordrecht. DOI: [10.1007/978-94-009-7798-3_15](https://doi.org/10.1007/978-94-009-7798-3_15). Publisher record: [Springer](https://link.springer.com/chapter/10.1007/978-94-009-7798-3_15). The publisher page gives the title, author, 1982 publication, pages, venue, and DOI, and its abstract explicitly defines a context `(G, M, I)`, the two derivation maps, their natural Galois connection, a concept `(A, B)` satisfying `A' = B` and `B' = A`, and the concept hierarchy.

**What it supports in the manuscript:** Use this as the original foundational source for the formal-context/Galois-connection formulation. In particular, it supports defining objects and attributes joined by a binary relation, defining the two antitone derivations, defining concepts as mutually closed extent–intent pairs, and ordering concepts by extent inclusion (equivalently reverse intent inclusion). This is the strongest citation for separating a formal concept extracted from an incidence relation from a native directed event in the observed network.

**Claim boundary:** Wille’s chapter does not study link prediction, missingness, ERGMs, MPLE, or the Enron/MathOverflow datasets. It should not be cited as evidence for predictive validity, a statistical model, or a temporal claim. Its formal context is an arbitrary binary relation; mapping a directed network to an object–attribute context is a manuscript modeling choice that must be stated explicitly.

### [3] Zhang et al. (2014)

**Bibliographic record:** Yun Zhang, Charles A. Phillips, Gary L. Rogers, Erich J. Baker, Elissa J. Chesler, and Michael A. Langston. 2014. “On finding bicliques in bipartite graphs: a novel algorithm and its application to the integration of diverse biological data types.” *BMC Bioinformatics* 15:110. DOI: [10.1186/1471-2105-15-110](https://doi.org/10.1186/1471-2105-15-110). Official full text and metadata: [PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC4038116/). The article record gives the title, authors, journal, date (15 April 2014), volume/article number, and DOI. Its background states that maximal-biclique enumeration was formulated in terms of rectangles, binary relations, and concept lattices; its abstract states that the algorithm produces all maximal bicliques in a bipartite graph.

**What it supports in the manuscript:** Use this for the graph-theoretic interpretation and computational vocabulary: a binary incidence matrix can be viewed as a bipartite graph, and a maximal biclique is a complete bipartite subgraph that cannot be enlarged while preserving completeness. In conjunction with [2]’s extent–intent fixed-point definition, this supports the manuscript’s precise statement that a formal concept corresponds to a maximal all-ones rectangle/maximal biclique of the associated bipartite incidence graph. It is also a suitable citation when describing maximal-biclique enumeration as a graph operation, without implying that it is a directed-link score.

**Claim boundary:** This is an algorithmic bioinformatics paper, not a source for the general FCA definitions, ERGM methodology, link-prediction evaluation, or missingness assumptions. It reports an enumeration algorithm and biological applications; it does not establish that a maximal biclique is a native directed event, nor that concept extraction forecasts future directed edges. The manuscript should not transfer its biological performance results to Enron or MathOverflow.

## Use in this manuscript

A defensible formulation is: “For an explicitly constructed bipartite incidence context, the derivation operators form a Galois connection and the mutually closed extent–intent pairs are formal concepts ordered in a concept lattice [1,2]. Equivalently, these concepts can be represented as maximal all-ones rectangles, or maximal bicliques, in the associated bipartite graph [2,3]. This formal-concept object is distinct from the observed directed event `(u,v)` used by native directed link prediction.” The last distinction is a manuscript interpretation grounded in the definitions; none of these sources supports claims about neural benchmarks, MCMC-derived joint L3 evidence, or full forecasting.

## Verification notes

The Springer and Crossref records were checked for [1]. The Springer chapter page was checked for [2], including the abstract’s explicit Galois-connection and concept definitions. The official PMC record was checked for [3], including bibliographic metadata, DOI, and the statements about maximal bicliques, binary relations, and concept lattices. No source was used to support claims outside its stated scope.
