import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_CSV = BASE_DIR / "products.csv"
USERS_CSV = BASE_DIR / "users.csv"
ORDERS_CSV = BASE_DIR / "orders.csv"
ORDER_ITEMS_CSV = BASE_DIR / "order_items.csv"

DEFAULT_PRODUCTS = [
    {"id": 101, "name": "Wireless Headphones", "category": "Electronics", "price": 80.0, "stock_count": 15},
    {"id": 102, "name": "Bluetooth Speaker", "category": "Electronics", "price": 45.0, "stock_count": 10},
    {"id": 103, "name": "Phone Case", "category": "Accessories", "price": 15.0, "stock_count": 50},
    {"id": 104, "name": "Smart Watch", "category": "Electronics", "price": 120.0, "stock_count": 25},
    {"id": 105, "name": "USB Cable", "category": "Accessories", "price": 10.0, "stock_count": 40},
]

USER_FIELDS = ["id", "username", "password", "full_name"]
PRODUCT_FIELDS = ["id", "name", "category", "price", "stock_count"]
ORDER_FIELDS = ["id", "user_id", "order_date", "total_amount", "status"]
ORDER_ITEM_FIELDS = ["id", "order_id", "product_name", "category", "quantity", "price"]


def _read_csv(path, fieldnames):
    if not path.exists():
        return []

    with path.open("r", newline="", encoding="utf-8") as csv_file:
        rows = []
        for row in csv.DictReader(csv_file):
            if not any(row.get(field) not in (None, "") for field in fieldnames):
                continue
            matching_headers = sum(row.get(field) == field for field in fieldnames)
            if matching_headers > 1:
                continue
            rows.append({field: row.get(field, "") for field in fieldnames})

    return rows


def _write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _seed_demo_files():
    if not PRODUCTS_CSV.exists() or not PRODUCTS_CSV.stat().st_size:
        _write_csv(PRODUCTS_CSV, DEFAULT_PRODUCTS, PRODUCT_FIELDS)

    if USERS_CSV.exists() and USERS_CSV.stat().st_size:
        return

    demo_users = [
        {"id": 1, "username": "admin", "password": "admin123", "full_name": "Admin User"},
        {"id": 2, "username": "jane", "password": "jane123", "full_name": "Jane Smith"},
        {"id": 3, "username": "sam", "password": "sam123", "full_name": "Sam Wilson"},
    ]
    _write_csv(USERS_CSV, demo_users, USER_FIELDS)

    if not ORDERS_CSV.exists() or not ORDERS_CSV.stat().st_size:
        demo_orders = [
            {"id": 1, "user_id": 1, "order_date": "2026-10-01 00:00:00", "total_amount": 220.0, "status": "Delivered"},
            {"id": 2, "user_id": 1, "order_date": "2026-10-12 00:00:00", "total_amount": 180.5, "status": "Shipped"},
            {"id": 3, "user_id": 2, "order_date": "2026-10-18 00:00:00", "total_amount": 120.0, "status": "Delivered"},
            {"id": 4, "user_id": 3, "order_date": "2026-10-22 00:00:00", "total_amount": 165.0, "status": "Processing"},
        ]
        _write_csv(ORDERS_CSV, demo_orders, ORDER_FIELDS)

    if not ORDER_ITEMS_CSV.exists() or not ORDER_ITEMS_CSV.stat().st_size:
        demo_items = [
            {"id": 1, "order_id": 1, "product_name": "Wireless Headphones", "category": "Electronics", "quantity": 1, "price": 180.0},
            {"id": 2, "order_id": 1, "product_name": "USB Cable", "category": "Accessories", "quantity": 2, "price": 20.0},
            {"id": 3, "order_id": 2, "product_name": "Phone Case", "category": "Accessories", "quantity": 3, "price": 15.0},
            {"id": 4, "order_id": 2, "product_name": "Bluetooth Speaker", "category": "Electronics", "quantity": 1, "price": 45.0},
            {"id": 5, "order_id": 3, "product_name": "Smart Watch", "category": "Electronics", "quantity": 1, "price": 120.0},
            {"id": 6, "order_id": 4, "product_name": "Bluetooth Speaker", "category": "Electronics", "quantity": 1, "price": 45.0},
            {"id": 7, "order_id": 4, "product_name": "USB Cable", "category": "Accessories", "quantity": 2, "price": 20.0},
            {"id": 8, "order_id": 4, "product_name": "Phone Case", "category": "Accessories", "quantity": 4, "price": 15.0},
        ]
        _write_csv(ORDER_ITEMS_CSV, demo_items, ORDER_ITEM_FIELDS)


def init_db():
    _seed_demo_files()
    return True


def validate_login(username, password):
    users = _read_csv(USERS_CSV, USER_FIELDS)
    for user in users:
        if user["username"] == username and user["password"] == password:
            return {
                "id": _to_int(user["id"]),
                "username": user["username"],
                "password": user["password"],
                "full_name": user["full_name"],
            }
    return None


