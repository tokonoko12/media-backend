from lib.downloaders.realdebrid import RealDebridDownloader
from lib.downloaders.torbox import TorboxDownloader


class DownloadManager:
    _supported_downloader = {
        "torbox": TorboxDownloader,
        "realdebrid": RealDebridDownloader,
    }
    _register = {}

    @classmethod
    def supportedDownloader(cls, downloader):
        return downloader in cls._supported_downloader

    @classmethod
    def register(cls, downloader, *args, **kwargs):
        try:
            downloader_obj = cls._supported_downloader[downloader.lower()](
                *args, **kwargs
            )
            cls._register[downloader_obj.type] = downloader_obj
        except KeyError:
            raise ValueError(f"Unknown Downloader: {downloader}")

    @classmethod
    def getDownloader(cls, downloader):
        if downloader is None and downloader not in cls._register:
            raise Exception("Downloader is not registered")
        return cls._register[downloader]
