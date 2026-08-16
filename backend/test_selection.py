import requests

res1 = requests.post("http://localhost:8000/api/travel/plan", json={
    "session_id": "test-session-123",
    "message": "Plan a trip to Paris from New York on 2026-09-01 for 2 people"
})
print("RES1:", res1.json().get("is_complete"))
recs = res1.json().get("recommendations", [])
print("RECOMMENDATIONS:", len(recs))

if recs:
    flight_id = recs[0]["flight"]["id"]
    hotel_id = recs[0]["hotel"]["id"]
    print(f"Selecting flight {flight_id} and hotel {hotel_id}")
    
    res2 = requests.post("http://localhost:8000/api/travel/plan", json={
        "session_id": "test-session-123",
        "message": "Plan a trip to Paris from New York on 2026-09-01 for 2 people",
        "selected_recommendation_ids": [flight_id, hotel_id]
    })
    print("RES2 STATUS:", res2.status_code)
    print("RES2 TEXT:", res2.text)
