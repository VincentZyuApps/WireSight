#!/usr/bin/env python3
"""
Usage:
    uv venv
    uv run python ./scripts/validate_publish.py

CI:
    uv run python ./scripts/validate_publish.py --ci
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from _metadata import (
    MetadataError,
    ReleaseMetadata,
    append_github_outputs,
    load_metadata,
    minecraft_version_family,
)


MODRINTH_API_ROOT = "https://api.modrinth.com/v2"
CURSEFORGE_GAME_VERSIONS_URL = (
    "https://minecraft.curseforge.com/api/game/versions"
)
CURSEFORGE_GAME_VERSION_TYPES_URL = (
    "https://minecraft.curseforge.com/api/game/version-types"
)
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
USER_AGENT = "VincentZyuApps/WireSight publish-validator/1.0"


class ApiError(RuntimeError):
    pass


class HttpApiError(ApiError):
    def __init__(self, service: str, status: int, detail: str) -> None:
        self.service = service
        self.status = status
        suffix = f": {detail}" if detail else ""
        super().__init__(f"{service} API returned HTTP {status}{suffix}")


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: Any,
        code: int,
        message: str,
        headers: Any,
        new_url: str,
    ) -> None:
        raise ApiError(f"unexpected HTTP redirect ({code})")


def redact(value: object, secrets: tuple[str, ...]) -> str:
    text = str(value)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "<redacted>")
    return text


def read_json_response(response: Any) -> Any:
    body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ApiError("API response exceeded the size limit")
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ApiError("API returned invalid JSON") from error


def request_json(url: str, headers: dict[str, str], service: str) -> Any:
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(RejectRedirects())
    try:
        with opener.open(request, timeout=30) as response:
            return read_json_response(response)
    except urllib.error.HTTPError as error:
        body = error.read(64 * 1024).decode("utf-8", errors="replace").strip()
        raise HttpApiError(service, error.code, body) from error
    except urllib.error.URLError as error:
        raise ApiError(f"{service} API request failed: {error.reason}") from error


def query_modrinth_project(identifier: str, token: str) -> dict[str, Any]:
    payload = request_json(
        f"{MODRINTH_API_ROOT}/project/{urllib.parse.quote(identifier, safe='')}",
        {
            "Accept": "application/json",
            "Authorization": token,
            "User-Agent": USER_AGENT,
        },
        "Modrinth",
    )
    if not isinstance(payload, dict):
        raise ApiError("Modrinth API returned an unexpected response shape")
    return payload


def query_curseforge_collection(
    url: str, token: str, collection_name: str
) -> list[dict[str, Any]]:
    payload = request_json(
        url,
        {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            "X-Api-Token": token,
        },
        "CurseForge",
    )
    if isinstance(payload, dict):
        payload = payload.get("data")
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ApiError(
            f"CurseForge API returned an unexpected {collection_name} response shape"
        )
    return payload


def map_curseforge_version_ids(
    metadata: ReleaseMetadata,
    available: list[dict[str, Any]],
    version_types: list[dict[str, Any]],
) -> list[tuple[str, str, str, str]]:
    type_ids_by_name: dict[str, set[str]] = {}
    for item in version_types:
        type_id = str(item.get("id", "")).strip()
        type_name = str(item.get("name", "")).strip()
        if type_id.isdigit() and type_name:
            type_ids_by_name.setdefault(type_name, set()).add(type_id)

    expected_types = {
        version: metadata.curseforge_version_types[
            minecraft_version_family(version)
        ]
        for version in metadata.minecraft_versions
    }
    invalid_type_names = sorted(
        {
            type_name
            for type_name in expected_types.values()
            if len(type_ids_by_name.get(type_name, set())) != 1
        }
    )
    if invalid_type_names:
        raise ApiError(
            "CurseForge did not return one exact type for: "
            + ", ".join(invalid_type_names)
        )

    expected_type_ids = {
        version: next(iter(type_ids_by_name[expected_types[version]]))
        for version in metadata.minecraft_versions
    }
    matches: dict[str, set[str]] = {
        version: set() for version in metadata.minecraft_versions
    }
    for item in available:
        name = str(item.get("name", "")).strip()
        version_id = str(item.get("id", "")).strip()
        version_type_id = str(item.get("gameVersionTypeID", "")).strip()
        if (
            name in matches
            and version_id.isdigit()
            and version_type_id == expected_type_ids[name]
        ):
            matches[name].add(version_id)

    missing = [name for name, ids in matches.items() if not ids]
    ambiguous = {name: sorted(ids) for name, ids in matches.items() if len(ids) > 1}
    if missing:
        raise ApiError("CurseForge did not return IDs for: " + ", ".join(missing))
    if ambiguous:
        detail = "; ".join(
            f"{name}={','.join(ids)}" for name, ids in ambiguous.items()
        )
        raise ApiError(f"CurseForge returned ambiguous IDs: {detail}")

    return [
        (
            version,
            next(iter(matches[version])),
            expected_types[version],
            expected_type_ids[version],
        )
        for version in metadata.minecraft_versions
    ]


def prompt_token(prompt: str) -> str:
    while True:
        value = getpass.getpass(f"{prompt}: ").strip()
        if value:
            return value
        print("Token cannot be empty, please try again.", file=sys.stderr)


def environment_tokens(required: bool) -> tuple[str, str] | None:
    modrinth_token = os.environ.get("MODRINTH_TOKEN", "").strip()
    curseforge_token = os.environ.get("CURSEFORGE_TOKEN", "").strip()
    if not modrinth_token and not curseforge_token and not required:
        return None
    missing = []
    if not modrinth_token:
        missing.append("MODRINTH_TOKEN")
    if not curseforge_token:
        missing.append("CURSEFORGE_TOKEN")
    if missing:
        raise ApiError("missing CI Secrets: " + ", ".join(missing))
    return modrinth_token, curseforge_token


def validate_platforms(
    metadata: ReleaseMetadata, modrinth_token: str, curseforge_token: str
) -> tuple[list[str], list[str]]:
    secrets = (modrinth_token, curseforge_token)
    warnings: list[str] = []
    errors: list[str] = []

    print("\n🔍 Querying Modrinth...")
    try:
        project = query_modrinth_project(metadata.modrinth_project, modrinth_token)
        project_type = str(project.get("project_type", "")).strip()
        if project_type != "shader":
            raise ApiError(
                f"project type is {project_type!r}; expected 'shader'"
            )
        print(
            json.dumps(
                {
                    "id": project.get("id"),
                    "slug": project.get("slug"),
                    "title": project.get("title"),
                    "project_type": project_type,
                    "status": project.get("status"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    except HttpApiError as error:
        if error.status == 404:
            warnings.append(
                "Modrinth project metadata is hidden or the token lacks project "
                f"read permission; retaining slug {metadata.modrinth_project!r}."
            )
        else:
            errors.append(redact(f"Modrinth: {error}", secrets))
    except Exception as error:
        errors.append(redact(f"Modrinth: {error}", secrets))

    print("\n🔍 Querying CurseForge game versions...")
    try:
        mapping = map_curseforge_version_ids(
            metadata,
            query_curseforge_collection(
                CURSEFORGE_GAME_VERSIONS_URL,
                curseforge_token,
                "game versions",
            ),
            query_curseforge_collection(
                CURSEFORGE_GAME_VERSION_TYPES_URL,
                curseforge_token,
                "game version types",
            ),
        )
        width = max(len(version) for version, _, _, _ in mapping)
        for version, version_id, type_name, type_id in mapping:
            print(
                f"  {version:<{width}} -> {version_id} "
                f"({type_name}, type {type_id})"
            )
        print(
            f"  Project {metadata.curseforge_project}: version mappings validated; "
            "project upload access is verified only by a real release."
        )
    except Exception as error:
        errors.append(redact(f"CurseForge: {error}", secrets))

    return warnings, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate WireSight release metadata and read-only platform access."
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="read tokens from CI Secrets and write metadata to GITHUB_OUTPUT",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    try:
        metadata = load_metadata(repo_root / "metadata.toml")
        print(
            f"✅ Metadata: WireSight {metadata.version}, "
            f"{len(metadata.minecraft_versions)} Minecraft versions, "
            f"Modrinth {metadata.modrinth_project}, "
            f"CurseForge {metadata.curseforge_project}"
        )

        if args.ci:
            required = os.environ.get("REQUIRE_PLATFORM_VALIDATION", "").lower() in {
                "1",
                "true",
                "yes",
            }
            tokens = environment_tokens(required)
        else:
            try:
                tokens = (
                    prompt_token("Modrinth personal access token"),
                    prompt_token("CurseForge author API token"),
                )
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.", file=sys.stderr)
                return 130

        warnings: list[str] = []
        errors: list[str] = []
        if tokens is None:
            print("ℹ️ No CI Secrets were injected; platform API validation skipped.")
        else:
            warnings, errors = validate_platforms(metadata, *tokens)
            tokens = ("", "")

        if args.ci:
            github_output = os.environ.get("GITHUB_OUTPUT")
            if github_output:
                append_github_outputs(Path(github_output), metadata.github_outputs())
            else:
                print("\nGitHub Actions outputs:")
                for name, value in metadata.github_outputs().items():
                    print(f"{name}={value}")

        if warnings:
            print("\n⚠️ Warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"  - {warning}", file=sys.stderr)
        if errors:
            print("\n❌ Validation errors:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
    except (ApiError, MetadataError, OSError) as error:
        secrets = tuple(
            value
            for value in (
                os.environ.get("MODRINTH_TOKEN", ""),
                os.environ.get("CURSEFORGE_TOKEN", ""),
            )
            if value
        )
        print(f"❌ Error: {redact(error, secrets)}", file=sys.stderr)
        return 1

    print("\n✅ Publish configuration validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
