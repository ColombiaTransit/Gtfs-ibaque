# Official frequency investigation — Ibagué

**Status as of 19 November 2026: all 30 route frequencies found in the official 2026 act. Moovit is excluded.**

## Governing source

[Resolución 005549 — Secretaría de Movilidad de Ibagué, 9 October 2026](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf), **article 3, scanned pages 9–13**, directly supplies all route headways.

- Repeals Resolución **005459** (6 October 2026).
- Partially modifies Resolución **004951** (15 September 2026), principally its **articles 1 and 3**.
- The earlier 004951 PDF is [available at the municipality archive](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/70041-RES-20261113170945.pdf); its formerly published table is **not** the controlling table after article 3 was replaced by 005549.
- Official original PDFs and OCR text were downloaded by [GitHub Actions run 44600046626](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44600046626). The scanned tables were **visually re-read** (OCR alone is unreliable).

**Canonical data:** [`official_resolution_005549_frequencies.csv`](official_resolution_005549_frequencies.csv).  
**Detailed data interpretation / caveats:** [`official_frequency_2026.md`](official_frequency_2026.md).

## Coverage

- **30/30 upstream routes:** authoritative October 2026 frequency standards per peak, off-peak and nocturnal period on weekdays and Saturdays, plus each Sunday/holiday headway.
- **16/16 routes with missing entries in the upstream ZIP now have official candidate headways** (22, 23, 24, 28, 29, 31, 33, 35, 37, 40, 43, 48, 50, 53, 82, 90).
- These values are safe to register as source transcription. They are **not yet applied to GTFS**, as the actual clock boundaries for HP/HV/NOC still need primary-source verification, along with assignment to all directions and GTFS variants.
- Route 29's `FREC NOC = 0` means no night departures, not a zero-minute headway.

## Prior acts / remaining research

- **Resolución 000370 (2 May 2022):** a [university study](https://repositorio.unibague.edu.co/bitstreams/f24b40e5-97a5-4a39-99f4-65b95f08fe63/download) cites earlier standards for 8 routes; superseded for our registry by the October 2026 headway table. See [historical references](historical_official_frequency_standards.csv).
- **Resolución 00197 (30 April 2024):** formally reported in [contemporary coverage](https://www.ecosdelcombeima.com/ibague/nota-17707-atencion-conozca-los-cambios-en-las-rutas-de-buses-en-ibague), but the original PDF/annex is not retrieved.
- The 2026 Act 004951 (page 16, article 4) explicitly references 000370/2022, 000898/2022, 00152/2024, 00197/2024, and 1595/27 March 2026 as continuing unless contradicted. This is a clue for locating period boundary definitions, not authorization to copy older headways over a later table.
- A 2022 resolution [republished by CambioIn](https://www.cambioin.com/principal/los-cambios-profundos-que-tendra-el-transporte-urbano-en-ibague) gives provisional HP/HV/NOC clock blocks, but it is a secondary transcription, has inconsistent printed afternoon valley text, and has not been confirmed against a primary applicable 2026 act. See [caveats](official_frequency_2026.md).
- Four feeder posters, official route 39, and separately shown route 4 require independent inclusion/authorization checks.
- Site service-hours conflicts are recorded separately from headways; don't silently overwrite the official October 2026 table with older route posters.

## Source rule

Moovit has no role in the present frequency research. The legacy `frequency_candidates.csv` file is **deprecated secondary-source material** and must not be consumed by the generator. Use only the direct 2026 legal table and verified official service-day sources.
