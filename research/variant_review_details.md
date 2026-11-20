# Ibagué — independent variant-pattern audit

**Date:** 20 November 2026. **Stage:** reproducible source-level research; nothing approved for production.

The current generator has not changed its source trip patterns, holiday rules or headway allocations in this work package. New script [`scripts/audit_variant_patterns.py`](../scripts/audit_variant_patterns.py) audits the original SHA-256-pinned university archive and reports only the pattern-level structure of routes **8, 28, 35, 48, 4/7, 29**. It runs under [`audit-variant-patterns.yml`](../.github/workflows/audit-variant-patterns.yml) and publishes QA only. The [variant rules CSV](variant_rules_2026.csv) is **evidence, not active GTFS schedule data**.

## Route 8: critical direction metadata anomaly

The prior [30-pattern GraphHopper research artifact](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44701165571) preserves the original ordered stop IDs. Independent comparison of the original visits shows:

| Pattern | `direction_id` | Stops | Likely overlapping family | Source terminal anomaly |
| --- | --- | ---: | --- | --- |
| `TRIP_R9` | `0` | 70 | A | none noted |
| `TRIP_R11` | `1` | 60 | A | terminal marker shares geographic direction A |
| `TRIP_R10` | `1` | 77 | B | last stop name mentions **route 37** |
| `TRIP_R12` | `1` | 75 | B | includes route 37 terminal marker before route 8 terminal |

- `R9`/`R11`: **49 identical exact stop IDs in the same visit order**.
- `R10`/`R12`: **61 identical exact stop IDs in the same visit order**.
- Across A and B: **zero exact common stop IDs** (they are on opposite boarding sides, though GraphHopper roads may closely overlap).
- The existing generator classifies R11 with three other direction-1 patterns and splits the direction-1 legal frequency **equally among three templates**. That is an **unverified allocation** because R11 shares most of its actual stop identity/order with R9.
- We cannot yet determine if each pair is a real parallel variant or a full-trip / short-turn, or if the source mislabeled some terminal records. **Do not forcibly change direction_id or frequency distribution** on stop overlap alone.

The road-following candidate geometry produced by GraphHopper is not proof that the official [2026-10 route-8 poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-8-scaled.png)'s diversion via Calle 100 is included. The initial GH routing used no verified official via points.

## Route 48: extremely uneven source directions

The existing GH manifest has only **17 stop visits in source `TRIP_R53`** and **85 in `TRIP_R54`** (its route candidates are approximately 13.4 km and 26.4 km, respectively). This is not proof of an independent Juntas variant: the original trips may simply have incomplete stop listings or a partial leg. The Sunday/holiday **all to Juntas** rule, the weekday/Saturday **every third** rule, and the specified **05:00 and 05:40 departures from Juntas** remain separate operating instructions. Source: [Resolución 005549](https://ibague.gov.co/portal/admin/archivos/normatividad/2026/69845-RES-20261009145629.pdf), pp. 7–8.

## Route 35: Cay

The official [route-35 poster](https://transmusical.gov.co/wp-content/uploads/2026/06/Ruta-35-scaled.jpg) gives a **one-in-three** extension to vereda Cay. The pinned upstream has two patterns, but those do not identify a verified normal-versus-Cay branch pair. Unlike route 48, the day-type implementation scope requires further original poster review. The parser's report records the actual two source-pattern termini for use in that determination.

## Route 28: Caiké

The [October new-route poster](https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-28-scaled.png) and [independent park announcement](https://caike.com.co/la-ruta-28-ahora-llega-hasta-la-puerta-del-parque-caike/) support direct entrance access; this may be the revised standard alignment, **not** a separately scheduled alternative. Additional weekend/holiday departures are mentioned in official regulation, but their exact departure times are not yet supported. No synthetic trips.

## Work to close each case

1. Route 8: inspect four official-route segments and stop endpoints on the October map; resolve the direction mislabel and distinguish partial trips from actual variants **before** changing interleaving.
2. Route 48: match Juntas extension and departure origin to actual sequence/shape; confirm the conditional feeder status, then implement dispatch selection without doubling route frequency.
3. Route 35: identify the divergence to Cay, its physical stops and exact day scope, then model one-in-three as a branch allocation.
4. Route 28: validate stop near park entrance, return side and whether direct access is universal; only add extra weekend departures when evidenced.
5. Keep 4/7→7 identity and 29 terminal change as separate variant-adjacent publication gates.

Run this analysis independently of costly GraphHopper routing. Its data are derived from the existing pinned source, and no map or stop data are redistributed in the repository.

## Reproduced source-pattern audit — successful Actions run

[GitHub Actions run 44708507040](https://github.com/ColombiaTransit/Gtfs-ibaque/actions/runs/44708507040) completed successfully. Its short-lived `ibague-variant-source-audit-qa` artifact contains the original-pinned source's `source_variant_report.json`: source pattern IDs, direction labels, first/last source stops, shared ordered stop IDs, and warnings for terminal labels of other routes. The *unlicensed source ZIP itself* is not redistributed.

| Route | Source pattern A | Source pattern B | Confirmed source issue |
| --- | --- | --- | --- |
| 8 | `R9` 70 + `R11` 60 stops (49 shared, original directions 0/1) | `R10` 77 + `R12` 75 stops (61 shared, both direction 1) | 2 same-order stop families, 1 direction metadata mismatch; variant service remains unknown |
| 28 | `R37`: 34 stops | `R38`: 52 stops | Not identifiable as separate Caiké timetable variants |
| 35 | `R45`: 37 stops | `R46`: 34 stops | Normal/extended Cay branch not separately present as confirmed pattern |
| 48 | `R53`: 17 stops | `R54`: 85 stops | Incomplete/asymmetric source patterns: no supported normal-versus-Juntas assignment |
| 4/7 | `R5`: 70 stops | `R6`: 32 stops | Direction asymmetry; separate 4 and 7 not reconciled |
| 29 | `R39`: 5 stops | `R40`: 44 stops | Severe unequal coverage; do not treat as two fully symmetric terminal services |

**Terminal-name caution:** Some source patterns include synthetic or shared stops with another route number in their name. In route 8, the `R10` final stop is labeled `Terminal Inicio - Ruta 37 Ida` and `R12` also visits route-37 terminal markers; this is a *source stop labeling/cross-route issue to inspect*, not proof of a bus route transfer, a valid terminal, or a third independent variant. Avoid deleting or renaming these stop records without direction/geometry evidence.

**Operational conclusion unchanged:** no version of `build_gtfs.py` has been authorized to change trip assignments or headways from these source-pattern similarities alone. All operational variant checks remain open. The automated audit can be rerun via [workflow](../.github/workflows/audit-variant-patterns.yml), without repeating the 182 GraphHopper routing queries.
