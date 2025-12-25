import json

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


class Downloader:
    def __init__(self) -> None:
        pass


class TorboxDownloader(Downloader):
    def __init__(self, baseurl, token) -> None:
        super().__init__()
        self.baseurl = baseurl
        self.token = token
        self.type = "torbox"

    def getTransCodeStreams(self, download_type, media_id):
        if download_type == "torrent":
            return self.__getTorrentTransCodeStreams__(media_id)
        return {"audios": {}}

    def __getTorrentTransCodeStreams__(self, media_id):
        value = {"audios": {}}
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
                "index": audio["index"],
                "hls-url": f"{hls_domain}/stream/{media_id}/null/{audio['index'] - 1}/playlist.m3u8?token={self.token}",
            }
        return value
