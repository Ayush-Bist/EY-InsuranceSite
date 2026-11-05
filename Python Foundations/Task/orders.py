from database import (
    create_order,
    get_all_products,
    get_user_category_totals,
    get_user_order_details,
    get_user_summary,
)


def get_dashboard_summary(user_id):
    summary = get_user_summary(user_id)
    summary["category_totals"] = get_user_category_totals(user_id)
    return summary


def display_products():
    products = get_all_products()
    print("\nAvailable Products:")
    for product in products:
        print(
            f"{product['id']} | {product['name']} | {product['category']} | "
            f"${product['price']:.2f} | Stock: {product['stock_count']}"
        )


def place_order_for_user(user_id):
    display_products()

    selected_items = []
    while True:
        try:
            item_choice = input("Enter product ID to add (0 to finish): ").strip()
        except EOFError:
            print("\nInput closed. Order cancelled.")
            return
        if item_choice == "0":
            break

        try:
            product_id = int(item_choice)
        except ValueError:
            print("Please enter a valid product ID.")
            continue

        try:
            quantity = input("Enter quantity: ").strip()
        except EOFError:
            print("\nInput closed. Order cancelled.")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            print("Quantity must be a number.")
            continue

        selected_items.append((product_id, quantity))

    if not selected_items:
        print("No items selected for this order.")
        return

    order_data, error = create_order(user_id, selected_items)
    if error:
        print(f"Order failed: {error}")
        return

    print("\nOrder placed successfully!")
    print(f"Order ID: {order_data['order_id']}")
    print(f"Total Amount: ${order_data['total_amount']:.2f}")
    for item in order_data["items"]:
        print(f"- {item['product_name']} x {item['quantity']} @ ${item['price']:.2f}")


def print_user_summary(user):
    summary = get_dashboard_summary(user["id"])

    print("\n=== User Order Summary ===")
    print(f"User: {user['full_name']}")
    print(f"Total Orders: {summary['total_orders']}")
    print(f"Total Spent: ${summary['total_spent']:.2f}")
    print(f"Average Order Value: ${summary['average_order']:.2f}")

    if not summary["orders"]:
        print("No orders found for this user.")
        return

    print("\nRecent Orders:")
    for order in summary["orders"]:
        print(
            f"- Order #{order['id']} | Date: {order['order_date']} | Status: {order['status']} | "
            f"Total: ${order['total_amount']:.2f}"
        )
        for item in order["items"]:
            print(
                f"  * {item['product_name']} ({item['category']}) x {item['quantity']} @ "
                f"${item['price']:.2f}"
            )

    if summary["category_totals"]:
        print("\nCategory Spend:")
        for row in summary["category_totals"]:
            print(f"- {row['category']}: ${float(row['total']):.2f}")
