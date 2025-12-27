from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from lib.database import db
from lib.models import WatchHistory
from datetime import datetime

@jwt_required()
def update_history():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    media_id = data.get("media_id")
    media_type = data.get("media_type")
    progress = data.get("progress", 0)
    duration = data.get("duration", 0)
    season = data.get("season")
    episode = data.get("episode")
    
    if not media_id or not media_type:
        return jsonify({"error": "media_id and media_type are required"}), 400
        
    # Find existing record
    query = WatchHistory.query.filter_by(
        user_id=user_id, 
        media_id=media_id,
        media_type=media_type
    )
    
    if media_type == 'series':
        if season is None or episode is None:
             return jsonify({"error": "season and episode required for series"}), 400
        query = query.filter_by(season=season, episode=episode)
        
    history_item = query.first()
    
    try:
        if history_item:
            history_item.progress = progress
            history_item.duration = duration
            history_item.last_watched_at = datetime.utcnow()
        else:
            history_item = WatchHistory(
                user_id=user_id,
                media_id=media_id,
                media_type=media_type,
                progress=progress,
                duration=duration,
                season=season,
                episode=episode
            )
            db.session.add(history_item)
            
        db.session.commit()
        return jsonify({"message": "History updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    # Get recent history with pagination
    pagination = WatchHistory.query.filter_by(user_id=user_id).order_by(WatchHistory.last_watched_at.desc()).paginate(page=page, per_page=limit, error_out=False)
    
    from lib.tmdb_client import TMDBClient
    client = TMDBClient()

    history_list = []
    for item in pagination.items:
        details = client.get_media_basic_details(item.media_id, item.media_type)
        details.update({
            "progress": item.progress,
            "duration": item.duration,
            "season": item.season,
            "episode": item.episode,
            "last_watched_at": item.last_watched_at.isoformat()
        })
        history_list.append(details)
        
    return jsonify({
        "history": history_list,
        "page": pagination.page,
        "total_pages": pagination.pages,
        "total_results": pagination.total
    }), 200

@jwt_required()
def get_history_by_media(media_id):
    user_id = get_jwt_identity()
    
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    pagination = WatchHistory.query.filter_by(user_id=user_id, media_id=media_id).order_by(WatchHistory.last_watched_at.desc()).paginate(page=page, per_page=limit, error_out=False)
    
    if not pagination.items:
        return jsonify({
            "history": [],
            "page": page,
            "total_pages": 0,
            "total_results": 0
        }), 200
        
    from lib.tmdb_client import TMDBClient
    client = TMDBClient()

    history_list = []
    for item in pagination.items:
        details = client.get_media_basic_details(item.media_id, item.media_type)
        details.update({
            "progress": item.progress,
            "duration": item.duration,
            "season": item.season,
            "episode": item.episode,
            "last_watched_at": item.last_watched_at.isoformat()
        })
        history_list.append(details)
        
    return jsonify({
        "history": history_list,
        "page": pagination.page,
        "total_pages": pagination.pages,
        "total_results": pagination.total
    }), 200
