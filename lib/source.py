import base64
import json

import requests

QUALITY_4K = "4k"
QUALITY_1080P = "1080p"
QUALITY_720P = "720p"
QUALITY_OTHER = "other"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


class Source:
    def __init__(self) -> None:
        pass


class TorrentioSource(Source):
    def __init__(self, baseurl, options) -> None:
        super().__init__()
        self.baseurl = baseurl
        self.options = options
        self.type = "torrentio"

    def __getLink__(self, media_id, category, downloader):
        return f"{self.baseurl}/debridoptions={self.options}|{downloader.type}={downloader.token}/stream/{category}/{media_id}.json"

    def getStreams(self, media_id, category, server_url, downloader):
        response_structure = {
            "streams": {
                QUALITY_4K: [],
                QUALITY_1080P: [],
                QUALITY_720P: [],
                QUALITY_OTHER: [],
            }
        }
        request_link = self.__getLink__(media_id, category, downloader)
        req = requests.get(request_link, headers=HEADERS)
        response = json.loads(req.text)

        for stream in response["streams"]:
            if QUALITY_4K in stream["name"]:
                response_structure["streams"][QUALITY_4K].append(
                    self.__getStream__(stream, server_url, downloader.type)
                )
            elif QUALITY_1080P in stream["name"]:
                response_structure["streams"][QUALITY_1080P].append(
                    self.__getStream__(stream, server_url, downloader.type)
                )
            elif QUALITY_720P in stream["name"]:
                response_structure["streams"][QUALITY_720P].append(
                    self.__getStream__(stream, server_url, downloader.type)
                )
            else:
                response_structure["streams"][QUALITY_OTHER].append(
                    self.__getStream__(stream, server_url, downloader.type)
                )

        return response_structure

    def getPlayableStreams(self, media_id, downloader, options):
        encoded_hash = options["hash"]
        metadata = json.loads(base64.b64decode(encoded_hash).decode("utf-8"))

        response = requests.get(metadata["url"], headers=HEADERS, allow_redirects=False)
        media_id = response.headers["location"].split("?")[0].split("dld/")[1]
        media_streams = downloader.getTransCodeStreams("torrent", media_id)
        media_streams["original"] = metadata["url"]
        return media_streams

    def __getStream__(self, stream, server_url, downloader_type):
        metadata = stream["behaviorHints"]
        magnet_hash = stream["url"].split("/")[6]
        hash = {
            "filename": metadata["filename"],
            "filehash": metadata["videoHash"],
            "url": stream["url"],
        }
        base64_encoded = base64.b64encode(json.dumps(hash).encode("utf-8")).decode(
            "utf-8"
        )
        return {
            "title": stream["title"],
            "url": f"{server_url}/{magnet_hash}?hash={base64_encoded}&source_type={self.type}&downloader_type={downloader_type}",
        }
