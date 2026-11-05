def test_plans_are_seeded(client):
    plans = client.get("/api/plans").get_json()
    assert [p["tier"] for p in plans] == ["bronze", "silver", "gold"]


def test_quote(client):
    res = client.post("/api/quote", json={"age": 25, "plan_id": 1, "smoker": False})
    assert res.status_code == 200
    assert res.get_json()["monthly_premium"] == 180


def test_quote_rejects_bad_age(client):
    assert client.post("/api/quote", json={"age": 10, "plan_id": 1}).status_code == 400


def test_create_member_and_duplicate_email(client, member):
    assert member["id"] == 1
    dup = client.post("/api/members", json={
        "name": "Other", "email": "ASHA@example.com", "age": 40, "plan_id": 2})
    assert dup.status_code == 409


def test_claim_lifecycle(client, member):
    res = client.post("/api/claims", json={
        "member_id": member["id"], "description": "Knee X-ray", "amount": 1200})
    assert res.status_code == 201
    claim_id = res.get_json()["id"]
    assert client.patch(f"/api/claims/{claim_id}", json={"status": "approved"}).status_code == 200
    stats = client.get("/api/stats").get_json()
    assert stats["claims_approved"] == 1 and stats["approved_total"] == 1200


def test_claim_over_coverage_limit_is_rejected(client, member):
    res = client.post("/api/claims", json={
        "member_id": member["id"], "description": "Surgery", "amount": 999999})
    assert res.status_code == 422


def test_invalid_claim_status(client, member):
    cid = client.post("/api/claims", json={
        "member_id": member["id"], "description": "Checkup", "amount": 50}).get_json()["id"]
    assert client.patch(f"/api/claims/{cid}", json={"status": "paid"}).status_code == 400


def test_delete_member_removes_claims(client, member):
    client.post("/api/claims", json={
        "member_id": member["id"], "description": "Checkup", "amount": 50})
    assert client.delete(f"/api/members/{member['id']}").status_code == 204
    assert client.get("/api/claims").get_json() == []
