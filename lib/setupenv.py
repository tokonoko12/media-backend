import os

from lib.downloadmanager import DownloadManager
from lib.sourceaggregator import SourceAggregator


def setupProxy(proxy_env):
    if proxy_env == "enable":
        proxy_base_url = os.environ.get("PROXY_BASE_URL", None)
        if not proxy_base_url:
            raise Exception("Proxy is enabled but its details not present in env")
        return proxy_base_url
    return None


def setupDownloaders(downloaders_env, proxy_url):
    downloaders_map = {}
    downloaders = downloaders_env.split(",")
    for downloader in downloaders:
        if not DownloadManager.supportedDownloader(downloader):
            raise Exception("Unsupported Downloader")

        downloader_base_url = os.environ.get(f"{downloader.upper()}_BASE_URL", None)
        downloader_token = os.environ.get(f"{downloader.upper()}_TOKEN", None)

        if not downloader_base_url and not downloader_token:
            raise Exception(
                f"{downloader.upper()} Downloader details not present in env"
            )
        DownloadManager.register(
            downloader, downloader_base_url, downloader_token, proxy_url
        )
    return downloaders_map


def setupSources(sources_env):
    sorces_map = {}
    sources = sources_env.split(",")
    for source in sources:
        if not SourceAggregator.supportedSource(source):
            raise Exception("Unsupported Source")

        source_base_url = os.environ.get(f"{source.upper()}_URL", None)
        source_downloader = os.environ.get(f"{source.upper()}_DOWNLOADER", None)

        if not source_base_url:
            raise Exception(f"{source} Source details not present in env")
        SourceAggregator.register(source, source_base_url, source_downloader)
    return sorces_map


def setupEnv():
    DOWNLOADERS = os.environ.get("DOWNLOADERS", "realdebrid")
    SOURCES = os.environ.get("SOURCES", "torrentio")
    PROXY = os.environ.get("PROXY", "disable")

    proxy_url = setupProxy(PROXY)
    setupDownloaders(DOWNLOADERS, proxy_url)
    setupSources(SOURCES)
