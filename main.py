import os

from flask import Flask, jsonify, request
from flask_cors import CORS

import lib.downloader as downloader
import lib.source as source

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8090")
torrentio_base_url = os.environ.get("TORRENTIO_BASE_URL", "https://torrentio.strem.fun")
torbox_base_url = os.environ.get("TORBOX_BASE_URL", "https://api.torbox.app/v1")
torbox_api_key = os.environ.get("TORBOX_API_KEY", None)

torrentio_source = source.TorrentioSource(torrentio_base_url, "nodownloadlinks")
torbox_downloader = downloader.TorboxDownloader(torbox_base_url, torbox_api_key)

SOURCES = {torrentio_source.type: torrentio_source}
DOWNLOADERS = {torbox_downloader.type: torbox_downloader}

app = Flask(__name__)
CORS(app)


@app.route("/health/ping")
def health_check():
    return "pong"


@app.route("/movies/<imdbid>")
def get_movie_streams(imdbid):
    streams = torrentio_source.getStreams(
        imdbid, "movies", f"{BASE_URL}/stream", torbox_downloader
    )
    return jsonify(streams)


@app.route("/series/<imdbid>/<season>/<episode>")
def get_series_strems(imdbid, season, episode):
    streams = torrentio_source.getStreams(
        f"{imdbid}:{1 if season is None else season}:{1 if episode is None else episode}",
        "movies",
        f"{BASE_URL}/stream",
        torbox_downloader,
    )
    return jsonify(streams)


@app.route("/stream/<media_id>")
def get_stream(media_id):
    downloader_type = request.args.get("downloader_type", torbox_downloader.type)
    source_type = request.args.get("source_type", torrentio_source.type)
    metadata = request.args.get("hash")
    playable_streams = SOURCES[source_type].getPlayableStreams(
        media_id, DOWNLOADERS[downloader_type], {"hash": metadata}
    )
    return jsonify(playable_streams)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
