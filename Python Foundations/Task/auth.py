from database import validate_login, register_user


def login_user():
    try:
        username = input("Username: ").strip()
        password = input("Password: ").strip()
    except EOFError:
        print("\nInput closed. Exiting login.")
        return None

    user = validate_login(username, password)
    if user:
        print(f"\nWelcome back, {user['full_name']}!")
        return user

    print("Invalid username or password.")
    return None


def register_new_user():
    try:
        username = input("Choose username: ").strip()
        password = input("Choose password: ").strip()
        full_name = input("Full name: ").strip()
    except EOFError:
        print("\nInput closed. Registration cancelled.")
        return False

    success, message = register_user(username, password, full_name)
    print(message)
    return success
