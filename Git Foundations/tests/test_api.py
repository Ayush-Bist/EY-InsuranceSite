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

def test_filter_claims_by_status_and_text(client, member):
    a = client.post("/api/claims", json={
        "member_id": member["id"], "description": "Knee X-ray", "amount": 1200}).get_json()
    client.post("/api/claims", json={
        "member_id": member["id"], "description": "Dental cleaning", "amount": 300})
    client.patch(f"/api/claims/{a['id']}", json={"status": "approved"})

    approved = client.get("/api/claims?status=approved").get_json()
    assert len(approved) == 1 and approved[0]["description"] == "Knee X-ray"

    found = client.get("/api/claims?q=dental").get_json()
    assert len(found) == 1 and found[0]["description"] == "Dental cleaning"

    assert len(client.get("/api/claims").get_json()) == 2

def test_reject_requires_reason(client, member):
    cid = client.post("/api/claims", json={
        "member_id": member["id"], "description": "Checkup", "amount": 50}).get_json()["id"]
    assert client.patch(f"/api/claims/{cid}", json={"status": "rejected"}).status_code == 400


def test_reject_with_reason_is_saved(client, member):
    cid = client.post("/api/claims", json={
        "member_id": member["id"], "description": "Checkup", "amount": 50}).get_json()["id"]
    res = client.patch(f"/api/claims/{cid}", json={"status": "rejected", "reason": "Not covered"})
    assert res.status_code == 200
    claim = client.get("/api/claims").get_json()[0]
    assert claim["status"] == "rejected" and claim["reason"] == "Not covered"