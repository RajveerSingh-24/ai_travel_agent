import json
import urllib.request

req1 = urllib.request.Request(
    'http://localhost:8000/api/travel/plan',
    data=json.dumps({
        'session_id': 'sess-995',
        'message': 'Trip to London from NY on 2026-09-01 for 10 days for 2 people'
    }).encode(),
    headers={'Content-Type': 'application/json'}
)
res1 = json.loads(urllib.request.urlopen(req1).read())
recs1 = res1['recommendations']
if recs1:
    flight_id1 = recs1[0]['flight']['id']
    print(f'Call 1 Flight ID: {flight_id1}')
    
    req2 = urllib.request.Request(
        'http://localhost:8000/api/travel/plan',
        data=json.dumps({
            'session_id': 'sess-995',
            'message': 'Trip to London from NY on 2026-09-01 for 10 days for 2 people'
        }).encode(),
        headers={'Content-Type': 'application/json'}
    )
    res2 = json.loads(urllib.request.urlopen(req2).read())
    recs2 = res2['recommendations']
    flight_id2 = recs2[0]['flight']['id']
    print(f'Call 2 Flight ID: {flight_id2}')
    print(f'Matches: {flight_id1 == flight_id2}')
