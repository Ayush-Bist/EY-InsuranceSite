from pathlib import Path

from auth import login_user, register_new_user
from database import init_db
from orders import place_order_for_user, print_user_summary
from visuals import generate_user_visuals, print_chart_paths, print_terminal_visuals


def show_dashboard(user):
    print_user_summary(user)
    print_terminal_visuals(user["id"])
    chart_dir = Path(__file__).resolve().parent / "charts"
    chart_files = generate_user_visuals(user["id"], output_dir=chart_dir)
    print_chart_paths(chart_files)


def user_menu(user):
    while True:
        print("\n=== User Dashboard ===")
        print("1. View Summary")
        print("2. Place Order")
        print("3. Logout")

        try:
            choice = input("Select an option: ").strip()
        except EOFError:
            print("\nInput closed. Exiting dashboard.")
            return

        if choice == "1":
            show_dashboard(user)
        elif choice == "2":
            place_order_for_user(user["id"])
            show_dashboard(user)
        elif choice == "3":
            print(f"Logging out {user['full_name']}.")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    init_db()

    while True:
        print("\n=== E-Commerce Login Portal ===")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        try:
            choice = input("Select an option: ").strip()
        except EOFError:
            print("\nInput closed. Exiting program.")
            break

        if choice == "1":
            user = login_user()
            if user:
                user_menu(user)

        elif choice == "2":
            if register_new_user():
                user = login_user()
                if user:
                    user_menu(user)

        elif choice == "3":
            print("Goodbye! Thank you for using the E-Commerce platform.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Goodbye.")