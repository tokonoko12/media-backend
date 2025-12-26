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
                "index": audio["index"],
                "hls-url": f"{hls_domain}/stream/{media_id}/null/{audio['index'] - 1}/playlist.m3u8?token={self.token}",
            }
        return value


class RealDebridDownloader(Downloader):
    def __init__(self, baseurl, token, mediafusion_proxy_base_url) -> None:
        super().__init__()
        self.baseurl = baseurl
        self.token = token
        self.mediafusion_proxy_base_url = mediafusion_proxy_base_url
        self.type = "realdebrid"

    def getTransCodeStreams(self, download_type, media_id, server_url):
        if download_type == "torrent":
            return self.__getTorrentTransCodeStreams__(media_id, server_url)
        return {"audios": {}}

    def getMediaId(self, url):
        return url.split("/d/")[1].split("/")[0][0:13]

    def proxifiedStreamManifest(self, manifest_type, url):
        proxy_url = f"{self.mediafusion_proxy_base_url}?d={url}&api_password=test123"
        req = requests.get(proxy_url, headers=HEADERS)
        proxied_manifest = req.text
        base_seq_url = url.split("?t=")[0].replace("full.mpd", "")
        proxied_base_seq_url = f"{self.mediafusion_proxy_base_url}?api_password=test123&amp;d={base_seq_url}"
        proxied_manifest = proxied_manifest.replace(base_seq_url, proxied_base_seq_url)
        return proxied_manifest

    def __getTorrentTransCodeStreams__(self, media_id, server_url):
        value = {"audios": {}, "downloader": self.type}
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
                "url": f"{server_url}?downloader_type={self.type}&url={transcode_model_url.replace('{audio}', audio)}",
            }
        return value
