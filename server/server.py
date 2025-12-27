from flask import Flask
from datetime import timedelta
from flask_cors import CORS
import os
from lib.database import db, bcrypt, jwt
from lib import models # Register models

from server.handlers import (
    get_movie_streams,
    get_series_strems,
    get_stream,
    health_check,
    serve_mpd,
)
from server.auth_handlers import login, register, logout, get_current_user
from server.watchlist_handlers import add_to_watchlist, get_watchlist, remove_from_watchlist
from server.history_handlers import update_history, get_history, get_history_by_media
from server.history_handlers import update_history, get_history, get_history_by_media
from server.catalog_handlers import (
    get_home_catalog, 
    get_movies_catalog, 
    get_series_catalog,
    get_movie_detail,
    get_series_detail,
    get_movie_detail,
    get_series_detail,
    get_season_details,
    search_catalog
)


class Server:
    def __init__(self, server_base_url, port=None, host=None):
        self.server_base_url = server_base_url
        self.port = port or 8090
        self.host = host or "0.0.0.0"
        self.app = Flask(__name__)
        CORS(self.app)
        
        # configuration
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/db")
        self.app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-key")
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
        
        # init extensions
        db.init_app(self.app)
        bcrypt.init_app(self.app)
        jwt.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()

    def serve(self):
        self.app.run(host=self.host, port=self.port)

    def registerRoutes(self):
        self.app.add_url_rule("/health/ping", "health_check", health_check)
        self.app.add_url_rule(
            "/streams/movies/<imdbid>",
            "get_movie_streams",
            lambda imdbid: get_movie_streams(imdbid, self.server_base_url),
        )

        self.app.add_url_rule(
            "/streams/series/<imdbid>/<season>/<episode>",
            "get_series_streams",
            lambda imdbid, season, episode: get_series_strems(
                imdbid, season, episode, self.server_base_url
            ),
        )

        self.app.add_url_rule(
            "/streaming/<media_id>",
            "get_stream",
            lambda media_id: get_stream(media_id, self.server_base_url),
        )

        self.app.add_url_rule(
            "/streaming/playlist.mpd",
            "serve_mpd",
            serve_mpd,
        )

        self.app.add_url_rule("/auth/register", "register", register, methods=["POST"])
        self.app.add_url_rule("/auth/login", "login", login, methods=["POST"])
        self.app.add_url_rule("/auth/logout", "logout", logout, methods=["POST"])
        self.app.add_url_rule("/auth/me", "get_current_user", get_current_user, methods=["GET"])

        self.app.add_url_rule("/watchlist", "add_to_watchlist", add_to_watchlist, methods=["POST"])
        self.app.add_url_rule("/watchlist", "get_watchlist", get_watchlist, methods=["GET"])
        self.app.add_url_rule("/watchlist/<media_id>", "remove_from_watchlist", remove_from_watchlist, methods=["DELETE"])

        self.app.add_url_rule("/history", "update_history", update_history, methods=["POST"])
        self.app.add_url_rule("/history", "get_history", get_history, methods=["GET"])
        self.app.add_url_rule("/history/<media_id>", "get_history_by_media", get_history_by_media, methods=["GET"])

        self.app.add_url_rule("/catalog/home", "get_home_catalog", get_home_catalog, methods=["GET"])
        self.app.add_url_rule("/catalog/movies", "get_movies_catalog", get_movies_catalog, methods=["GET"])
        self.app.add_url_rule("/catalog/series", "get_series_catalog", get_series_catalog, methods=["GET"])
        self.app.add_url_rule("/details/movies/<tmdb_id>", "get_movie_detail", get_movie_detail, methods=["GET"])
        self.app.add_url_rule("/details/series/<tmdb_id>", "get_series_detail", get_series_detail, methods=["GET"])
        self.app.add_url_rule("/details/series/<tmdb_id>", "get_series_detail", get_series_detail, methods=["GET"])
        self.app.add_url_rule("/details/series/<tmdb_id>/season/<season_number>", "get_season_details", get_season_details, methods=["GET"])
        self.app.add_url_rule("/search", "search_catalog", search_catalog, methods=["GET"])
