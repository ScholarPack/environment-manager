import os
from flask import Flask


class EnvironmentManager:
    """
    Utility functions to assist during app creation
    """

    enabled_values = ["true", "on"]
    disabled_values = ["false", "off"]

    @classmethod
    def parse_whitelist(cls, app: Flask):
        """
        Consolidates environment variables with app.config values
        Only sets values on the whitelist
        :param app: Flask app instance
        :return: Boolean task status
        """
        try:
            whitelist = app.config["ENV_OVERRIDE_WHITELIST"]
        except KeyError:
            app.logger.debug("Whitelist missing")
            whitelist = None

        if whitelist is not None:
            for key in whitelist:
                default = None
                if key in app.config.keys():
                    default = app.config[key]

                if os.environ.get(key, default) is not None:
                    app.config[key] = cls.coerce_value(os.environ.get(key, default))
        else:
            app.logger.debug("No whitelist to process")

        return True

    @classmethod
    def coerce_value(cls, value):
        """
        Coerce the passed value to a boolean if it is of the correct value.
        :param value: The value to coerce.
        """
        if type(value) is str:
            if value.lower() in cls.enabled_values:
                return True

            if value.lower() in cls.disabled_values:
                return False

        return value
