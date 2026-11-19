# Ibagué clock-block research (HP / HV / NOC) — 19 November 2026

## Finding: historical definition exists, but current applicability still requires an amendment audit

The text of **Resolución 000370 of 2 May 2022** is reproduced in [CambioIn — Los cambios profundos que tendrá el transporte urbano en Ibagué](https://www.cambioin.com/principal/los-cambios-profundos-que-tendra-el-transporte-urbano-en-ibague). In its paragraph on frequency categories, it specifies these operating periods:

| Start | End | Category |
| --- | --- | --- |
| 04:40 | 06:00 | NOC (night, with demand-dependent exceptions) |
| 06:00 | 08:30 | HP (morning peak) |
| 08:30 | 11:30 | HV (valley) |
| 11:30 | 14:30 | HP (midday peak) |
| 14:30 | 17:00 | HV (valley; inconsistent source text) |
| 17:00 | 19:30 | HP (evening peak) |
| 19:30 | 22:00 | NOC (night) |

**Source ambiguity:** The reproduced running text says 14:30–15:00 for the afternoon valley, but the adjacent graphical schedule instead shows 14:30–17:00. The graphical schedule fits the 17:00 evening peak start. The 17:00 end is a *provisional interpretation*, not independently verified against the original scanned 2022 resolution.

**Explicit historical exceptions:**
1. **04:40–06:00** may use any of HP, HV, NOC frequencies depending on demand. Do not hard-code all routes to NOC without a documented assumption.
2. **Route 28:** afternoon peak is **16:00–18:00**, rather than the usual 17:00–19:30. The precise 18:00–19:30 classification for this route was not stated in the source transcription. Do not automatically treat it as HP or HV.

## Why the 2022 clock scheme may still apply to the 2026 frequency table

Two original official municipal 2026 resolutions were inspected as scanned PDFs:

- [**Resolución 004951**, 15 September 2026](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/70041-RES-20261113170945.pdf), **article 4, scanned PDF page 16**: provisions of 000370/2022, 000898/2022, 00152/2024, 00197/2024, 1595/27 March 2026 remain in force unless inconsistent with this resolution. The date/act number and carry-forward language were **visually checked on the actual page image**, not inferred from an article.
- [**Resolución 005549**, 9 October 2026](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf), **article 3, pp. 9–13**: updated official HP/HV/NOC **headway values**, but these pages do not independently define the cutover clock times. It also repeals 005459/2026 and partially modifies 004951. Its article 4 preserves unchanged provisions from 004951.

**Therefore:** There is a plausible, document-backed *continuity chain* from the 2022 clock categories to the October 2026 headways, **but not conclusive proof** that 2024 or early-2026 amendments did not modify their definitions. The original 000370/2022 and the relevant amendments (especially **00197/2024** and **1595/2026**, also 000898/2022 and 00152/2024) were not directly inspected for clock-cutoff changes.

The 2026 legal frequency table already supplies all route headways: see [official_resolution_005549_frequencies.csv](official_resolution_005549_frequencies.csv). **Do not use the obsolete 2022 frequency values themselves.**

## Practical generator policy

- Store this provisional profile separately in [clock_blocks_2022.csv](clock_blocks_2022.csv) with a status flag. Do not change canonical official 2026 data.
- The table provides three periods for **días ordinarios** and **días sábados**; the 2022 clock scheme is a proposed mapping for both until a subsequent act confirms day-specific cutovers.
- **Sunday and holidays** use one official route-level frequency and no HP/HV/NOC period mapping.
- Apply route-specific first/last service limits separately; a global 04:40–22:00 classification does **not** imply every route operates throughout that window.
- Apply the correct 2026 legal headway to each period, but block release of unreviewed route-28 evening hours and the demand-dependent early morning.
- Do not confuse passenger-bus HP/HV/NOC with Ibagué private-car **pico y placa** valley exemption hours; they are unrelated.

## Outstanding precise verification

1. Obtain the scanned official **000370 (2 May 2022)** to check the 14:30/15:00/17:00 conflict, exceptions and day-type scope.
2. Inspect **00197 of 30 April 2024** and **1595 of 27 March 2026** for later changes to HP/HV/NOC cutover hours.
3. Review **000898/2022** and **00152/2024** for service-hour changes.
4. If these later texts do not change the clock profiles, mark the period mapping as confirmed for 2026; otherwise add effective-dated overrides.