def register_user(username, password, full_name):
    if not username or not password or not full_name:
        return False, "All fields are required."

    users = _read_csv(USERS_CSV, USER_FIELDS)
    if any(user["username"].strip().lower() == username.strip().lower() for user in users):
        return False, "Username already exists. Please choose another one."

    next_id = max((_to_int(user["id"]) for user in users), default=0) + 1
    users.append(
        {
            "id": next_id,
            "username": username.strip(),
            "password": password.strip(),
            "full_name": full_name.strip(),
        }
    )
    _write_csv(USERS_CSV, users, USER_FIELDS)
    return True, "User registered successfully."


def get_all_products():
    products = _read_csv(PRODUCTS_CSV, PRODUCT_FIELDS)
    return [
        {
            "id": _to_int(product["id"]),
            "name": product["name"],
            "category": product["category"],
            "price": _to_float(product["price"]),
            "stock_count": _to_int(product["stock_count"]),
        }
        for product in products
    ]


def create_order(user_id, selected_items):
    if not selected_items:
        return None, "No product selected."

    products = get_all_products()
    product_map = {product["id"]: product for product in products}
    total_amount = 0.0
    order_items = []

    for product_id, quantity in selected_items:
        if quantity <= 0:
            return None, "Quantity must be greater than zero."

        product = product_map.get(product_id)
        if not product:
            return None, f"Product {product_id} does not exist."

        if product["stock_count"] < quantity:
            return None, f"Not enough stock for {product['name']}."

        item_total = float(product["price"]) * quantity
        total_amount += item_total
        order_items.append(
            {
                "product_id": product_id,
                "product_name": product["name"],
                "category": product["category"],
                "quantity": quantity,
                "price": float(product["price"]),
            }
        )

    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    orders = _read_csv(ORDERS_CSV, ORDER_FIELDS)
    next_order_id = max((_to_int(order["id"]) for order in orders), default=0) + 1
    orders.append(
        {
            "id": next_order_id,
            "user_id": user_id,
            "order_date": order_date,
            "total_amount": round(total_amount, 2),
            "status": "Processing",
        }
    )
    _write_csv(ORDERS_CSV, orders, ORDER_FIELDS)

    order_items_rows = _read_csv(ORDER_ITEMS_CSV, ORDER_ITEM_FIELDS)
    next_item_id = max((_to_int(item["id"]) for item in order_items_rows), default=0) + 1

    for item in order_items:
        order_items_rows.append(
            {
                "id": next_item_id,
                "order_id": next_order_id,
                "product_name": item["product_name"],
                "category": item["category"],
                "quantity": item["quantity"],
                "price": item["price"],
            }
        )
        next_item_id += 1

        product = product_map[item["product_id"]]
        updated_product = {
            "id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "stock_count": product["stock_count"] - item["quantity"],
        }
        products = [
            updated_product if current["id"] == product["id"] else current
            for current in products
        ]

    _write_csv(ORDER_ITEMS_CSV, order_items_rows, ORDER_ITEM_FIELDS)
    _write_csv(PRODUCTS_CSV, products, PRODUCT_FIELDS)

    return {
        "order_id": next_order_id,
        "total_amount": round(total_amount, 2),
        "items": order_items,
        "order_date": order_date,
    }, None


def get_user_by_id(user_id):
    users = _read_csv(USERS_CSV, USER_FIELDS)
    for user in users:
        if _to_int(user["id"]) == _to_int(user_id):
            return {
                "id": _to_int(user["id"]),
                "username": user["username"],
                "password": user["password"],
                "full_name": user["full_name"],
            }
    return None


def get_user_order_details(user_id):
    orders = _read_csv(ORDERS_CSV, ORDER_FIELDS)
    item_rows = _read_csv(ORDER_ITEMS_CSV, ORDER_ITEM_FIELDS)

    result = []
    for order in orders:
        if _to_int(order["user_id"]) != _to_int(user_id):
            continue

        matching_items = [
            {
                "product_name": item["product_name"],
                "category": item["category"],
                "quantity": _to_int(item["quantity"]),
                "price": _to_float(item["price"]),
            }
            for item in item_rows
            if _to_int(item["order_id"]) == _to_int(order["id"])
        ]

        result.append(
            {
                "id": _to_int(order["id"]),
                "order_date": order["order_date"],
                "status": order["status"],
                "total_amount": _to_float(order["total_amount"]),
                "items": matching_items,
            }
        )

    result.sort(key=lambda item: item["order_date"], reverse=True)
    return result


def get_user_category_totals(user_id):
    totals = {}
    for order in get_user_order_details(user_id):
        for item in order["items"]:
            category = item["category"]
            totals[category] = totals.get(category, 0.0) + (item["price"] * item["quantity"])

    return [{"category": category, "total": round(total, 2)} for category, total in sorted(totals.items(), key=lambda entry: entry[1], reverse=True)]


def get_user_summary(user_id):
    orders = get_user_order_details(user_id)
    if not orders:
        return {
            "total_orders": 0,
            "total_spent": 0.0,
            "average_order": 0.0,
            "orders": [],
        }

    total_spent = sum(order["total_amount"] for order in orders)
    total_orders = len(orders)

    return {
        "total_orders": total_orders,
        "total_spent": round(total_spent, 2),
        "average_order": round(total_spent / total_orders, 2),
        "orders": orders,
    }
