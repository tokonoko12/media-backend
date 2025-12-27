from lib.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    preferences = db.relationship('UserPreferences', backref='user', uselist=False, cascade="all, delete-orphan")
    history = db.relationship('WatchHistory', backref='user', lazy='dynamic')
    watchlist = db.relationship('Watchlist', backref='user', lazy='dynamic', cascade="all, delete-orphan")

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.String(50), nullable=False)
    media_type = db.Column(db.String(20), nullable=False) # 'movie' or 'series'
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'media_id', name='_user_media_uc'),)

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    preferences = db.Column(JSONB, default={})
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WatchHistory(db.Model):
    __tablename__ = 'watch_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.String(50), nullable=False)
    media_type = db.Column(db.String(20), nullable=False) # 'movie' or 'series'
    progress = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer)
    season = db.Column(db.Integer) 
    episode = db.Column(db.Integer)
    last_watched_at = db.Column(db.DateTime, default=datetime.utcnow)
