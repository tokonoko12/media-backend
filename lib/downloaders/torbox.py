import json

import requests

from lib.constant import HEADERS
from lib.downloaders.downloader import Downloader


class TorboxDownloader(Downloader):
    def __init__(self, baseurl, token) -> None:
        super().__init__()
        self.baseurl = baseurl
        self.token = token
        self.type = "torbox"

    def getTransCodeStreams(self, download_type, media_id, server_url: None):
        if download_type == "torrent":
            return self.__getTorrentTransCodeStreams__(media_id)
        return {"audios": {}}

    def getMediaId(self, url):
        return url.split("?")[0].split("dld/")[1]

    def __getTorrentTransCodeStreams__(self, media_id):
        value = {"audios": {}, "downloader": self.type}
        hls_domain = "https://flux-003.wnam.tb-cdn.io"
        request_link = f"{self.baseurl}/api/stream/getstreamdata"
        req = requests.get(
            request_link,
            headers=HEADERS,
            params={"presigned_token": media_id, "token": self.token},
        )
        response = json.loads(req.text)

        for audio in response["data"]["metadata"]["audios"]:
            value["audios"][f"{audio['language']}-{audio['index']}"] = {
                "language": audio["language_full"],
                "url": f"{hls_domain}/stream/{media_id}/null/{audio['index'] - 1}/playlist.m3u8?token={self.token}",
            }
        return value
