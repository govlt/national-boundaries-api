import os

from uvicorn_worker import UvicornWorker


class ApiWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "auto", "http": "auto", "root_path": os.getenv("ROOT_PATH", "")}
