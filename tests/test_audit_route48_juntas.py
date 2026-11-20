"""Offline guardrails for route 48 branch QA, no external network dependency."""
import sys
import unittest
from pathlib import Path
from shapely.geometry import LineString
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_route48_juntas import (extract_osm_features,find_route48,landmark_rows,
                                  overpass_query,sample_overlap,verify_landmark_order)

class TestRoute48(unittest.TestCase):
    def test_exact_source_patterns_only(self):
        f=lambda trip: {"properties":{"route":"48","source_trip_id":trip},"geometry":{"type":"LineString","coordinates":[[-75.31,4.52],[-75.32,4.55]]}}
        self.assertEqual(len(find_route48([f('TRIP_R53'),f('TRIP_R54')],'test')),2)
        with self.assertRaises(ValueError):find_route48([f('TRIP_R53')],'test')
        with self.assertRaises(ValueError):find_route48([f('TRIP_R53'),f('TRIP_R53')],'test')
    def test_landmark_order(self):
        rows=[{'source_trip_id':trip,'reference_name':name,'projected_branch_distance_m':i}
          for trip,names in [('TRIP_R53',('Villa Restrepo village','Iguaima location','Juntas village')),
                             ('TRIP_R54',('Juntas village','Iguaima location','Villa Restrepo village'))]
          for i,name in enumerate(names)]
        self.assertEqual(len(verify_landmark_order(rows)),2)
        rows[2]['projected_branch_distance_m']=-1
        with self.assertRaises(ValueError):verify_landmark_order(rows)
    def test_osm_platforms_not_official(self):
        data={'elements':[{'type':'node','id':45,'lat':4.55,'lon':-75.32,
                          'tags':{'highway':'bus_stop','name':'Juntas candidate'}},
                         {'type':'node','id':90,'lat':9.01,'lon':-73.0,'tags':{'highway':'bus_stop'}}]}
        r=extract_osm_features(data)
        self.assertEqual(len(r),1)
        self.assertEqual(r[0]['route_48_operator_confirmed'],'no')
    def test_no_distance_shortcut(self):
        a=LineString([(0,0),(200,0)])
        b=LineString([(0,20),(200,20)])
        self.assertEqual(sample_overlap(a,b, every_m=20,tolerance_m=55),1)
    def test_narrow_bus_stop_overpass_query(self):
        query=overpass_query()
        self.assertIn('4.502,-75.341,4.563,-75.295',query)
        self.assertIn('bus_stop',query)
        self.assertNotIn('way["highway"]',query)

if __name__=='__main__': unittest.main()
