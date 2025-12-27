from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import jwt_required, get_jwt_identity
from lib.tmdb_client import TMDBClient
from lib.models import WatchHistory, Watchlist

client = TMDBClient()

@jwt_required()
def get_home_catalog():
    try:
        # Fetch data concurrently in a real app, but sequential here is fine for now
        featured = client.get_trending_home()[:5] # Top 5 for hero
        
        # Sections Data
        recent = client.get_now_playing()
        bollywood = client.get_bollywood_movies()
        global_movies = client.get_popular_movies()
        south = client.get_south_indian_movies()
        world_tv = client.get_popular_series()
        top_rated = client.get_top_rated()
        
        return jsonify({
            "featured": featured,
            "sections": [
                {
                    "title": "Recent Arrivals",
                    "items": recent
                },
                {
                    "title": "Bollywood Hits",
                    "items": bollywood
                },
                {
                    "title": "Global Hits",
                    "items": global_movies
                },
                 {
                    "title": "South Indian Cinema",
                    "items": south
                },
                {
                    "title": "World TV Hits",
                    "items": world_tv
                },
                {
                    "title": "Top Rated Archive",
                    "items": top_rated
                }
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_movies_catalog():
    try:
        popular = client.get_popular_movies()
        action = client.get_movies_by_genre(28)['results']
        comedy = client.get_movies_by_genre(35)['results']
        scifi = client.get_movies_by_genre(878)['results']
        horror = client.get_movies_by_genre(27)['results']
        animation = client.get_movies_by_genre(16)['results']
        romance = client.get_movies_by_genre(10749)['results']

        return jsonify({
            "sections": [
                {"title": "Popular Movies", "items": popular},
                {"title": "Action", "items": action},
                {"title": "Comedy", "items": comedy},
                {"title": "Sci-Fi", "items": scifi},
                {"title": "Horror", "items": horror},
                {"title": "Animation", "items": animation},
                {"title": "Romance", "items": romance}
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_series_catalog():
    try:
        popular = client.get_popular_series()
        action_adv = client.get_series_by_genre(10759)['results']
        comedy = client.get_series_by_genre(35)['results']
        scifi_fantasy = client.get_series_by_genre(10765)['results']
        animation = client.get_series_by_genre(16)['results']
        drama = client.get_series_by_genre(18)['results']

        return jsonify({
            "sections": [
                 {"title": "Popular Series", "items": popular},
                 {"title": "Action & Adventure", "items": action_adv},
                 {"title": "Comedy", "items": comedy},
                 {"title": "Sci-Fi & Fantasy", "items": scifi_fantasy},
                 {"title": "Animation", "items": animation},
                 {"title": "Drama", "items": drama}
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_movie_detail(tmdb_id):
    try:
        data = client.get_movie_details(tmdb_id)
        # Add streams url
        # Use real IMDB ID if available, else fallback to tmdb:ID
        imdb_id = data.get("external_ids", {}).get("imdb_id")
        unique_id = imdb_id if imdb_id else f"tmdb:{tmdb_id}"
        
        data["streams_url"] = f"{request.host_url}streams/movies/{unique_id}"
        
        # Remove external_ids from the response as per user request
        data.pop("external_ids", None)
        
        # Inject Watch History
        user_id = get_jwt_identity()
        
        # Check multiple ID variants (IMDb, tmdb:ID, raw ID) to ensure we find the history
        possible_ids = {unique_id, f"tmdb:{tmdb_id}", str(tmdb_id)}
        
        history_item = WatchHistory.query.filter(
            WatchHistory.user_id == user_id, 
            WatchHistory.media_id.in_(possible_ids)
        ).first()
        
        if history_item:
            data["watched_duration"] = history_item.progress
        else:
             data["watched_duration"] = 0
            
        # Check Watchlist
        watchlist_item = Watchlist.query.filter(
            Watchlist.user_id == user_id,
            Watchlist.media_id.in_(possible_ids)
        ).first()
        data["in_watchlist"] = bool(watchlist_item)
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_series_detail(tmdb_id):
    try:
        data = client.get_series_details(tmdb_id)
        
        # Remove external_ids from the response as per user request
        data.pop("external_ids", None)
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_season_details(tmdb_id, season_number):
    try:
        data = client.get_season_details(tmdb_id, season_number)
        
        # Get Extenal ID for the show to build stream url
        show_imdb_id = client.get_external_id(tmdb_id, "tv")
        unique_id = show_imdb_id if show_imdb_id else f"tmdb:{tmdb_id}"
        
        # Add streams_url to each episode
        # Also inject watch history
        user_id = get_jwt_identity()
        
        # Connect to Series ID for watchlist check
        # possible_ids contains the Series IDs
        possible_ids = {unique_id, f"tmdb:{tmdb_id}", str(tmdb_id)}
        
        watchlist_item = Watchlist.query.filter(
            Watchlist.user_id == user_id,
            Watchlist.media_id.in_(possible_ids)
        ).first()
        data["in_watchlist"] = bool(watchlist_item)

        history_items = WatchHistory.query.filter(
            WatchHistory.user_id == user_id,
            WatchHistory.media_id.in_(possible_ids),
            WatchHistory.season == season_number
        ).all()
        
        # Create a map for O(1) lookup: episode_number -> history_item
        # If duplicates exist (e.g. history for 'tt123' and '83533'), the last one processed wins
        # Ideally we'd merge or take the most recent, but simple map override is acceptable for now
        history_map = {item.episode: item for item in history_items}

        for episode in data.get("episodes", []):
            ep_num = episode.get("episode_number")
            episode["streams_url"] = f"{request.host_url}streams/series/{unique_id}/{season_number}/{ep_num}"
            
            # Inject history if exists, else default
            watched_duration = 0
            
            if ep_num in history_map:
                h_item = history_map[ep_num]
                watched_duration = h_item.progress
            
            episode["watched_duration"] = watched_duration
            
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def search_catalog():
    try:
        query = request.args.get("q")
        page = request.args.get("page", 1, type=int)
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
            
        result = client.search_multi(query, page=page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_genre_movies(genre_id):
    try:
        page = request.args.get("page", 1, type=int)
        result = client.get_movies_by_genre(genre_id, page=page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jwt_required()
def get_genre_series(genre_id):
    try:
        page = request.args.get("page", 1, type=int)
        result = client.get_series_by_genre(genre_id, page=page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
