#!/usr/bin/env python3
"""Research-only direction and rural branch geometry check for Ibagué.

Uses the SHA-256-verified university feed and OSM-identified candidate places.
Never promotes candidates to GTFS, adjusts departure allocations, or invents
an official bus stop at a settlement's centroid.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.request
from pathlib import Path

from route_changed_shapes_graphhopper import (
    SOURCE_URL, HEADERS, GraphHopper, manifest, meters, source_tables,
)
from audit_variant_patterns import shared_order

# Coordinates from OSM objects, independent of the older university GTFS.
# Place= village is NOT a boarding stop. The bus_station tag for Cay likewise
# does not establish official service or a verified curbside terminal.
ANCHORS = {
    '35': {
        'name': 'Vereda Cay OSM bus_station',
        'lon_lat': [-75.25473, 4.47358],
        'osm_ref': 'node/4339120589',
        'source_url': 'https://www.openstreetmap.org/node/4339120589',
        'kind': 'OSM_BUS_STATION_NOT_OFFICIAL_GTFS_STOP',
    },
    '48': {
        'name': 'Juntas OSM village center',
        'lon_lat': [-75.3214, 4.55603],
        'osm_ref': 'node/703223338',
        'source_url': 'https://www.openstreetmap.org/node/703223338',
        'kind': 'OSM_VILLAGE_CENTER_NOT_BUS_STOP',
    },
}
OFFICIAL_MAPS = {
    '8': 'https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-8-scaled.png',
    '35': 'https://transmusical.gov.co/wp-content/uploads/2026/06/Ruta-35-scaled.jpg',
    '48': 'https://transmusical.gov.co/wp-content/uploads/2026/10/Ruta-48-scaled.png',
}


def by_trip(patterns):
    index = {p['source_trip_id']: p for p in patterns}
    if len(index) != len(patterns):
        raise ValueError('Duplicate source trip')
    return index


def review_route8(patterns):
    """Infer geographic directions only, with published 2026 poster context.

    Official poster: IDA starts at Nueva Castilla (east) and ends at
    Santa Barbara (west), VUELTA does the opposite. This supports direction
    but cannot prove that all four old trip variants are still operating.
    """
    idx = by_trip(patterns)
    if set(idx) != {'TRIP_R9', 'TRIP_R10', 'TRIP_R11', 'TRIP_R12'}:
        raise ValueError('Unexpected route 8 source trips')
    pairs = (('TRIP_R9', 'TRIP_R11'), ('TRIP_R10', 'TRIP_R12'))
    details = []
    family = {}
    for group, (a, b) in zip(('IDA', 'VUELTA'), pairs):
        ap = idx[a]['stop_visits']
        bp = idx[b]['stop_visits']
        relation = shared_order([x['stop_id'] for x in ap], [x['stop_id'] for x in bp])
        if not relation['shared_in_identical_order'] or relation['fraction_of_shorter'] < 0.65:
            raise ValueError('Unexpected route 8 stop-family order')
        family[group] = {'source_trips': [a, b], **relation}
        for name in (a,b):
            family[name] = group
    for name in sorted(idx):
        p = idx[name]
        visits = p['stop_visits']
        origin, terminus = visits[0], visits[-1]
        dx = terminus['point_lon_lat'][0] - origin['point_lon_lat'][0]
        geo = 'IDA' if dx < -0.02 else ('VUELTA' if dx > 0.02 else 'UNCLEAR')
        expected = family[name]
        if geo != expected:
            raise ValueError(f'Route 8 course mismatched official-direction stop family: {name}')
        designated_full = 'TRIP_R9' if geo == 'IDA' else 'TRIP_R10'
        full = idx[designated_full]['stop_visits']
        if geo == 'IDA':
            west_deviation = meters(terminus['point_lon_lat'], full[-1]['point_lon_lat'])
        else:
            west_deviation = meters(origin['point_lon_lat'], full[0]['point_lon_lat'])
        details.append({
            'source_trip_id': name, 'source_direction_id': p['source_direction_id'],
            'poster_direction_label': geo,
            'direction_id_suggested_by_official_poster': '0' if geo == 'IDA' else '1',
            'direction_metadata_mismatch': p['source_direction_id'] != ('0' if geo == 'IDA' else '1'),
            'stop_count': len(visits),
            'first_stop_id': origin['stop_id'], 'last_stop_id': terminus['stop_id'],
            'first_stop_name': origin['stop_name'], 'last_stop_name': terminus['stop_name'],
            'first_point_lon_lat': origin['point_lon_lat'], 'last_point_lon_lat': terminus['point_lon_lat'],
            'west_endpoint_distance_from_long_pattern_m': round(west_deviation,1),
            'candidate_west_shortening': name in ('TRIP_R11','TRIP_R12') and west_deviation > 700,
            'route_active_in_october_2026_confirmed': False,
            'legal_service_variant_confirmed': False,
            'poster_url': OFFICIAL_MAPS['8'],
        })
    return {
        'official_poster_direction_legend': {
            'IDA': 'Nueva Castilla (east) -> Santa Barbara (west)',
            'VUELTA': 'Santa Barbara (west) -> Nueva Castilla (east)',
        },
        'geographic_families': {k:v for k,v in family.items() if k in ('IDA','VUELTA')},
        'direction_id_correction_candidate': 'TRIP_R11: 1 -> 0',
        'source_trips': details,
        'all_source_patterns_confirmed_current': False,
        'generator_direction_or_headway_changed': False,
    }


def prepare_branch(pattern):
    route = pattern['route']
    anchor = ANCHORS[route]
    visits = pattern['stop_visits']
    first, last = visits[0], visits[-1]
    dfirst = meters(first['point_lon_lat'],anchor['lon_lat'])
    dlast = meters(last['point_lon_lat'],anchor['lon_lat'])
    endpoint_name = 'first' if dfirst < dlast else 'last'
    endpoint = first if endpoint_name == 'first' else last
    dmin = min(dfirst,dlast)
    # Reject unknown endpoint position rather than routing through the city.
    if dmin > 15000:
        raise ValueError(f"No plausible source terminal near {anchor['name']} ({round(dmin)} m)")
    if endpoint_name == 'first':
        ordered = [anchor['lon_lat'], endpoint['point_lon_lat']]
        direction = 'branch_point_towards_city'
    else:
        ordered = [endpoint['point_lon_lat'], anchor['lon_lat']]
        direction = 'city_towards_branch_point'
    return {
        'route': route, 'source_trip_id': pattern['source_trip_id'],
        'source_direction_id': pattern['source_direction_id'],
        'branch_name': anchor['name'], 'branch_anchor_osm_id': anchor['osm_ref'],
        'branch_anchor_lon_lat': anchor['lon_lat'], 'branch_anchor_kind': anchor['kind'],
        'branch_anchor_url': anchor['source_url'],
        'reference_poster_url': OFFICIAL_MAPS[route],
        'source_nearest_terminal_side': endpoint_name,
        'source_nearest_terminal_stop_id': endpoint['stop_id'],
        'source_nearest_terminal_stop_name': endpoint['stop_name'],
        'source_nearest_terminal_lon_lat': endpoint['point_lon_lat'],
        'straight_line_terminal_to_candidate_m': round(dmin,1),
        'routing_direction': direction,
        'routing_points_lon_lat': ordered,
        'official_branch_junction_verified': False,
        'official_branch_stop_sequence_verified': False,
        'exact_bus_stop_at_osm_anchor_verified': False,
        'gtfs_service_or_frequency_modified': False,
        'classification': 'OSM_ANCHOR_CANDIDATE_NO_GTFS_APPROVAL',
    }


def prep(tables, output):
    p8 = manifest(tables, {'8'})['patterns']
    branch = manifest(tables, {'35','48'})['patterns']
    if len(p8)!=4 or len(branch)!=4 or {p['route'] for p in branch}!={'35','48'}:
        raise ValueError('Unexpected source pattern scope')
    result = {
        'project': 'Ibagué 2026 variant-road investigation',
        'source': 'SHA256-pinned 22 May 2026 GTFS',
        'route8': review_route8(p8),
        'branches': [prepare_branch(p) for p in branch],
        'published_gtfs_modified': False,
        'requires_official_map_and_stop_order_review': True,
    }
    output.mkdir(parents=True,exist_ok=True)
    (output/'branch_variant_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (output/'route8_direction_evidence.csv').open('w',newline='',encoding='utf-8') as f:
        cols = ('source_trip_id','source_direction_id','poster_direction_label',
                'direction_id_suggested_by_official_poster','direction_metadata_mismatch',
                'stop_count','first_stop_name','last_stop_name',
                'west_endpoint_distance_from_long_pattern_m','candidate_west_shortening',
                'route_active_in_october_2026_confirmed','legal_service_variant_confirmed','poster_url')
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(result['route8']['source_trips'])
    return result


def routing_candidate(result, output, gh):
    gh.check_bus_profile()
    roads=[]; reports=[]; successes=0
    for row in result['branches']:
        props={k:v for k,v in row.items() if k not in ('routing_points_lon_lat',)}
        try:
            candidate=gh.route(row['routing_points_lon_lat'])
            coords=candidate['coordinates']
            dist=candidate['distance_m']
            if not 0<dist<30000:
                raise ValueError('Branch road distance outside plausibility range')
            props.update({'routing_status':'GRAPHOPPER_BUS_CANDIDATE', 'graphhopper_distance_m':round(dist,1),
                          'road_vs_straight_ratio':round(dist/row['straight_line_terminal_to_candidate_m'],2),
                          'is_actual_operational_branch_verified':False})
            roads.append({'type':'Feature','properties':props,
                          'geometry':{'type':'LineString','coordinates':coords}})
            successes+=1
        except (RuntimeError,ValueError) as exc:
            props.update({'routing_status':'ROUTING_FAILED','reason_type':type(exc).__name__})
        reports.append(props)
    feature_collection={'type':'FeatureCollection',
        'metadata':{'status':'RESEARCH_ONLY_NOT_A_GTFS_SHAPE','branches_successful':successes,
                    'official_branch_ways_verified':False,'source_trips_and_stops_modified':0,
                    'osm_attribution':'© OpenStreetMap contributors'},'features':roads}
    (output/'osm_branch_graphhopper_candidates_RESEARCH_ONLY.geojson').write_text(
        json.dumps(feature_collection,ensure_ascii=False)+'\n',encoding='utf-8')
    (output/'branch_route_qa.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if successes==0:
        raise RuntimeError('No branch road candidates generated')
    return reports


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    src=ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--download',action='store_true')
    src.add_argument('--zip',type=Path)
    ap.add_argument('--output',type=Path,default=Path('build/ibague-variant-branch-qa'))
    ap.add_argument('--route',action='store_true',help='Request provisional GraphHopper bus roads, never GTFS shapes')
    args=ap.parse_args()
    if args.download:
        with urllib.request.urlopen(urllib.request.Request(SOURCE_URL,headers=HEADERS),timeout=90) as res:
            payload=res.read()
    else: payload=args.zip.read_bytes()
    result=prep(source_tables(payload),args.output)
    print('Route 8 geodirectional source patterns:',
          [(x['source_trip_id'],x['poster_direction_label'],x['direction_metadata_mismatch'])
           for x in result['route8']['source_trips']])
    print('Branch candidate terminal proximity (m):',
          [(x['route'],x['source_trip_id'],x['straight_line_terminal_to_candidate_m'])
           for x in result['branches']])
    if args.route:
        base=os.getenv('GRAPHHOPPER_URL','')
        if not base:
            raise RuntimeError('GRAPHHOPPER_URL organization variable is required')
        p=routing_candidate(result,args.output,GraphHopper(base,profile=os.getenv('GRAPHHOPPER_PROFILE','bus')))
        print('GraphHopper route statuses:',[(x['route'],x['source_trip_id'],x['routing_status']) for x in p])
    else:print('No GraphHopper requested; source research manifest generated')


if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError) as exc:
        print(type(exc).__name__+': '+str(exc),file=sys.stderr)
        sys.exit(1)
