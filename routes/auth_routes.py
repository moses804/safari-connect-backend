from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import re

from models import db, User  # keep this consistent with how your team imports

auth_bp = Blueprint("auth", __name__)

# ----------------- VALIDATION HELPERS -----------------
def validate_phone_number(phone):
    """Validate phone number format (supports various formats)"""
    # Allow digits, spaces, dashes, parentheses, and leading +
    pattern = r'^[\d\s\-\+\(\)]{7,20}$'
    return bool(re.match(pattern, phone))

# ----------------- SERVICE HELPERS (in same file) -----------------
def register_user(data):
    if User.query.filter_by(email=data["email"]).first():
        raise ValueError("Email already exists")
    
    if User.query.filter_by(phone_number=data["phone_number"]).first():
        raise ValueError("Phone number already registered")

    user = User(
        name=data["name"],
        email=data["email"],
        phone_number=data["phone_number"],
        role=data.get("role", "tourist")
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()
    return user


def login_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ValueError("Invalid email or password")

    token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role}
    )
    return token, user


# ----------------- ROUTES -----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    required = ["name", "email", "phone_number", "password"]
    if not all(k in data and data[k] for k in required):
        return {"error": "name, email, phone_number, password are required"}, 400

    # Validate phone number format
    if not validate_phone_number(data["phone_number"]):
        return {"error": "Invalid phone number format"}, 400

    # optional role validation
    if "role" in data and data["role"] not in ("tourist", "host", "driver"):
        return {"error": "role must be tourist, host, or driver"}, 400

    try:
        user = register_user(data)
        return user.to_dict(), 201
    except ValueError as e:
        return {"error": str(e)}, 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    if not data.get("email") or not data.get("password"):
        return {"error": "email and password are required"}, 400

    try:
        token, user = login_user(data["email"], data["password"])
        return {"access_token": token, "user": user.to_dict()}, 200
    except ValueError as e:
        return {"error": str(e)}, 401


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    return user.to_dict(), 200
