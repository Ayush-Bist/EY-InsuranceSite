"""Pure business logic, kept free of Flask so it is easy to unit test."""
import re

CLAIM_STATUSES = ("pending", "approved", "rejected")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def age_factor(age: int) -> float:
    if age < 30:
        return 1.0
    if age < 45:
        return 1.25
    if age < 60:
        return 1.6
    return 2.1


def calculate_premium(base_premium: float, age: int, smoker: bool) -> float:
    """Monthly premium = base x age band x smoker loading (+30%)."""
    premium = base_premium * age_factor(age)
    if smoker:
        premium *= 1.3
    return round(premium, 2)


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))
