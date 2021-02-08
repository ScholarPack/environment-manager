import pytest

from flask import Flask
from typing import Any
from flask_environment_manager import WhitelistParser


class TestWhitelistParser:
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
        values: dict,
        expected: dict,
        app: Flask,
    ) -> None:
        app.config["ENV_OVERRIDE_WHITELIST"] = whitelist
        parser = WhitelistParser(app, values)
        parser.parse()
        for key in values.keys():
            assert app.config.get(key) == expected.get(key)

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
        parser = WhitelistParser(app, {})
        assert parser._coerce_value(value_in) == value_out
