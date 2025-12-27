import lib.sources.torrentio as torrentio
from lib.constant import QUALITY_4K, QUALITY_720P, QUALITY_1080P, QUALITY_OTHER


class SourceAggregator:
    _register = {}
    _supported_sources = {
        "torrentio": torrentio.TorrentioSource,
    }

    @classmethod
    def supportedSource(cls, source):
        return source in cls._supported_sources

    @classmethod
    def register(cls, source, *args, **kwargs):
        try:
            source_obj = cls._supported_sources[source.lower()](*args, **kwargs)
            cls._register[source_obj.type] = source_obj
        except KeyError:
            raise ValueError(f"Unknown Source: {source}")

    @classmethod
    def getSource(cls, source):
        if source not in cls._register:
            raise Exception("Source is not registered")
        return cls._register[source]

    @classmethod
    def streams(cls, media_id, category, server_url):
        response_structure = {
            "streams": {
                QUALITY_4K: [],
                QUALITY_1080P: [],
                QUALITY_720P: [],
                QUALITY_OTHER: [],
            }
        }
        for source in cls._register:
            source_streams = cls._register[source].getStreams(
                media_id, category, server_url
            )
            response_structure["streams"][QUALITY_4K] += source_streams["streams"][
                QUALITY_4K
            ]
            response_structure["streams"][QUALITY_1080P] += source_streams["streams"][
                QUALITY_1080P
            ]
            response_structure["streams"][QUALITY_720P] += source_streams["streams"][
                QUALITY_720P
            ]
            response_structure["streams"][QUALITY_OTHER] += source_streams["streams"][
                QUALITY_OTHER
            ]

        return response_structure
