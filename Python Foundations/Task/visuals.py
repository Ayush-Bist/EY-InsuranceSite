from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from database import get_user_category_totals, get_user_order_details


def print_terminal_bar_chart(title, series, label_key, value_key):
    print(f"\n{title}")
    if not series:
        print("No data available.")
        return

    max_value = max(float(item[value_key]) for item in series)
    if max_value == 0:
        max_value = 1

    print("-" * 50)
    for item in series:
        label = item[label_key]
        value = float(item[value_key])
        bar_width = max(1, int((value / max_value) * 30))
        print(f"{label:<20} | {'#' * bar_width} ${value:.2f}")
    print("-" * 50)


def print_terminal_visuals(user_id):
    orders = get_user_order_details(user_id)
    if orders:
        order_series = [
            {"order": f"Order #{order['id']}", "total": float(order["total_amount"])}
            for order in orders
        ]
        print_terminal_bar_chart("Terminal Order Totals", order_series, "order", "total")
    else:
        print("\nTerminal Order Totals\nNo order history to chart yet.")

    category_totals = get_user_category_totals(user_id)
    if category_totals:
        category_series = [
            {"category": row["category"], "total": float(row["total"])}
            for row in category_totals
        ]
        print_terminal_bar_chart("Terminal Category Spend", category_series, "category", "total")
    else:
        print("\nTerminal Category Spend\nNo category spending to chart yet.")


def generate_user_visuals(user_id, output_dir=None):
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    user_output_dir = output_dir / f"user_{user_id}"
    user_output_dir.mkdir(parents=True, exist_ok=True)
    orders = get_user_order_details(user_id)
    saved_files = []

    order_data = pd.DataFrame([
        {"order": f"Order #{order['id']}", "total": float(order["total_amount"])}
        for order in orders
    ], columns=["order", "total"])

    plt.figure(figsize=(10, 5))
    if order_data.empty:
        plt.text(0.5, 0.5, "No order history yet", ha="center", va="center", transform=plt.gca().transAxes)
        plt.xticks([])
        plt.yticks([])
    else:
        sns.barplot(data=order_data, x="order", y="total", hue="order", palette="Set2", dodge=False, legend=False)
    plt.title("Order Totals by Order")
    plt.xlabel("Order")
    plt.ylabel("Total ($)")
    plt.xticks(rotation=25)
    plt.tight_layout()
    total_path = user_output_dir / "order_totals.png"
    plt.savefig(total_path)
    plt.close()
    saved_files.append(str(total_path))

    category_totals = get_user_category_totals(user_id)
    category_data = pd.DataFrame(
        [
            {"category": row["category"], "total": float(row["total"])}
            for row in category_totals
        ],
        columns=["category", "total"],
    )

    plt.figure(figsize=(8, 6))
    if category_data.empty:
        plt.text(0.5, 0.5, "No category spending yet", ha="center", va="center", transform=plt.gca().transAxes)
        plt.xticks([])
        plt.yticks([])
    else:
        sns.barplot(data=category_data, x="category", y="total", hue="category", palette="Blues_d", dodge=False, legend=False)
    plt.title("Spend by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Spent ($)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    category_path = user_output_dir / "category_spend.png"
    plt.savefig(category_path)
    plt.close()
    saved_files.append(str(category_path))

    return saved_files


def print_chart_paths(chart_files):
    if not chart_files:
        print("No charts generated.")
        return

    print("\nCharts generated:")
    for item in chart_files:
        print(f"- {item}")
