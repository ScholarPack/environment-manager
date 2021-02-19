import os
import pytest

from typing import Any
from unittest.mock import patch
from flask import Flask
from flask_environment_manager import SsmEnvironmentManager


class TestSsmEnvironmentManager:
    @patch("boto3.client")
    def test_building_value_dict(
        self, mock_client: Any, app: Flask, ssm_client: Any
    ) -> None:
        mock_client.return_value = ssm_client
        env_man = SsmEnvironmentManager(app, region_name="eu-west-2")
        data = env_man._get_ssm_parameters("/")
        assert data == {
            "test": "9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
            "child": "27698a22-c47c-4457-a6b6-907051b4534a",
            "1": "49f48a53-e592-4bab-bf3a-7cfb08c584fb",
            "2": "e6c0fcf4-a67b-4375-a477-e7d72fce3420",
            "3": "fef47e26-b153-4ab8-a195-c7958e000491",
        }

    @pytest.mark.parametrize(
        "mock_value, mock_config, expected_missing, expected_mismatched",
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
        "flask_environment_manager.ssm_environment_manager.SsmEnvironmentManager._get_ssm_parameters"
    )
    def test_environment_comparisons(
        self,
        mock_get_ssm_parameters: Any,
        mock_value: dict,
        mock_config: Any,
        expected_missing: list,
        expected_mismatched: list,
        app: Flask,
    ) -> None:
        os.environ = mock_config
        mock_get_ssm_parameters.return_value = mock_value
        env_man = SsmEnvironmentManager(app, ["/"], "eu-west-2")
        res = env_man.compare_env_and_ssm()
        assert res.get("missing") == expected_missing
        assert res.get("mismatched") == expected_mismatched

    @patch("boto3.client")
    @pytest.mark.parametrize(
        "path, expected",
        [
            (
                ["/a", "/b"],
                {
                    "1": "49f48a53-e592-4bab-bf3a-7cfb08c584fb",
                    "2": "ee11a634-5d43-4f16-a584-82752ce24591",
                    "3": "fef47e26-b153-4ab8-a195-c7958e000491",
                },
            ),
            (
                ["/a", "/c"],
                {
                    "1": "49f48a53-e592-4bab-bf3a-7cfb08c584fb",
                    "2": "e6c0fcf4-a67b-4375-a477-e7d72fce3420",
                },
            ),
            (
                ["/c", "/a"],
                {
                    "1": "49f48a53-e592-4bab-bf3a-7cfb08c584fb",
                    "2": "ee11a634-5d43-4f16-a584-82752ce24591",
                },
            ),
        ],
    )
    def test_loading_multiple_paths(
        self, mock_client: Any, path: Any, expected: Any, app: Flask, ssm_client: Any
    ) -> None:
        mock_client.return_value = ssm_client
        env_man = SsmEnvironmentManager(app, path, "eu-west-2")
        assert env_man._get_parameters_from_paths() == expected

    @patch("boto3.client")
    def test_loading_from_local_file(
        self,
        mock_client: Any,
        app: Flask,
        ssm_client: Any,
    ) -> None:
        mock_client.return_value = ssm_client
        app.config["LOCAL_CONFIG_PYFILE"] = "local_config.py"
        env_man = SsmEnvironmentManager(app, ["/a"], "eu-west-2")
        parameters = env_man._get_parameters_to_parse()
        assert parameters.get("TEST1") == 1
        assert parameters.get("TEST2") == 2
