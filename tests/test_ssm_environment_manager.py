import os
import boto3
import pytest

from typing import Any
from unittest.mock import patch
from flask import Flask
from flask_environment_manager import SsmEnvironmentManager
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


class TestSsmEnvironmentManager:
    @mock_ssm
    def test_building_value_dict(self, app: Flask) -> None:
        setup_mock_ssm()
        env_man = SsmEnvironmentManager(app, "/", "eu-west-2")
        data = env_man._get_ssm_values()
        assert data == {
            "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
            "child": "27698a22-c47c-4457-a6b6-907051b4534a",
        }

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
        "flask_environment_manager.ssm_environment_manager.SsmEnvironmentManager._get_ssm_values"
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
        env_man = SsmEnvironmentManager(app, "/", "eu-west-2")
        res = env_man.compare_env_and_ssm()
        assert res.get("missing") == expected_missing
        assert res.get("mismatched") == expected_mismatched
