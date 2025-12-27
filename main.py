import os

from dotenv import load_dotenv

load_dotenv()

from lib.setupenv import setupEnv
from server.server import Server
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8090")


def main():
    setupEnv()
    server = Server(BASE_URL)
    server.registerRoutes()
    server.serve()


if __name__ == "__main__":
    main()
