import os

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

import lib.downloader as downloader
import lib.source as source

load_dotenv()

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8090")
torrentio_base_url = os.environ.get("TORRENTIO_BASE_URL", "https://torrentio.strem.fun")
torbox_base_url = os.environ.get("TORBOX_BASE_URL", "https://api.torbox.app/v1")
torbox_api_key = os.environ.get("TORBOX_API_KEY", None)
media_fusion_proxy = os.environ.get("MEDIAFUSION_PROXY", None)

real_debrid_base_url = os.environ.get(
    "REAL_DEBRID_BASE_URL", "https://app.real-debrid.com/rest/1.0"
)
real_debrid_api_key = os.environ.get("REAL_DEBRID_TOKEN", None)

torrentio_source = source.TorrentioSource(torrentio_base_url, "nodownloadlinks")
torbox_downloader = downloader.TorboxDownloader(torbox_base_url, torbox_api_key)
real_debrid_downloader = downloader.RealDebridDownloader(
    real_debrid_base_url, real_debrid_api_key, media_fusion_proxy
)

SOURCES = {torrentio_source.type: torrentio_source}
DOWNLOADERS = {
    torbox_downloader.type: torbox_downloader,
    real_debrid_downloader.type: real_debrid_downloader,
}

app = Flask(__name__)
CORS(app)


@app.route("/health/ping")
def health_check():
    return "pong"


@app.route("/movies/<imdbid>")
def get_movie_streams(imdbid):
    streams = torrentio_source.getStreams(
        imdbid, "movies", f"{BASE_URL}/stream", real_debrid_downloader
    )
    return jsonify(streams)


@app.route("/series/<imdbid>/<season>/<episode>")
def get_series_strems(imdbid, season, episode):
    streams = torrentio_source.getStreams(
        f"{imdbid}:{1 if season is None else season}:{1 if episode is None else episode}",
        "series",
        f"{BASE_URL}/stream",
        real_debrid_downloader,
    )
    return jsonify(streams)


@app.route("/stream/<media_id>")
def get_stream(media_id):
    downloader_type = request.args.get("downloader_type", real_debrid_downloader.type)
    source_type = request.args.get("source_type", real_debrid_downloader.type)
    metadata = request.args.get("hash")
    playable_streams = SOURCES[source_type].getPlayableStreams(
        media_id,
        DOWNLOADERS[downloader_type],
        {"hash": metadata, "serverurl": f"{BASE_URL}/streaming/playlist.mpd"},
    )
    return jsonify(playable_streams)


@app.route("/streaming/playlist.mpd")
def serve_mpd():
    url = request.args.get("url", "")
    t = request.args.get("t", 0)
    downloader_type = request.args.get("downloader_type", real_debrid_downloader.type)
    proxified_manifest = DOWNLOADERS[downloader_type].proxifiedStreamManifest(
        "mpd", f"{url}?t={t}"
    )
    # req = requests.get(stream["stream_url"], headers=headers)
    # # return redirect(stream["stream_url"], code=302)
    # mpd_file = req.text
    # mpd_file = mpd_file.replace(
    #     stream["seq_url"], f"{BASE_URL}/streaming/mpd/{stream_id}/"
    # )
    return Response(proxified_manifest, mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
