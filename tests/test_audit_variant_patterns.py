"""Test Ibagué variant audit without network access or copied upstream GTFS."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_variant_patterns import shared_order, route_family_pairs, audited


class VariantAuditTest(unittest.TestCase):
    def test_ordered_overlap_exact(self):
        d=shared_order(['1','2','3','4'],['9','1','2','4','10'])
        self.assertEqual(d['shared_stop_ids'],3)
        self.assertEqual(d['inversions'],0)
        self.assertTrue(d['shared_in_identical_order'])

    def test_out_of_order_is_flagged(self):
        self.assertEqual(shared_order(['1','2','3'],['3','1','2'])['inversions'],2)

    def test_two_families_and_direction_mismatch(self):
        ps=[{'source_trip_id':'a','direction_id':'0'}, {'source_trip_id':'b','direction_id':'1'},
            {'source_trip_id':'c','direction_id':'1'}, {'source_trip_id':'d','direction_id':'1'}]
        seq={'a':['1','2','3','4'], 'b':['1','2','3'], 'c':['5','6','7','8'], 'd':['5','6','7']}
        import itertools
        pair=[{'a':a,'b':b,**shared_order(seq[a],seq[b])} for a,b in itertools.combinations(seq,2)]
        f=route_family_pairs(ps,pair)
        self.assertEqual(len(f),2)
        self.assertEqual(sum(x['direction_id_mismatch'] for x in f),1)

    def test_no_unsupported_family_if_weak_overlap(self):
        ps=[{'source_trip_id':x,'direction_id':'0'} for x in ('a','b','c','d')]
        seq={'a':['1','2','3','4'], 'b':['1','5','6','7'], 'c':['8','9','10'], 'd':['9','11','12']}
        import itertools
        pair=[{'a':a,'b':b,**shared_order(seq[a],seq[b])} for a,b in itertools.combinations(seq,2)]
        self.assertEqual(route_family_pairs(ps,pair),[])

if __name__ == '__main__': unittest.main()
