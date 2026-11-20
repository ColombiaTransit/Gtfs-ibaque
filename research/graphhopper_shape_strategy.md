# GraphHopper / OSM research routing of Ibagué's 14 changed routes

**Implementation:** [`scripts/route_changed_shapes_graphhopper.py`](../scripts/route_changed_shapes_graphhopper.py), reproducible [review workflow](../.github/workflows/review-october-graphhopper-shapes.yml).

This **does not replace any GTFS shapes** and does **not prove** that a route is correct after the 19 October 2026 municipal modification. Read the [route change register](route_changes_2026_10_19.csv). The municipality's official 2026 October route posters are the itinerary authority; the self-hosted ColombiaTransit GraphHopper server runs its imported **OpenStreetMap** road network with the **`bus` profile**. GraphHopper finds a traversable road alignment between known waypoints, not a municipal bus itinerary or authoritative stop sequence.

## Routing sequence

1. Download the **SHA-256 pinned May 2026 original source GTFS**. Preserve the original route, trip, stop and geometry IDs. Restrict the run to routes 1, 2, 7, 8, 9, 15, 19, 21, 28, 29, 37, 40, 48 and 50. Historical route `4/7` is **mapped to label 7 only for research review**; it is *not* renamed in production.
2. Extract each source **trip pattern and ordered stop sequence**. There are 30 source patterns across the fourteen routes (four on route 8). Export `route_waypoint_review_manifest.json` for manual examination.
3. POST ordered `[lon, lat]` waypoints to the existing private self-hosted `GRAPHHOPPER_URL` using its `bus` profile and GeoJSON output (`points_encoded=false`). Chunk the route into overlapping 12-waypoint requests; retain all returned road vertices rather than straight-lining the stops. Browser-like headers and optional Cloudflare Access credentials match the approach already used in `gtfs-barranquilla-urbanas`.
4. The first pass is **stop-only research routing**, not a legally verified shape. For an official change such as route 8 via Calle 100, or route 50 returning through La Tobogán, update the **relevant direction's** manifest with explicitly reviewed **official via waypoints**. Each via requires `after_stop_sequence`, `point_lon_lat`, `approved: true` and the October official map URL in `official_source_url`. When routing, these vias are inserted in stop order.
5. Evaluate GraphHopper route success, continuity across chunks, candidate stop-to-road distances and potential missing new detours; visually compare candidate lines to the October official route poster and current OSM road network. The script preserves status `ROAD_CANDIDATE_ONLY_OFFICIAL_ITINERARY_UNVERIFIED` even when there are no stop offset warnings.
6. Candidate outputs are `candidate_road_shapes_RESEARCH_ONLY.geojson`, `pattern_route_qa.json`, and `candidate_shapes_NOT_GTFS.txt`. They are research artifacts, **not an updated GTFS feed**, and none is auto-imported by `scripts/build_gtfs.py`. Promotion requires reviewing the official itineraries and stop sequences and then an independent MobilityData validation.

## Workflow

In GitHub Actions select **Ibagué — OSM GraphHopper changed-route shape candidates**. Default pilot: `8,37,50` and 8 patterns. `route_labels=all`, `max_patterns=30` covers the full fourteen-route inventory when ready.

- Uses ColombiaTransit organization variable **`GRAPHHOPPER_URL`** and optional **`GRAPHHOPPER_PROFILE`** (`bus` by default), and optional Cloudflare Access secrets **`CF_ACCESS_CLIENT_ID`** / **`CF_ACCESS_CLIENT_SECRET`**. The script does not print the private base URL or credentials.
- With no GraphHopper URL, still builds the stop sequence/waypoint manifest and emits a warning. It cannot pretend that road candidates were generated.
- Push-triggered pilot and optional manual runs retain research outputs for up to 7 days, **without updating the generator or creating a public GTFS release**.

## Review priorities

- **First:** route 8 (Calle 100 instead of Calle 108, four patterns); route 37 (inbound via Calle 15 instead of Calle 16); route 50 (**return direction only**, La Tobogán–Calle 42–Guabinal).
- **Then:** local changes on 2, 19, 21, 40; major extensions/terminal changes on 1, 7, 9, 15, 28, 29; route 48 urban corridor and Juntas branching.
- A stop-only candidate can still choose the **old street** where the official detour does not include a stop. Do **not** promote solely because its stops snap closely to the road. For loops, review both first/last stops and the direction of travel. New official stops cannot be invented by GraphHopper.
- GraphHopper road access depends on its imported OSM snapshot (date may differ from the municipality's change date) and bus profile; public OSM can be incomplete or outdated.

Source attribution: © OpenStreetMap contributors (ODbL). Generated derivatives need review of source licensing and attribution before public redistribution. The source University's GTFS also lacks explicit redistribution permission in its pinned repository.
