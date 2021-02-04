import pytest

from typing import Generator
from flask import Flask, Config


@pytest.fixture(scope="function", autouse=True)
def app() -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.app_context().push()
    yield app
