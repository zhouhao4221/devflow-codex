#!/usr/bin/env python3
"""Swagger 解析器的参数覆盖与组合 schema 回归测试。"""
import importlib.util
from pathlib import Path
import unittest


PARSER_PATH = Path(__file__).resolve().parents[1] / "plugins/api/scripts/swagger-parser.py"
spec = importlib.util.spec_from_file_location("swagger_parser", PARSER_PATH)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


class SwaggerParserTests(unittest.TestCase):
    def test_allof_keeps_sibling_properties_and_required(self):
        document = {"components": {"schemas": {"Base": {
            "type": "object", "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        }}}}
        schema = {
            "allOf": [{"$ref": "#/components/schemas/Base"}],
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }

        result = parser.resolve_schema(document, schema)

        self.assertEqual(set(result["properties"]), {"id", "name"})
        self.assertEqual(result["required"], ["id", "name"])

    def test_operation_parameter_overrides_referenced_path_parameter(self):
        document = {
            "openapi": "3.0.3",
            "components": {"parameters": {"PathId": {
                "name": "id", "in": "path", "required": True,
                "schema": {"type": "integer"},
            }}},
            "paths": {"/items/{id}": {
                "parameters": [{"$ref": "#/components/parameters/PathId"}],
                "get": {"parameters": [{
                    "name": "id", "in": "path", "required": True,
                    "schema": {"type": "string"},
                }]},
            }},
        }

        result = parser.get_api_detail(document, "GET", "/items/{id}")

        self.assertEqual(len(result["parameters"]), 1)
        self.assertEqual(result["parameters"][0]["schema"], {"type": "string"})

    def test_swagger2_referenced_body_parameter_becomes_request_body(self):
        document = {
            "swagger": "2.0",
            "parameters": {"Payload": {
                "name": "payload", "in": "body", "required": True,
                "schema": {"type": "object", "properties": {"id": {"type": "integer"}}},
            }},
            "paths": {"/items": {"post": {
                "parameters": [{"$ref": "#/parameters/Payload"}],
            }}},
        }

        result = parser.get_api_detail(document, "POST", "/items")

        self.assertEqual(result["parameters"], [])
        self.assertTrue(result["requestBody"]["required"])
        self.assertIn("id", result["requestBody"]["schema"]["properties"])


if __name__ == "__main__":
    unittest.main()
