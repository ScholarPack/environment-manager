from flask import Flask
from typing import Any


class WhitelistParser:
    _enabled_values = ["true", "on"]
    _disabled_values = ["false", "off"]

    def __init__(self, app: Flask, data_source: dict):
        """
        :param app: The flask app instance.
        :param data_source: The data source to parse the whitelist against
        """
        self._app = app
        self._data_source = data_source

    def parse(self) -> bool:
        """
        Consolidates the source with app.config values
        Only sets values on the whitelist
        :return: Boolean task status
        """
        try:
            whitelist = self._app.config["ENV_OVERRIDE_WHITELIST"]
        except KeyError:
            self._app.logger.debug("No whitelist to process")
            whitelist = None

        if whitelist is not None:
            for key in whitelist:
                default = None
                if key in self._app.config.keys():
                    default = self._app.config[key]

                if self._data_source.get(key, default) is not None:
                    self._app.config[key] = self._coerce_value(
                        self._data_source.get(key, default)
                    )

        return True

    def _coerce_value(self, value: Any) -> Any:
        """
        Coerce the passed value to a boolean if it is of the correct value.
        :param value: The value to coerce.
        """
        if type(value) is str:
            if value.lower() in self._enabled_values:
                return True

            if value.lower() in self._disabled_values:
                return False

        return value
