import os
from flask import Flask
import boto3


class EnvironmentManager:
    """
    Utility functions to assist during app creation
    """

    _enabled_values = ["true", "on"]
    _disabled_values = ["false", "off"]

    def __init__(self, app: Flask, path: str = "", region_name: str = ""):
        """
        :param app: The Flask app instance
        :param path: Path of the parameters in the SSM instance to read
        :param region_name: The region of the SSM instance
        """
        self._app = app
        self._path = path
        self._region_name = region_name

    def compare_env_and_ssm(self):
        """
        Compare the environment to the SSM parameters.
        Log an error where a key in the environment is not in SSM.
        """
        ssm = self._get_ssm_values()
        for key in self._app.config.keys():
            if key not in ssm:
                self._app.logger.error(f"{key} not found in SSM")

    def load_ssm_into_config(self):
        """
        Load the SSM parameters into the Flask app config.
        """
        ssm = self._get_ssm_values()
        for key in ssm:
            self._app.config[key] = self.coerce_value(ssm.get(key))

    def _get_ssm_values(self):
        """
        Get all values in a given path from SSM.
        The name of the keys in the return dict is the final
        part of the parameter path, e.g '/a/param/path' will
        be stored in the dict as 'path'
        :returns: A dict of parameter names and values.
        """
        client = boto3.client("ssm", region_name=self._region_name)
        more_parameters = True
        ssm_values: dict = {}
        ssm_repsonse: dict = {}
        while more_parameters:
            if ssm_repsonse.get("NextToken"):
                ssm_repsonse = client.get_parameters_by_path(
                    Path=self._path,
                    Recursive=True,
                    NextToken=ssm_repsonse.get("NextToken"),
                )
            else:
                ssm_repsonse = client.get_parameters_by_path(
                    Path=self._path, Recursive=True
                )

            parameters = ssm_repsonse.get("Parameters", [])
            for param in parameters:
                name = param.get("Name")
                if name:
                    path_parts = param["Name"].split("/")
                    if len(path_parts) > 0:
                        name = path_parts[-1]

                value = param.get("Value")
                ssm_values[name] = value

            if not ssm_repsonse.get("NextToken"):
                more_parameters = False

        return ssm_values

    def parse_whitelist(self):
        """
        Consolidates environment variables with app.config values
        Only sets values on the whitelist
        :return: Boolean task status
        """
        try:
            whitelist = self._app.config["ENV_OVERRIDE_WHITELIST"]
        except KeyError:
            self._app.logger.debug("Whitelist missing")
            whitelist = None

        if whitelist is not None:
            for key in whitelist:
                default = None
                if key in self._app.config.keys():
                    default = self._app.config[key]

                if os.environ.get(key, default) is not None:
                    self._app.config[key] = self.coerce_value(
                        os.environ.get(key, default)
                    )
        else:
            self._app.logger.debug("No whitelist to process")

        return True

    def coerce_value(self, value):
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
