from flask import request, jsonify
from lib.database import db, bcrypt
from lib.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    full_name = data.get("full_name")
    
    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
    new_user = User(
        email=email,
        username=username,
        password_hash=hashed_password,
        full_name=full_name
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or Email already exists"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    # Generate token immediately? Or ask to login? Supabase returned session, let's return token.
    access_token = create_access_token(identity=str(new_user.id))

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        },
        "session": {
            "access_token": access_token
        }
    }), 201

def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            },
            "session": {
                "access_token": access_token
            }
        }), 200
    else:
        return jsonify({"error": "Invalid login credentials"}), 401

def logout():
    return jsonify({"message": "Logged out successfully"}), 200

@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat()
        }
    }), 200
