# Official sources for Senate co-sponsorship benchmark and Network Science submission

## Legislative source

The U.S. Government Publishing Office (GPO) Bill Status Bulk Data Repository makes machine-readable XML available for the 108th through 119th Congresses. It provides a stable, official source for the completed 118th Congress Senate measure audit.

Congress.gov directs developers to its API and to the GPO Bill Status bulk-data repository. It identifies the Bill Status XML user guide as the detailed source schema documentation.

The Bill Status XML guide documents the fields needed for the proposed record construction:

- `sponsors/item/identifiers/bioguideId` for sponsor identity;
- `cosponsors/item/identifiers/bioguideId` for co-sponsor identity;
- `cosponsors/item/isOriginalCosponsor` for original co-sponsor status;
- `cosponsors/item/sponsorshipDate` and optional `sponsorshipWithdrawnDate`; and
- `introducedDate` for the measure introduction date.

The new pipeline will save each acquired archive URL, SHA-256 checksum, schema policy, and filtering account in its audit metadata. It will use no web scraping.

The Bill Status collection is a mutable latest snapshot even for completed Congresses. The acquisition driver therefore retains the XML records, source-directory JSON, retrieval time, file checksums, and a raw-tree checksum. The official directory contains individual XML records rather than a single archive.

For roster-policy auditing, the pipeline also snapshots the public, CC0
`unitedstates/congress-legislators` current and historical JSON files. Those files
are combined because the project documentation notes that the current/historical
split is administrative; together they expose Bioguide IDs and Senate term dates.
They are used only to define actor universes. Bill Status XML remains the event
record source.

## Senate procedure

The Congressional Research Service explains that a Senate bill has one sponsor but
may have any number of co-sponsors. It describes members submitted with a bill at
introduction as original co-sponsors. The benchmark consequently uses the explicit
`isOriginalCosponsor` field, rather than treating a same-day co-sponsorship date as
original. It retains an original co-sponsor even if the official record later lists
a withdrawal date: the target is the recorded coalition at introduction, not a
later membership roster.

## Journal and special-collection source

The Network Science Political Networks special collection explicitly welcomes relational-methods research on electoral and legislative processes, coalition formation, and representational relationships. Its stated deadline is 13 November 2026.

Network Science requires an anonymised main manuscript together with a separate title page containing the title, authors and affiliations, acknowledgements where relevant, competing-interest, funding, and data-availability statements. Its instructions permit LaTeX source files and state an ordinary article length of 20--40 pages, including footnotes and references.

## References

[1]: https://www.govinfo.gov/bulkdata/BILLSTATUS "GPO Bill Status bulk data repository"

[2]: https://www.congress.gov/help/using-data-offsite "Congress.gov guidance for developers using data offsite"

[3]: https://github.com/usgpo/bill-status/blob/main/BILLSTATUS-XML_User_User-Guide.md "Bill Status XML user guide"

[4]: https://github.com/unitedstates/congress-legislators "Congress-legislators public roster repository"

[5]: https://www.congress.gov/crs_external_products/RS/HTML/98-279.web.html "Sponsorship and Cosponsorship of Senate Bills"

[6]: https://www.cambridge.org/core/journals/network-science/announcements/call-for-papers/call-for-papers-political-networks-theory-methods-and-applications "Network Science Political Networks call for papers"

[7]: https://www.cambridge.org/core/journals/network-science/information/author-instructions/preparing-your-materials "Network Science preparing your materials"
