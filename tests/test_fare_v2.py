"""Offline GTFS Fares v2 tests for 2026-only Ibagué prices."""
import csv
import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from fare_v2 import make_2026_fares, _active_on, FARE_IDS

ROOT = Path(__file__).resolve().parents[1]

def register(name):
    with (ROOT / 'research' / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def routes():
    return [{'route_id': str(i), 'route_short_name': 'RUTA '+r['route']}
            for i,r in enumerate(register('fare_route_scope_2026.csv'), 1)]

class TestFareV2(unittest.TestCase):
    def generate(self, start, days, holidays):
        return make_2026_fares(routes(), register('official_fares_2026.csv'),
                               register('fare_route_scope_2026.csv'), start, days, holidays)

    def test_urban_daytype_prices_and_exclusions(self):
        tables, calendar, exc, report = self.generate(dt.date(2026,11,20), 90,
                                                       {dt.date(2026,12,8),dt.date(2026,12,25),
                                                        dt.date(2027,1,1),dt.date(2027,1,11)})
        self.assertEqual({x['amount'] for x in tables['fare_products.txt']}, {'3300.00','3400.00'})
        self.assertEqual({x['currency'] for x in tables['fare_products.txt']}, {'COP'})
        self.assertEqual(len(tables['fare_leg_rules.txt']),2)
        self.assertEqual(len(tables['timeframes.txt']),3)
        self.assertEqual(len(tables['route_networks.txt']),30)
        self.assertEqual(report['urban_fare_mapped_routes'],25)
        self.assertEqual(report['unpriced_review_route_labels'],['28','29','35','4/7','48'])
        self.assertEqual(report['fare_validity_end'],'2026-12-31')
        self.assertEqual({r['end_date'] for r in calendar},{'20261231'})
        self.assertEqual(len(exc),4) # two December 2026 holidays; Jan 2027 excluded
        self.assertEqual(_active_on(dt.date(2026,12,25),calendar,exc),{FARE_IDS['SU']})
        self.assertEqual(_active_on(dt.date(2026,12,26),calendar,exc),{FARE_IDS['SA']})
        self.assertEqual(_active_on(dt.date(2026,12,27),calendar,exc),{FARE_IDS['SU']})
        self.assertEqual(_active_on(dt.date(2027,1,1),calendar,exc),set())

    def test_no_2027_fare_without_new_source(self):
        tables,calendar,exceptions,report=self.generate(dt.date(2027,1,1),60,set())
        self.assertEqual(tables,{})
        self.assertEqual(calendar,[])
        self.assertEqual(exceptions,[])
        self.assertFalse(report['fare_v2_active'])

    def test_short_2026_range_and_no_holiday(self):
        tables,calendar,exceptions,report=self.generate(dt.date(2026,12,30),2,set())
        self.assertEqual(report['fare_validity_start'],'2026-12-30')
        self.assertEqual(report['fare_validity_end'],'2026-12-31')
        self.assertEqual(exceptions,[])

    def test_changed_or_missing_official_rates_rejected(self):
        a=register('official_fares_2026.csv')
        a[0]['amount_cop']='3500'
        with self.assertRaisesRegex(ValueError,'Inconsistent/unverified'):
            make_2026_fares(routes(),a,register('fare_route_scope_2026.csv'),dt.date(2026,12,20),7,set())

    def test_unverified_route_scope_required(self):
        with self.assertRaisesRegex(ValueError,'Unreviewed route fare scope'):
            make_2026_fares(routes(),register('official_fares_2026.csv'),
                            register('fare_route_scope_2026.csv')[:-1],dt.date(2026,12,20),7,set())

if __name__=='__main__':
    unittest.main()
