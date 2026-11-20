"""Isolated route 8+branch source audit test; no outside network or original GTFS."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from review_route8_and_branches import review_route8, prepare_branch, ANCHORS


def mk(trip, direction, coords, common_ids):
    return {'route':'8','source_trip_id':trip,'source_direction_id':direction,
            'stop_visits':[{'stop_id':v,'stop_name':v,'point_lon_lat':xy}
                           for v,xy in zip(common_ids,coords)]}

class TestSourceReview(unittest.TestCase):
    def setUp(self):
        self.p=[
            mk('TRIP_R9','0',[[-75.15,4.43],[-75.16,4.43],[-75.20,4.44],[-75.25,4.45]],['east','a','b','west']),
            mk('TRIP_R11','1',[[-75.16,4.43],[-75.20,4.44],[-75.24,4.45]],['a','b','shortwest']),
            mk('TRIP_R10','1',[[-75.25,4.45],[-75.20,4.44],[-75.16,4.43],[-75.15,4.43]],['west2','c','d','east2']),
            mk('TRIP_R12','1',[[-75.24,4.45],[-75.20,4.44],[-75.16,4.43]],['shortwest2','c','d']),
        ]
    def test_direction_clustering_and_bad_code(self):
        d=review_route8(self.p)
        idx={x['source_trip_id']:x for x in d['source_trips']}
        self.assertEqual(idx['TRIP_R11']['poster_direction_label'],'IDA')
        self.assertTrue(idx['TRIP_R11']['direction_metadata_mismatch'])
        self.assertFalse(idx['TRIP_R10']['direction_metadata_mismatch'])
        self.assertTrue(idx['TRIP_R11']['candidate_west_shortening'])
        self.assertFalse(d['all_source_patterns_confirmed_current'])
    def test_wrong_course_rejected(self):
        x=self.p[1]['stop_visits']
        self.p[1]['stop_visits']=list(reversed(x))
        with self.assertRaises(ValueError):review_route8(self.p)
    def test_anchor_branch_direction_side(self):
        a=ANCHORS['35']['lon_lat']
        p={'route':'35','source_trip_id':'TRIP_R45','source_direction_id':'0',
           'stop_visits':[{'stop_id':'start','stop_name':'east','point_lon_lat':[-75.18,4.44]},
                          {'stop_id':'last','stop_name':'west','point_lon_lat':[-75.254,4.466]}]}
        branch=prepare_branch(p)
        self.assertEqual(branch['routing_direction'],'city_towards_branch_point')
        self.assertEqual(branch['routing_points_lon_lat'][-1],a)
        self.assertFalse(branch['official_branch_stop_sequence_verified'])
    def test_candidate_not_boarding_stop(self):
        self.assertIn('NOT_BUS_STOP',ANCHORS['48']['kind'])
        self.assertIn('NOT_OFFICIAL_GTFS_STOP',ANCHORS['35']['kind'])
    def test_far_endpoint_rejected(self):
        p={'route':'48','source_trip_id':'xxx','source_direction_id':'0',
          'stop_visits':[{'stop_id':'x','stop_name':'x','point_lon_lat':[-75.10,4.20]},
                         {'stop_id':'y','stop_name':'y','point_lon_lat':[-75.12,4.25]}]}
        with self.assertRaises(ValueError):prepare_branch(p)

if __name__=='__main__':unittest.main()
