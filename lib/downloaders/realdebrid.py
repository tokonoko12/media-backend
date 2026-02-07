import json

import requests

from lib.constant import HEADERS
from lib.downloaders.downloader import Downloader
import base64

class RealDebridDownloader(Downloader):
    def __init__(self, baseurl, token, proxy_url) -> None:
        super().__init__()
        self.baseurl = baseurl
        self.token = token
        self.proxy_url = proxy_url
        self.type = "realdebrid"

    def getTransCodeStreams(self, download_type, media_id, server_url):
        if download_type == "torrent":
            return self.__getTorrentTransCodeStreams__(media_id, server_url)
        return {"audios": {}}

    def getMediaId(self, url):
        return url.split("/d/")[1].split("/")[0][0:13]

    def proxifiedStreamManifest(self, manifest_type, url):
        if self.proxy_url is None:
            raise Exception("Proxy is not setup")
        if manifest_type == "mpd":
            return self.__proxifiedMpdManifest__(url)

    def __proxifiedMpdManifest__(self, url):
        proxy_url = f"{self.proxy_url}?d={url}&api_password=test123"
        req = requests.get(proxy_url, headers=HEADERS)
        proxied_manifest = req.text
        base_seq_url = url.split("?t=")[0].replace("full.mpd", "")
        proxied_base_seq_url = (
            f"{self.proxy_url}?api_password=test123&amp;d={base_seq_url}"
        )
        proxied_manifest = proxied_manifest.replace(base_seq_url, proxied_base_seq_url)
        return proxied_manifest

    def __getTorrentTransCodeStreams__(self, media_id, server_url):
        value = {"audios": {}, "downloader": self.type, "duration": 0}
        request_link = f"{self.baseurl}/streaming/mediaInfos/{media_id}"
        req = requests.get(
            request_link,
            headers=HEADERS,
            params={"auth_token": self.token},
        )
        response = json.loads(req.text)

        transcode_model_url = response["modelUrl"]
        transcode_model_url = (
            transcode_model_url.replace("{subtitles}", "none")
            .replace("{audioCodec}", "aac")
            .replace("{quality}", "full")
            .replace("{format}", "mpd")
        )

        for audio in response["details"]["audio"]:
            value["audios"][audio] = {
                "language": response["details"]["audio"][audio]["lang"],
                "url": f"{server_url}?downloader_type={self.type}&url={base64.b64encode(transcode_model_url.replace('{audio}', audio).encode('utf-8')).decode("utf-8)}",
            }
        value["duration"] = response["duration"]
        return value
