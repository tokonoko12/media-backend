import base64
import json

import requests

import lib.sources.source as source
from lib.constant import HEADERS, QUALITY_4K, QUALITY_720P, QUALITY_1080P, QUALITY_OTHER


class TorrentioSource(source.Source):
    def __init__(self, baseurl, downloader) -> None:
        super().__init__()
        self.baseurl = baseurl
        self.downloader = downloader
        self.type = "torrentio"

    def __getStreamsFetchLink__(self, media_id, category):
        return f"{self.baseurl}/stream/{category}/{media_id}.json"

    def getStreams(self, media_id, category, server_url):
        response_structure = {
            "streams": {
                QUALITY_4K: [],
                QUALITY_1080P: [],
                QUALITY_720P: [],
                QUALITY_OTHER: [],
            }
        }
        request_link = self.__getStreamsFetchLink__(media_id, category)
        req = requests.get(request_link, headers=HEADERS)

        if not req.status_code == 200:
            return response_structure

        response = json.loads(req.text)
        for stream in response["streams"]:
            if QUALITY_4K in stream["name"]:
                response_structure["streams"][QUALITY_4K].append(
                    self.__getStream__(stream, server_url, self.downloader)
                )
            elif QUALITY_1080P in stream["name"]:
                response_structure["streams"][QUALITY_1080P].append(
                    self.__getStream__(stream, server_url, self.downloader)
                )
            elif QUALITY_720P in stream["name"]:
                response_structure["streams"][QUALITY_720P].append(
                    self.__getStream__(stream, server_url, self.downloader)
                )
            else:
                response_structure["streams"][QUALITY_OTHER].append(
                    self.__getStream__(stream, server_url, self.downloader)
                )

        return response_structure

    def getPlayableStreams(self, media_id, downloader, options):
        encoded_hash = options["hash"]
        metadata = json.loads(base64.b64decode(encoded_hash).decode("utf-8"))

        response = requests.get(metadata["url"], headers=HEADERS, allow_redirects=False)
        media_id = downloader.getMediaId(response.headers["location"])
        media_streams = downloader.getTransCodeStreams(
            "torrent", media_id, options.get("serverurl")
        )
        media_streams["original"] = metadata["url"]
        return media_streams

    def __getStream__(self, stream, server_url, downloader_type):
        metadata = stream["behaviorHints"]
        magnet_hash = stream["url"].split("/")[6]
        hash = {
            "filename": metadata.get("filename"),
            "filehash": metadata.get("videoHash"),
            "url": stream["url"],
        }
        base64_encoded = base64.b64encode(json.dumps(hash).encode("utf-8")).decode(
            "utf-8"
        )
        return {
            "title": stream["title"],
            "url": f"{server_url}/{magnet_hash}?hash={base64_encoded}&source_type={self.type}&downloader_type={downloader_type}",
        }
