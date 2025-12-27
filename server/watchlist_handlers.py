from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from lib.database import db
from lib.models import Watchlist, User

@jwt_required()
def add_to_watchlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    media_id = data.get("media_id")
    media_type = data.get("media_type")
    
    if not media_id or not media_type:
        return jsonify({"error": "media_id and media_type are required"}), 400
        
    # Check if already exists
    existing = Watchlist.query.filter_by(user_id=user_id, media_id=media_id).first()
    if existing:
        return jsonify({"message": "Item already in watchlist"}), 200
        
    new_item = Watchlist(user_id=user_id, media_id=media_id, media_type=media_type)
    
    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Added to watchlist", "item": {
            "media_id": media_id,
            "media_type": media_type
        }}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    # Use pagination on the relationship or query
    pagination = Watchlist.query.filter_by(user_id=user_id).order_by(Watchlist.added_at.desc()).paginate(page=page, per_page=limit, error_out=False)
    
    from lib.tmdb_client import TMDBClient
    client = TMDBClient()

    watchlist_items = []
    for item in pagination.items:
        details = client.get_media_basic_details(item.media_id, item.media_type)
        details["added_at"] = item.added_at.isoformat()
        watchlist_items.append(details)
        
    return jsonify({
        "watchlist": watchlist_items,
        "page": pagination.page,
        "total_pages": pagination.pages,
        "total_results": pagination.total
    }), 200

@jwt_required()
def remove_from_watchlist(media_id):
    user_id = get_jwt_identity()
    
    item = Watchlist.query.filter_by(user_id=user_id, media_id=media_id).first()
    
    if not item:
        return jsonify({"error": "Item not found in watchlist"}), 404
        
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Removed from watchlist"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
