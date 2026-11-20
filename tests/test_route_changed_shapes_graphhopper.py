"""Offline tests: route selection, OSM API behavior, reviewed waypoints, QA status."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ibague_gh', ROOT/'scripts/route_changed_shapes_graphhopper.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    return {"routes.txt": [
        {"route_id":"20","route_short_name":"RUTA 4/7"},
        {"route_id":"27","route_short_name":"RUTA 8"}],
        "trips.txt": [
        {"route_id":"20","trip_id":"SRC7","shape_id":"SH7","trip_headsign":"Centro"},
        {"route_id":"27","trip_id":"SRC8","shape_id":"SH8","trip_headsign":"Otra"}],
        "stops.txt": [
        {"stop_id":"A","stop_lon":"-75.22","stop_lat":"4.44","stop_name":"A"},
        {"stop_id":"B","stop_lon":"-75.21","stop_lat":"4.45","stop_name":"B"},
        {"stop_id":"C","stop_lon":"-75.20","stop_lat":"4.46","stop_name":"C"}],
        "stop_times.txt": [
        {"trip_id":"SRC7","stop_id":"A","stop_sequence":"1"},
        {"trip_id":"SRC7","stop_id":"B","stop_sequence":"2"},
        {"trip_id":"SRC8","stop_id":"B","stop_sequence":"1"},
        {"trip_id":"SRC8","stop_id":"C","stop_sequence":"2"}],
        "shapes.txt": []}


class FakeHopper:
    def __init__(self):
        self.sent = []
    def check_bus_profile(self):
        return {"profile": "bus", "osm_data_date": "unknown"}
    def route(self, points):
        self.sent.append(points)
        return {"coordinates": points, "distance_m": 2000}


class TestIbaguéOSMShapes(unittest.TestCase):
    def test_legacy_4_7_maps_to_official_7_only_for_review(self):
        data = mod.manifest(fixture(), {"7", "8"})
        self.assertEqual([x['route'] for x in data['patterns']], ['7', '8'])
        self.assertEqual([x['source_trip_id'] for x in data['patterns']], ['SRC7', 'SRC8'])
        self.assertFalse(any(x['official_map_reviewed'] for x in data['patterns']))
        self.assertEqual(data['patterns'][0]['source_shape_id'], 'SH7')

    def test_reject_invalid_selection(self):
        with self.assertRaises(ValueError):
            mod.selected_labels('15,15')
        with self.assertRaises(ValueError):
            mod.selected_labels('21,22')
        self.assertEqual(len(mod.selected_labels('all')), 14)

    def test_reviewed_vias_require_approval_source_and_sequence(self):
        pattern = mod.manifest(fixture(), {'7'})['patterns'][0]
        via = {"after_stop_sequence":1, "point_lon_lat":[-75.214,4.445],
               "official_source_url":"https://transmusical.gov.co/rutas/", "approved": True}
        pattern['reviewed_official_vias'] = [via]
        self.assertEqual(len(mod.insert_reviewed_vias(pattern)), 3)
        pattern['reviewed_official_vias'][0]['approved'] = False
        with self.assertRaises(ValueError):
            mod.insert_reviewed_vias(pattern)
        pattern['reviewed_official_vias'][0]['approved'] = True
        pattern['reviewed_official_vias'][0]['after_stop_sequence'] = 999
        with self.assertRaises(ValueError):
            mod.insert_reviewed_vias(pattern)

    def test_graphhopper_endpoint_and_coordinates(self):
        self.assertEqual(mod.normalize_endpoint('https://example.org/router/route'), 'https://example.org/router')
        self.assertTrue(mod.valid_xy([-75.2,4.4]))
        self.assertFalse(mod.valid_xy([4.4,-75.2]))
        self.assertFalse(mod.valid_xy([-73,4.4]))

    def test_generate_candidate_without_promotion(self):
        data = mod.manifest(fixture(), {'7','8'})
        gh = FakeHopper()
        with tempfile.TemporaryDirectory() as t:
            dest = Path(t)
            report = mod.create_outputs(data, gh, dest)
            self.assertEqual(report['successful_graphhopper_candidates'],2)
            self.assertEqual(report['failed_patterns'],0)
            self.assertTrue(report['source_gtfs_unchanged'])
            self.assertFalse((dest/'shapes.txt').exists())
            geo = json.loads((dest/'candidate_road_shapes_RESEARCH_ONLY.geojson').read_text())
            self.assertEqual(geo['metadata']['shape_id_replacements_committed'],0)
            self.assertEqual(len(gh.sent), 2)
            self.assertEqual(geo['features'][0]['properties']['status'],
                             'ROAD_CANDIDATE_ONLY_OFFICIAL_ITINERARY_UNVERIFIED')
            self.assertTrue((dest/'candidate_shapes_NOT_GTFS.txt').exists())

    def test_chunked_route_continuity_and_stop_offset(self):
        p = mod.manifest(fixture(), {'7'})['patterns'][0]
        # Three source stop visits with one reviewed via to force >2-point chunking.
        p['reviewed_official_vias']=[{"after_stop_sequence":1,"point_lon_lat":[-75.214,4.445],
                                    "official_source_url":"https://transmusical.gov.co/rutas/","approved":True}]
        gh=FakeHopper()
        out=mod.route_pattern(p,gh,chunk_size=2)
        self.assertEqual(out['queries'],2)
        self.assertEqual(out['stops_over_100m'],0)

if __name__=='__main__':
    unittest.main()
