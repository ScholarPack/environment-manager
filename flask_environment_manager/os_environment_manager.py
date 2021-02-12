import os

from flask import Flask
from flask_environment_manager.whitelist_parser import WhitelistParser


class OsEnvironmentManager:
    def __init__(
        self,
        app: Flask,
    ):
        """
        :param app: The Flask app instance
        """
        self._app = app

    def load_into_config(self) -> None:
        """
        Load the OS Environment values into the Flask app config.
        """
        WhitelistParser(self._app, dict(os.environ)).parse()
