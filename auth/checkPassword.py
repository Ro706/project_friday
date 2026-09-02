try:
    from .password import verify_user
except ImportError:
    from password import verify_user


def check_password(username, password):
    """Return whether the supplied credentials match a stored user."""
    return verify_user(username, password)

if __name__ == "__main__":
    # Example usage
    username = "rohit"
    password = "@rohit21"
    if check_password(username, password):
        print("Password is correct.")
    else:
        print("Password is incorrect.")