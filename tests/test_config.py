import os
import boto3
import pytest

from typing import Any, Union
from unittest.mock import patch
from flask import Flask
from flask_environment_manager.environment_manager import EnvironmentManager
from moto import mock_ssm


def setup_mock_ssm() -> None:
    client = boto3.client("ssm", region_name="eu-west-2")
    values = [
        dict(Name="/test", Type="string", Value="9ce10572-a1a4-422c-9cf1-d4b45ecd93c2"),
        dict(
            Name="/parent/child",
            Type="string",
            Value="27698a22-c47c-4457-a6b6-907051b4534a",
        ),
    ]
    for value in values:
        client.put_parameter(**value)


class TestEnvironmentManager:
    @mock_ssm
    def test_building_value_dict(self, app: Flask) -> None:
        setup_mock_ssm()
        env_man = EnvironmentManager(app, "/", "eu-west-2")
        data = env_man._get_ssm_values()
        assert data == {
            "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
            "child": "27698a22-c47c-4457-a6b6-907051b4534a",
        }

    @pytest.mark.parametrize(
        "whitelist, values, expected",
        [
            (
                ["test", "child"],
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
            ),
            (
                ["test"],
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                },
            ),
            (
                [],
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                {},
            ),
        ],
    )
    def test_parsing_whitelist(
        self,
        whitelist: list,
        values: Union[dict, os._Environ],
        expected: dict,
        app: Flask,
    ) -> None:
        app.config["ENV_OVERRIDE_WHITELIST"] = whitelist
        env_man = EnvironmentManager(app)
        env_man.parse_whitelist(values)
        for key in values.keys():
            assert app.config.get(key) == expected.get(key)

    @pytest.mark.parametrize(
        "mock_config, mock_value, expected_missing, expected_mismatched",
        [
            (
                {},
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                ["test", "child"],
                ["test", "child"],
            ),
            (
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                [],
                [],
            ),
            (
                {
                    "test": "9ce10573-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                [],
                ["test"],
            ),
            (
                {
                    "test": "9ce10573-a1a4-422c-9cf1-d4b45ecd93c2",
                },
                {
                    "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
                    "child": "27698a22-c47c-4457-a6b6-907051b4534a",
                },
                ["child"],
                ["test", "child"],
            ),
        ],
    )
    @patch(
        "flask_environment_manager.environment_manager.EnvironmentManager._get_ssm_values"
    )
    def test_environment_comparisons(
        self,
        mock_get_ssm_values: Any,
        mock_config: Any,
        mock_value: dict,
        expected_missing: list,
        expected_mismatched: list,
        app: Flask,
    ) -> None:
        os.environ = mock_config
        mock_get_ssm_values.return_value = mock_value
        env_man = EnvironmentManager(app, "/", "eu-west-2")
        res = env_man.compare_env_and_ssm()
        assert res.get("missing") == expected_missing
        assert res.get("mismatched") == expected_mismatched

    @pytest.mark.parametrize(
        "value_in, value_out",
        [
            ("", ""),
            (True, True),
            (False, False),
            ("ON", True),
            ("OfF", False),
            ("FaLsE", False),
            ("true", True),
        ],
    )
    def test_coerce(
        self,
        value_in: Any,
        value_out: Any,
        app: Flask,
    ) -> None:
        env_man = EnvironmentManager(app)
        assert env_man.coerce_value(value_in) == value_out
