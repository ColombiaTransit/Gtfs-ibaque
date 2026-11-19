# Final review of HP/HV/NOC amendment evidence — 19 November 2026

## Scope

Target: verify whether **Resolución 00197 of 30 April 2024** and **Resolución 1595 of 27 March 2026** modify the time-of-day definitions of HP (peak), HV (valley), or NOC (night) established in the published transcription of **Resolución 000370 of 2 May 2022**. This review **does not** re-investigate the already validated October 2026 route headway values.

## Actual PDFs inspected

| Document | Primary PDF | Inspection | Outcome |
| --- | --- | --- | --- |
| **004951**, 15 Sep 2026 | [Official municipality scan](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/70041-RES-20261113170945.pdf) | **16 pages**; article 4 on **p. 16 visually inspected** | Repeals contradictory provisions; otherwise preserves 000370/2022, 000898/2022, 00152/2024, 00197/2024 and **1595 of 27 March 2026**. It does **not** reproduce an HP/HV/NOC cutover timetable on p. 16. |
| **005549**, 9 Oct 2026 | [Official municipality scan](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf) | **13 pages**; Article 3 tables **pp. 9–13** and Article 4 **p. 13 visually inspected** | Repeals 005459/2026, replaces articles 1 and 3 of 004951/2026, prescribes the controlling **route headways** but **not** HP/HV/NOC cutover clock times; Article 4 preserves all other non-amended provisions of 004951. |
| **00197**, 30 Apr 2024 | **Original PDF not retrieved** | References in official 004951/2026 article 4 and [contemporaneous news quoting SETP](https://caracol.com.co/2024/05/03/conozca-los-cambios-en-el-recorrido-de-algunas-rutas-de-bus-en-ibague/) | Cannot certify whether its definitions amended HP/HV/NOC because its actual pages were **not inspected**. |
| **1595**, 27 Mar 2026 | **Original PDF not retrieved** | Verifiable mention of this exact number/date in official 004951/2026 article 4 | Cannot certify whether it amends HP/HV/NOC because its actual pages were **not inspected**. |

## Retrieval check

Searches performed on the official [municipal Gaceta index](https://ibague.gov.co/portal/seccion/normatividad/index.php), its archived legacy index, the [TransMusical normativity page](https://transmusical.gov.co/normatividad/), official SETP site search, web indexing and currently available user source files yielded **no authenticated document URLs** for the **two missing original acts**. Exact-number queries in Gaceta for 00197/2024 and 1595/2026 had zero matching results. In 2024 a search for `197` returned an **unrelated decree**, not the bus-service resolution. Do **not** confuse this with evidence of absence of the acts.

Relevant GitHub Actions evidence:
- [Municipal official-number and date search, run 44604306480](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44604306480).
- [Legacy municipality and TransMusical indexes, run 44604740385](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44604740385).
- [Original 004951 & 005549 PDFs + OCR archive, run 44600046626](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44600046626).

## Legal-status conclusion

**Documented:** The 2022 clock categories are *not directly repealed* by the two original **2026 PDFs inspected**; 004951/2026 explicitly retains earlier compatible regulations, and 005549/2026 explicitly retains the non-amended provisions of 004951.

**Not demonstrated:** That neither 00197/2024 nor 1595/2026 modified those categories. A mere carry-forward reference does not establish that every provision of 000370/2022 remains unchanged. Consequently, **do not label the original 2022 cutovers “verified legally effective in 2026”**.

### Historical working-clock profile (not a certified current schedule)

See [`clock_blocks_2022.csv`](clock_blocks_2022.csv) and [`clock_blocks_audit.md`](clock_blocks_audit.md):
- 04:40–06:00 NOC *tentative* (historical document allows demand-dependent alternatives).
- 06:00–08:30 HP; 08:30–11:30 HV; 11:30–14:30 HP; 14:30–17:00 HV *tentative* (historical text conflict at 15:00); 17:00–19:30 HP; 19:30–22:00 NOC.
- Historical route **28** exception: HP **16:00–18:00**; the route's remaining 18:00–19:30 categorization needs explicit handling. 
- The current 2026 legal table supplies **separate weekday, Saturday and Sunday/holiday headways**. The precise cutover blocks for Saturdays remain unverified.

## Practical closure for the feed

1. **Close the official-frequency acquisition stage.** All **30 routes × 7 frequency values** are already stored in [`official_resolution_005549_frequencies.csv`](official_resolution_005549_frequencies.csv).
2. **Close this PDF discovery pass without claiming nonexistent verification.** The two older acts remain unavailable, so keep a single open archival dependency, not a repeated scrape/search task.
3. In downstream GTFS generation use the 2022 time profile **only if explicitly selected as a provisional reconstruction assumption** with provenance. Do not silently promote it to a legal cutoff or assign route-specific exceptions by guess.
4. Keep existing official route-wide span conflicts, route 4/7 vs 4+7 and route 39, and modified geometry in separate registers; avoid opening those issues again as part of clock-block research.
5. Do not publish an unqualified definitive service calendar solely from this conditional profile. Before public release disclose the provisional period mapping or obtain source clarification from Secretaría de Movilidad / SETP.

**Final classification:** official headways **verified**; clock-period continuity **supported but not proved**; PDF search **closed with source gap explicitly recorded**.
