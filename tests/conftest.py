import pytest
import os
import boto3

from typing import Any, Generator
from flask import Flask, Config
from moto import mock_ssm


@pytest.fixture(scope="function", autouse=True)
def app() -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.app_context().push()
    yield app


@pytest.fixture(scope="module")
def aws_credentials() -> None:
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="module")
def ssm_client(aws_credentials: Any) -> Any:
    with mock_ssm():
        client = boto3.client("ssm", region_name="eu-west-2")
        values = [
            dict(
                Name="/test",
                Type="string",
                Value="9ce10572-a1a4-422c-9cf1-d4b45ecd93c2",
            ),
            dict(
                Name="/parent/child",
                Type="string",
                Value="27698a22-c47c-4457-a6b6-907051b4534a",
            ),
            dict(
                Name="/a/1",
                Type="string",
                Value="49f48a53-e592-4bab-bf3a-7cfb08c584fb",
            ),
            dict(
                Name="/a/2",
                Type="string",
                Value="ee11a634-5d43-4f16-a584-82752ce24591",
            ),
            dict(
                Name="/b/3",
                Type="string",
                Value="fef47e26-b153-4ab8-a195-c7958e000491",
            ),
            dict(
                Name="/c/2",
                Type="string",
                Value="e6c0fcf4-a67b-4375-a477-e7d72fce3420",
            ),
        ]
        for value in values:
            client.put_parameter(**value)
        yield client
