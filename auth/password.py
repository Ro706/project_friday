from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os


# ============================================================
# Flask Application
# ============================================================

app = Flask(__name__)


# ============================================================
# Database Configuration
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "data")
)

os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "password.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# User Model
# ============================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }


# ============================================================
# Initialize Database
# ============================================================

def init_db():

    with app.app_context():
        db.create_all()

    print(f"Database initialized at: {DB_PATH}")


# ============================================================
# Add User
# ============================================================

def add_user(username, password):

    with app.app_context():

        try:

            # Check if username already exists
            existing_user = User.query.filter_by(
                username=username
            ).first()

            if existing_user:
                print("Username already exists.")
                return False

            # Convert password into secure hash
            password_hash = generate_password_hash(password)

            # Create user
            new_user = User(
                username=username,
                password_hash=password_hash
            )

            # Save user
            db.session.add(new_user)
            db.session.commit()

            print("User created successfully.")

            return True

        except Exception as e:

            db.session.rollback()

            print(f"Database error: {e}")

            return False


# ============================================================
# Verify Login
# ============================================================

def verify_user(username, password):

    with app.app_context():

        user = User.query.filter_by(
            username=username
        ).first()

        if user is None:
            return False

        # Compare entered password with stored hash
        if check_password_hash(
            user.password_hash,
            password
        ):
            return True

        return False


# ============================================================
# Get User
# ============================================================

def get_user(username):

    with app.app_context():

        user = User.query.filter_by(
            username=username
        ).first()

        if user:

            return user.to_dict()

        return None


# ============================================================
# Get All Users
# ============================================================

def get_all_users():

    with app.app_context():

        users = User.query.all()

        return [
            user.to_dict()
            for user in users
        ]


# ============================================================
# Delete User
# ============================================================

def delete_user(username):

    with app.app_context():

        try:

            user = User.query.filter_by(
                username=username
            ).first()

            if user is None:
                print("User not found.")
                return False

            db.session.delete(user)
            db.session.commit()

            print("User deleted successfully.")

            return True

        except Exception as e:

            db.session.rollback()

            print(f"Database error: {e}")

            return False


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    # Create database and table
    init_db()

    # Create a user
    add_user(
        "test",
        "test123"
    )

    # Verify login
    if verify_user(
        "test",
        "test123"
    ):
        print("Login successful.")
    else:
        print("Invalid username or password.")

    # Get user information
    print("\nUser:")
    print(get_user("test"))

    # Get all users
    print("\nAll users:")
    print(get_all_users())