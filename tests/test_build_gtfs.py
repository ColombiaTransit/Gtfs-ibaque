"""Offline generator tests; no redistribution of third-party upstream ZIP."""
import csv
import datetime as dt
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_gtfs import (build, clock_segments, fmt, hm, service_calendar, template_offsets, write_zip)


def legal(route="1"):
    return [{"route": route,
             "weekday_service_hours": "05:00-21:30", "saturday_service_hours": "05:00-21:30",
             "sunday_holiday_service_hours": "05:30-21:00",
             "weekday_peak_hp_min": "6", "weekday_valley_hv_min": "9", "weekday_night_noc_min": "12",
             "saturday_peak_hp_min": "7", "saturday_valley_hv_min": "10", "saturday_night_noc_min": "13",
             "sunday_holiday_min": "14", "source_url": "official-test-url"}]


def source(variants=1):
    trips = []
    times = []
    for i in range(variants):
        tid = f"SRC_{i}"
        trips.append({"trip_id": tid, "route_id": "1", "service_id": "OLD", "direction_id": "0",
                      "trip_headsign": "Centro", "shape_id": "SH1"})
        times += [{"trip_id": tid, "stop_id": "1", "stop_sequence": "1", "arrival_time": "05:00:00",
                   "departure_time": "05:00:00", "shape_dist_traveled": "0"},
                  {"trip_id": tid, "stop_id": "2", "stop_sequence": "2", "arrival_time": "05:08:00",
                   "departure_time": "05:08:00", "shape_dist_traveled": "5"}]
    return {"agency.txt": [{"agency_id": "a", "agency_name": "Transmusical", "agency_url": "https://example.org",
                             "agency_timezone": "America/Bogota"}],
            "routes.txt": [{"route_id": "1", "agency_id": "a", "route_short_name": "RUTA 1",
                            "route_long_name": "Centro", "route_type": "3"}],
            "trips.txt": trips,
            "stops.txt": [{"stop_id": "1", "stop_name": "Marcador De Local Sem Titulo", "stop_lat": "4.0", "stop_lon": "-75.0"},
                          {"stop_id": "2", "stop_name": "Terminal", "stop_lat": "4.01", "stop_lon": "-75.01"}],
            "stop_times.txt": times,
            "shapes.txt": [{"shape_id": "SH1", "shape_pt_lat": "4.0", "shape_pt_lon": "-75.0", "shape_pt_sequence": "1"},
                           {"shape_id": "SH1", "shape_pt_lat": "4.01", "shape_pt_lon": "-75.01", "shape_pt_sequence": "2"}]}


def parse(blob):
    return list(csv.DictReader(io.StringIO(blob.decode("utf-8"))))


class TestGenerator(unittest.TestCase):
    def test_segments_clip_legal_spans(self):
        out = clock_segments("1", "WK", "05:30-20:30")
        self.assertEqual(out[0], (hm("05:30"), hm("06:00"), "NOC"))
        self.assertEqual(out[-1], (hm("19:30"), hm("20:30"), "NOC"))
        self.assertEqual(clock_segments("1", "SU", "05:30-20:30"), [(hm("05:30"), hm("20:30"), "FLAT")])

    def test_route_28_does_not_guess_unverified_evening(self):
        periods = clock_segments("28", "WK", "05:00-20:00")
        self.assertIn((hm("16:00"), hm("18:00"), "HP"), periods)
        self.assertFalse(any(a < hm("19:30") and b > hm("18:00") for a, b, _ in periods))

    def test_offset_normalization_and_shape_distance_removed(self):
        normalized, reason = template_offsets(source()["stop_times.txt"])
        self.assertIsNone(reason)
        self.assertEqual(normalized[0]["arrival_time"], "00:00:00")
        self.assertEqual(normalized[1]["arrival_time"], "00:08:00")
        self.assertNotIn("shape_dist_traveled", normalized[0])

    def test_calendar_holiday_monday_and_saturday(self):
        start = dt.date(2026, 11, 16)
        cal, overrides = service_calendar(start, 7, {start, dt.date(2026, 11, 21), dt.date(2026, 11, 22)})
        self.assertEqual(len(cal), 3)
        self.assertEqual(len(overrides), 4)
        self.assertEqual([x["service_id"] for x in overrides], ["CT_WK", "CT_SU", "CT_SA", "CT_SU"])

    def test_equal_split_does_not_double_frequency(self):
        tables, report = build(source(2), legal(), dt.date(2026, 11, 20), 30, set())
        rows = parse(tables["frequencies.txt"])
        peak = [r for r in rows if r["trip_id"].startswith("CT_WK_") and r["start_time"][:5] in ("06:00", "06:06")]
        self.assertEqual(len(peak), 2)
        self.assertEqual({r["headway_secs"] for r in peak}, {str(6 * 2 * 60)})
        self.assertEqual({r["start_time"] for r in peak}, {"06:00:00", "06:06:00"})
        self.assertEqual(report["covered_routes"], 1)
        self.assertEqual(parse(tables["feed_info.txt"])[0]["feed_lang"], "es")
        self.assertFalse(report["publication_ready"])
        self.assertEqual(report["remaining_unnamed_stops"], 1)
        self.assertEqual(len(parse(tables["trips.txt"])), 6)
        self.assertEqual(len(parse(tables["stop_times.txt"])), 12)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"preview.zip"
            write_zip(path, tables)
            self.assertTrue(path.is_file())

    def test_zero_night_frequency_suppresses_route_29_night(self):
        s = source()
        s["routes.txt"][0]["route_short_name"] = "RUTA 29"
        values = legal("29")
        values[0]["weekday_night_noc_min"] = "0"
        values[0]["saturday_night_noc_min"] = "0"
        tables, _ = build(s, values, dt.date(2026, 11, 20), 30, set())
        weekday = [r for r in parse(tables["frequencies.txt"]) if r["trip_id"].startswith("CT_WK_")]
        self.assertFalse(any(hm(r["start_time"]) < hm("06:00") or hm(r["start_time"]) >= hm("19:30") for r in weekday))

    def test_unverified_stop_override_rejected(self):
        from build_gtfs import approved_stop_names
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"stops.csv"
            p.write_text("stop_id,stop_name,source_url,approved\n1,Calle 12,,yes\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                approved_stop_names(source()["stops.txt"], p)

    def test_bad_trip_pattern_not_silently_repaired(self):
        s = source()
        s["stop_times.txt"][1]["arrival_time"] = "04:00:00"
        with self.assertRaisesRegex(ValueError, "All source trip patterns were excluded"):
            build(s, legal(), dt.date(2026, 11, 20), 30, set())


if __name__ == "__main__":
    unittest.main()
