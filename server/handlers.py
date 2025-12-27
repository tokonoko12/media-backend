from flask import Response, jsonify, request

from lib.downloadmanager import DownloadManager
from lib.sourceaggregator import SourceAggregator
from flask_jwt_extended import jwt_required
from lib.sourceaggregator import SourceAggregator
from flask_jwt_extended import jwt_required
from lib.tmdb_client import TMDBClient

client = TMDBClient()
def health_check():
    return "pong"

@jwt_required()
def get_movie_streams(imdbid, base_server_url):
    lookup_id = imdbid
    if imdbid.startswith("tmdb:"):
        tmdb_id = imdbid.split(":")[1]
        resolved_id = client.get_external_id(tmdb_id, "movie")
        if resolved_id:
            lookup_id = resolved_id
    
    streams = SourceAggregator.streams(lookup_id, "movies", f"{base_server_url}/streaming")
    return jsonify(streams)

@jwt_required()
def get_series_strems(imdbid, season, episode, base_server_url):
    lookup_id = imdbid
    if imdbid.startswith("tmdb:"):
        tmdb_id = imdbid.split(":")[1]
        resolved_id = client.get_external_id(tmdb_id, "tv")
        if resolved_id:
            lookup_id = resolved_id

    streams = SourceAggregator.streams(
        f"{lookup_id}:{1 if season is None else season}:{1 if episode is None else episode}",
        "series",
        f"{base_server_url}/streaming",
    )
    return jsonify(streams)

@jwt_required()
def get_stream(media_id, base_server_url):
    downloader_type = request.args.get("downloader_type", None)
    source_type = request.args.get("source_type", None)
    metadata = request.args.get("hash")
    downloader_obj = DownloadManager.getDownloader(downloader_type)
    source_obj = SourceAggregator.getSource(source_type)
    playable_streams = source_obj.getPlayableStreams(
        media_id,
        downloader_obj,
        {"hash": metadata, "serverurl": f"{base_server_url}/streaming/playlist.mpd"},
    )
    return jsonify(playable_streams)

def serve_mpd():
    url = request.args.get("url", "")
    t = request.args.get("t", 0)
    downloader_type = request.args.get("downloader_type", None)
    downloader_obj = DownloadManager.getDownloader(downloader_type)

    proxified_manifest = downloader_obj.proxifiedStreamManifest("mpd", f"{url}?t={t}")
    return Response(proxified_manifest, mimetype="application/xml")
