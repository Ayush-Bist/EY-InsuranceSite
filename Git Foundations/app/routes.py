import csv
import io
import sqlite3

from flask import Blueprint, Response, jsonify, render_template, request

from .db import get_db
from .services import CLAIM_STATUSES, calculate_premium, is_valid_email

bp = Blueprint("main", __name__)


def error(message, status=400):
    return jsonify({"error": message}), status


def rows(cursor):
    return [dict(r) for r in cursor.fetchall()]


@bp.get("/")
def index():
    return render_template("index.html")


# ---- Plans -----------------------------------------------------------------
@bp.get("/api/plans")
def list_plans():
    return jsonify(rows(get_db().execute("SELECT * FROM plans ORDER BY base_premium")))


@bp.post("/api/quote")
def quote():
    data = request.get_json(silent=True) or {}
    try:
        age = int(data.get("age"))
        plan_id = int(data.get("plan_id"))
    except (TypeError, ValueError):
        return error("Enter a valid age and choose a plan.")
    if not 18 <= age <= 100:
        return error("Age must be between 18 and 100.")
    plan = get_db().execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
    if plan is None:
        return error("Plan not found.", 404)
    premium = calculate_premium(plan["base_premium"], age, bool(data.get("smoker")))
    return jsonify({"plan": plan["name"], "monthly_premium": premium,
                    "annual_premium": round(premium * 12, 2)})


# ---- Members ---------------------------------------------------------------
@bp.get("/api/members")
def list_members():
    cur = get_db().execute(
        "SELECT m.id, m.name, m.email, m.age, m.plan_id, p.name AS plan_name "
        "FROM members m JOIN plans p ON p.id = m.plan_id ORDER BY m.id DESC"
    )
    return jsonify(rows(cur))


@bp.post("/api/members")
def create_member():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    try:
        age = int(data.get("age"))
        plan_id = int(data.get("plan_id"))
    except (TypeError, ValueError):
        return error("Age and plan are required.")
    if not name:
        return error("Name is required.")
    if not is_valid_email(email):
        return error("Enter a valid email address.")
    if not 18 <= age <= 100:
        return error("Age must be between 18 and 100.")
    db = get_db()
    if db.execute("SELECT 1 FROM plans WHERE id = ?", (plan_id,)).fetchone() is None:
        return error("Plan not found.", 404)
    try:
        cur = db.execute(
            "INSERT INTO members (name, email, age, plan_id) VALUES (?, ?, ?, ?)",
            (name, email, age, plan_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error("A member with this email already exists.", 409)
    return jsonify({"id": cur.lastrowid, "name": name, "email": email,
                    "age": age, "plan_id": plan_id}), 201


@bp.delete("/api/members/<int:member_id>")
def delete_member(member_id):
    db = get_db()
    cur = db.execute("DELETE FROM members WHERE id = ?", (member_id,))
    db.commit()
    if cur.rowcount == 0:
        return error("Member not found.", 404)
    return "", 204


# ---- Claims ----------------------------------------------------------------
@bp.get("/api/claims")
def list_claims():
    cur = get_db().execute(
        "SELECT c.id, c.member_id, m.name AS member_name, c.description, "
        "c.amount, c.status, c.created_at FROM claims c "
        "JOIN members m ON m.id = c.member_id ORDER BY c.id DESC"
    )
    return jsonify(rows(cur))


@bp.post("/api/claims")
def create_claim():
    data = request.get_json(silent=True) or {}
    description = (data.get("description") or "").strip()
    try:
        member_id = int(data.get("member_id"))
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return error("Choose a member and enter a claim amount.")
    if not description:
        return error("Describe the treatment or service.")
    if amount <= 0:
        return error("Claim amount must be greater than zero.")
    db = get_db()
    member = db.execute(
        "SELECT m.id, p.coverage_limit FROM members m "
        "JOIN plans p ON p.id = m.plan_id WHERE m.id = ?", (member_id,)
    ).fetchone()
    if member is None:
        return error("Member not found.", 404)
    if amount > member["coverage_limit"]:
        return error("Amount exceeds this plan's coverage limit.", 422)
    cur = db.execute(
        "INSERT INTO claims (member_id, description, amount) VALUES (?, ?, ?)",
        (member_id, description, amount),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "status": "pending"}), 201


@bp.patch("/api/claims/<int:claim_id>")
def update_claim(claim_id):
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in CLAIM_STATUSES:
        return error("Status must be one of: " + ", ".join(CLAIM_STATUSES) + ".")
    db = get_db()
    cur = db.execute("UPDATE claims SET status = ? WHERE id = ?", (status, claim_id))
    db.commit()
    if cur.rowcount == 0:
        return error("Claim not found.", 404)
    return jsonify({"id": claim_id, "status": status})


# ---- Dashboard -------------------------------------------------------------
@bp.get("/api/stats")
def stats():
    db = get_db()
    one = lambda q: db.execute(q).fetchone()[0]
    return jsonify({
        "members": one("SELECT COUNT(*) FROM members"),
        "claims_pending": one("SELECT COUNT(*) FROM claims WHERE status='pending'"),
        "claims_approved": one("SELECT COUNT(*) FROM claims WHERE status='approved'"),
        "approved_total": one("SELECT COALESCE(SUM(amount),0) FROM claims WHERE status='approved'"),
    })

# ---- Export ----------------------------------------------------------------
@bp.get("/api/claims/export.csv")
def export_claims():
    cur = get_db().execute(
        "SELECT c.id, m.name, c.description, c.amount, c.status, c.created_at "
        "FROM claims c JOIN members m ON m.id = c.member_id ORDER BY c.id"
    )
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "member", "description", "amount", "status", "created_at"])
    writer.writerows([tuple(r) for r in cur.fetchall()])
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=claims.csv"},
    )