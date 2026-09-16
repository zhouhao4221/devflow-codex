#!/usr/bin/env python3
"""
Swagger/OpenAPI 解析器

解析 OpenAPI 2.0/3.0/3.1 文档，提取接口信息供 DevFlow API 插件使用。

用法：
    # 解析 URL，输出摘要
    python3 swagger-parser.py --url "http://localhost:8080/swagger/doc.json" --mode summary

    # 解析本地文件
    python3 swagger-parser.py --file "./swagger.json" --mode summary

    # 搜索接口
    python3 swagger-parser.py --url "..." --mode search --keyword "用户"

    # 获取单个接口详情
    python3 swagger-parser.py --url "..." --mode detail --path "GET /api/v1/users/{id}"
"""

import argparse
import json
import sys
import re
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def load_swagger(url=None, file_path=None):
    """加载 Swagger 文档"""
    content = None

    if url:
        try:
            req = Request(url, headers={"User-Agent": "swagger-parser/1.0"})
            with urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
        except HTTPError as e:
            print(json.dumps({"error": f"HTTP {e.code}: {e.reason}", "type": "http_error"}))
            sys.exit(1)
        except URLError as e:
            print(json.dumps({"error": f"无法访问: {e.reason}", "type": "connection_error"}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": str(e), "type": "unknown_error"}))
            sys.exit(1)
    elif file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(json.dumps({"error": f"文件不存在: {file_path}", "type": "file_not_found"}))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": str(e), "type": "file_error"}))
            sys.exit(1)
    else:
        print(json.dumps({"error": "需要 --url 或 --file 参数", "type": "args_error"}))
        sys.exit(1)

    # 尝试 JSON 解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # 尝试 YAML 解析
    try:
        import yaml
        return yaml.safe_load(content)
    except ImportError:
        # YAML 不可用，尝试简单处理
        print(json.dumps({"error": "YAML 格式需要安装 pyyaml: pip3 install pyyaml", "type": "yaml_missing"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"解析失败: {e}", "type": "parse_error"}))
        sys.exit(1)


def detect_version(spec):
    """检测 OpenAPI 版本"""
    if "openapi" in spec:
        return spec["openapi"]
    elif "swagger" in spec:
        return spec["swagger"]
    return "unknown"


def resolve_ref(spec, ref):
    """解析 $ref 引用"""
    if not ref or not ref.startswith("#/"):
        return {}
    parts = ref[2:].split("/")
    node = spec
    for part in parts:
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return {}
    return node


def resolve_schema(spec, schema, depth=0):
    """递归解析 schema，展开 $ref、allOf、oneOf、anyOf"""
    if depth > 10:
        return schema

    if not isinstance(schema, dict):
        return schema

    # 解析 $ref
    if "$ref" in schema:
        resolved = resolve_ref(spec, schema["$ref"])
        return resolve_schema(spec, resolved, depth + 1)

    # 解析 allOf
    if "allOf" in schema:
        merged = {}
        merged_props = {}
        merged_required = []
        for sub in schema["allOf"]:
            resolved_sub = resolve_schema(spec, sub, depth + 1)
            if "properties" in resolved_sub:
                merged_props.update(resolved_sub["properties"])
            if "required" in resolved_sub:
                merged_required.extend(resolved_sub["required"])
            merged.update(resolved_sub)
        merged["properties"] = merged_props
        if merged_required:
            merged["required"] = list(set(merged_required))
        merged.pop("allOf", None)
        return merged

    # 解析 oneOf / anyOf
    for key in ("oneOf", "anyOf"):
        if key in schema:
            resolved_items = [resolve_schema(spec, item, depth + 1) for item in schema[key]]
            return {key: resolved_items, "type": "union"}

    # 解析 properties 中的 $ref
    if "properties" in schema:
        resolved_props = {}
        for prop_name, prop_schema in schema["properties"].items():
            resolved_props[prop_name] = resolve_schema(spec, prop_schema, depth + 1)
        schema = dict(schema)
        schema["properties"] = resolved_props

    # 解析 items 中的 $ref
    if "items" in schema:
        schema = dict(schema)
        schema["items"] = resolve_schema(spec, schema["items"], depth + 1)

    return schema


def get_paths(spec):
    """获取所有路径定义"""
    return spec.get("paths", {})


def get_api_list(spec):
    """提取所有 API 接口列表"""
    apis = []
    paths = get_paths(spec)

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, detail in methods.items():
            if method.upper() not in ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"):
                continue
            if not isinstance(detail, dict):
                continue
            apis.append({
                "method": method.upper(),
                "path": path,
                "summary": detail.get("summary", ""),
                "description": detail.get("description", ""),
                "tags": detail.get("tags", []),
                "operationId": detail.get("operationId", ""),
            })

    return apis


def get_summary(spec):
    """生成摘要信息"""
    version = detect_version(spec)
    info = spec.get("info", {})
    apis = get_api_list(spec)

    # 按 Tag 分组统计
    tag_counts = {}
    for api in apis:
        tags = api["tags"] if api["tags"] else ["无分组"]
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Tag 描述
    tag_descriptions = {}
    for tag_def in spec.get("tags", []):
        if isinstance(tag_def, dict):
            tag_descriptions[tag_def.get("name", "")] = tag_def.get("description", "")

    tags = []
    for tag_name, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        tags.append({
            "name": tag_name,
            "count": count,
            "description": tag_descriptions.get(tag_name, ""),
        })

    return {
        "version": version,
        "title": info.get("title", ""),
        "description": info.get("description", ""),
        "apiVersion": info.get("version", ""),
        "totalApis": len(apis),
        "tags": tags,
    }


def search_apis(spec, keyword):
    """搜索匹配的 API"""
    apis = get_api_list(spec)
    keyword_lower = keyword.lower()
    results = []

    for api in apis:
        searchable = " ".join([
            api["path"],
            api["summary"],
            api["description"],
            api["operationId"],
            " ".join(api["tags"]),
        ]).lower()

        if keyword_lower in searchable:
            results.append(api)

    return results


def get_api_detail(spec, method, path):
    """获取单个接口的完整详情"""
    paths = get_paths(spec)
    version = detect_version(spec)

    # 查找匹配的路径
    path_detail = paths.get(path)
    if not path_detail:
        # 尝试模糊匹配
        for p in paths:
            if p.rstrip("/") == path.rstrip("/"):
                path_detail = paths[p]
                break

    if not path_detail or not isinstance(path_detail, dict):
        return {"error": f"路径未找到: {path}"}

    method_lower = method.lower()
    detail = path_detail.get(method_lower)
    if not detail:
        return {"error": f"方法未找到: {method} {path}"}

    result = {
        "method": method.upper(),
        "path": path,
        "summary": detail.get("summary", ""),
        "description": detail.get("description", ""),
        "tags": detail.get("tags", []),
        "operationId": detail.get("operationId", ""),
        "parameters": [],
        "requestBody": None,
        "responses": {},
    }

    # 解析参数（OpenAPI 3.x）
    params = detail.get("parameters", [])
    # 合并 path-level 参数
    path_params = path_detail.get("parameters", [])
    all_params = path_params + params

    for param in all_params:
        if not isinstance(param, dict):
            continue
        # 解析 $ref
        if "$ref" in param:
            param = resolve_ref(spec, param["$ref"])
        p = {
            "name": param.get("name", ""),
            "in": param.get("in", ""),
            "required": param.get("required", False),
            "description": param.get("description", ""),
            "schema": resolve_schema(spec, param.get("schema", {})),
        }
        # OpenAPI 2.x 兼容
        if "type" in param and "schema" not in param:
            p["schema"] = {"type": param["type"]}
            if "format" in param:
                p["schema"]["format"] = param["format"]
            if "enum" in param:
                p["schema"]["enum"] = param["enum"]
        result["parameters"].append(p)

    # 解析请求体
    if version.startswith("3"):
        # OpenAPI 3.x
        request_body = detail.get("requestBody", {})
        if "$ref" in request_body:
            request_body = resolve_ref(spec, request_body["$ref"])
        if request_body:
            content = request_body.get("content", {})
            for content_type, content_detail in content.items():
                schema = content_detail.get("schema", {})
                result["requestBody"] = {
                    "contentType": content_type,
                    "required": request_body.get("required", False),
                    "schema": resolve_schema(spec, schema),
                }
                break  # 取第一个 content type
    else:
        # OpenAPI 2.x — body 参数
        for param in all_params:
            if isinstance(param, dict) and param.get("in") == "body":
                schema = param.get("schema", {})
                result["requestBody"] = {
                    "contentType": "application/json",
                    "required": param.get("required", False),
                    "schema": resolve_schema(spec, schema),
                }
                # 从 parameters 中移除 body 参数
                result["parameters"] = [p for p in result["parameters"] if p["in"] != "body"]
                break

    # 解析响应
    responses = detail.get("responses", {})
    for status_code, resp_detail in responses.items():
        if not isinstance(resp_detail, dict):
            continue
        if "$ref" in resp_detail:
            resp_detail = resolve_ref(spec, resp_detail["$ref"])

        resp = {
            "description": resp_detail.get("description", ""),
            "schema": None,
        }

        if version.startswith("3"):
            content = resp_detail.get("content", {})
            for content_type, content_detail in content.items():
                schema = content_detail.get("schema", {})
                resp["schema"] = resolve_schema(spec, schema)
                resp["contentType"] = content_type
                break
        else:
            # OpenAPI 2.x
            schema = resp_detail.get("schema", {})
            if schema:
                resp["schema"] = resolve_schema(spec, schema)

        result["responses"][str(status_code)] = resp

    return result


def main():
    parser = argparse.ArgumentParser(description="Swagger/OpenAPI 解析器")
    parser.add_argument("--url", help="Swagger 文档 URL")
    parser.add_argument("--file", help="本地 Swagger 文件路径")
    parser.add_argument("--mode", choices=["summary", "search", "detail", "list"],
                        default="summary", help="运行模式")
    parser.add_argument("--keyword", help="搜索关键词（search 模式）")
    parser.add_argument("--path", help="接口路径，格式: 'GET /api/v1/users'（detail 模式）")
    parser.add_argument("--tag", help="按 Tag 过滤")

    args = parser.parse_args()

    # 加载文档
    spec = load_swagger(url=args.url, file_path=args.file)

    if args.mode == "summary":
        result = get_summary(spec)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.mode == "list":
        apis = get_api_list(spec)
        if args.tag:
            apis = [a for a in apis if args.tag in a.get("tags", [])]
        print(json.dumps(apis, ensure_ascii=False, indent=2))

    elif args.mode == "search":
        if not args.keyword:
            print(json.dumps({"error": "search 模式需要 --keyword 参数"}))
            sys.exit(1)
        results = search_apis(spec, args.keyword)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.mode == "detail":
        if not args.path:
            print(json.dumps({"error": "detail 模式需要 --path 参数，格式: 'GET /api/v1/users'"}))
            sys.exit(1)
        parts = args.path.split(" ", 1)
        if len(parts) != 2:
            print(json.dumps({"error": "路径格式错误，应为: 'GET /api/v1/users'"}))
            sys.exit(1)
        method, path = parts
        result = get_api_detail(spec, method, path)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
