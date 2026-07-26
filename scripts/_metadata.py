#!/usr/bin/env python3

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VERSION_LINE_PATTERN = re.compile(
    r'^  version = "([0-9]+\.[0-9]+\.[0-9]+(?:[.-][0-9A-Za-z.-]+)?)"$'
)
SEMVER_PATTERN = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:[.-][0-9A-Za-z.-]+)?$"
)
MINECRAFT_VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
MODRINTH_PROJECT_ID_PATTERN = re.compile(r"^[0-9A-Za-z]{8}$")
SAFE_NAME_PATTERN = re.compile(r"^[0-9a-z_-]+$")
REQUIRED_VARIANTS = ("iris-oculus", "optifine")


class MetadataError(ValueError):
    pass


@dataclass(frozen=True)
class BuildVariant:
    name: str
    suffix: str
    loader: str
    minecraft_versions: tuple[str, ...]

    def artifact_name(self, version: str) -> str:
        return f"WireSight-{version}-{self.suffix}.zip"

    @property
    def output_prefix(self) -> str:
        return self.name.replace("-", "_")

    @property
    def modrinth_game_versions(self) -> str:
        return ",".join(self.minecraft_versions)


@dataclass(frozen=True)
class ReleaseMetadata:
    version: str
    variants: tuple[BuildVariant, ...]
    modrinth_project: str
    curseforge_project: int
    curseforge_version_types: dict[str, str]

    @property
    def tag(self) -> str:
        return f"v{self.version}"

    @property
    def minecraft_versions(self) -> tuple[str, ...]:
        versions = {
            version
            for variant in self.variants
            for version in variant.minecraft_versions
        }
        return tuple(sorted(versions, key=_numeric_version_key))

    def variant(self, name: str) -> BuildVariant:
        for variant in self.variants:
            if variant.name == name:
                return variant
        raise MetadataError(f"unknown build variant: {name}")

    def curseforge_game_versions(self, variant: BuildVariant) -> str:
        values = []
        for version in variant.minecraft_versions:
            family = minecraft_version_family(version)
            values.append(f"{self.curseforge_version_types[family]}:{version}")
        return ",".join(values)

    def github_outputs(self) -> dict[str, str]:
        outputs = {
            "version": self.version,
            "tag": self.tag,
            "modrinth_project": self.modrinth_project,
            "curseforge_project": str(self.curseforge_project),
        }
        for variant in self.variants:
            prefix = variant.output_prefix
            outputs.update(
                {
                    f"{prefix}_artifact_name": variant.artifact_name(self.version),
                    f"{prefix}_modrinth_loader": variant.loader,
                    f"{prefix}_modrinth_game_versions": (
                        variant.modrinth_game_versions
                    ),
                    f"{prefix}_curseforge_game_versions": (
                        self.curseforge_game_versions(variant)
                    ),
                }
            )
        return outputs


def minecraft_version_family(version: str) -> str:
    return ".".join(version.split(".")[:2])


def _expect_table(parent: dict[str, Any], key: str, context: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise MetadataError(f"{context}.{key} must be a TOML table")
    return value


def _reject_unknown_keys(
    table: dict[str, Any], allowed: set[str], context: str
) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise MetadataError(f"unknown {context} keys: {', '.join(unknown)}")


def _string_list(value: Any, context: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise MetadataError(f"{context} must be a non-empty TOML array")
    if not all(isinstance(item, str) and item for item in value):
        raise MetadataError(f"{context} must contain only non-empty strings")
    result = tuple(value)
    if len(result) != len(set(result)):
        raise MetadataError(f"{context} must not contain duplicates")
    return result


def _numeric_version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _load_variant(name: str, table: dict[str, Any]) -> BuildVariant:
    context = f"variants.{name}"
    _reject_unknown_keys(
        table, {"suffix", "loader", "minecraft-versions"}, context
    )
    suffix = table.get("suffix")
    loader = table.get("loader")
    if not isinstance(suffix, str) or SAFE_NAME_PATTERN.fullmatch(suffix) is None:
        raise MetadataError(f"{context}.suffix must be a safe lowercase name")
    if not isinstance(loader, str) or SAFE_NAME_PATTERN.fullmatch(loader) is None:
        raise MetadataError(f"{context}.loader must be a safe lowercase name")
    versions = _string_list(
        table.get("minecraft-versions"), f"{context}.minecraft-versions"
    )
    invalid_versions = [
        value
        for value in versions
        if MINECRAFT_VERSION_PATTERN.fullmatch(value) is None
    ]
    if invalid_versions:
        raise MetadataError(
            f"invalid stable Minecraft versions in {context}: "
            + ", ".join(invalid_versions)
        )
    if list(versions) != sorted(versions, key=_numeric_version_key):
        raise MetadataError(
            f"{context}.minecraft-versions must be in ascending numeric order"
        )
    return BuildVariant(name, suffix, loader, versions)


def load_metadata(path: Path) -> ReleaseMetadata:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise MetadataError(f"metadata file does not exist: {path}") from error
    except UnicodeDecodeError as error:
        raise MetadataError("metadata.toml must be UTF-8 without a BOM") from error

    lines = text.splitlines()
    if not lines or lines[0] != "[project]":
        raise MetadataError("metadata.toml line 1 must be exactly: [project]")
    if len(lines) < 2:
        raise MetadataError("metadata.toml is missing its version line")
    version_match = VERSION_LINE_PATTERN.fullmatch(lines[1])
    if version_match is None:
        raise MetadataError(
            'metadata.toml line 2 must match exactly:   version = "X.Y.Z"'
        )

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise MetadataError(f"invalid metadata.toml: {error}") from error
    if not isinstance(data, dict):
        raise MetadataError("metadata.toml must contain TOML tables")
    _reject_unknown_keys(
        data, {"project", "variants", "modrinth", "curseforge"}, "top-level"
    )

    project = _expect_table(data, "project", "metadata")
    raw_variants = _expect_table(data, "variants", "metadata")
    modrinth = _expect_table(data, "modrinth", "metadata")
    curseforge = _expect_table(data, "curseforge", "metadata")
    _reject_unknown_keys(project, {"version"}, "project")
    _reject_unknown_keys(modrinth, {"project"}, "modrinth")
    _reject_unknown_keys(curseforge, {"project", "version-types"}, "curseforge")

    version = project.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        raise MetadataError("project.version must be a SemVer-like string")
    if version != version_match.group(1):
        raise MetadataError("the parsed version does not match metadata.toml line 2")

    if tuple(raw_variants) != REQUIRED_VARIANTS:
        raise MetadataError(
            "variants must appear exactly in this order: "
            + ", ".join(REQUIRED_VARIANTS)
        )
    variants = tuple(
        _load_variant(name, _expect_table(raw_variants, name, "variants"))
        for name in REQUIRED_VARIANTS
    )
    suffixes = [variant.suffix for variant in variants]
    if len(suffixes) != len(set(suffixes)):
        raise MetadataError("variant suffixes must be unique")

    modrinth_project = modrinth.get("project")
    if (
        not isinstance(modrinth_project, str)
        or MODRINTH_PROJECT_ID_PATTERN.fullmatch(modrinth_project) is None
    ):
        raise MetadataError("modrinth.project must be an 8-character project ID")

    curseforge_project = curseforge.get("project")
    if (
        isinstance(curseforge_project, bool)
        or not isinstance(curseforge_project, int)
        or curseforge_project <= 0
    ):
        raise MetadataError("curseforge.project must be a positive integer")

    raw_version_types = curseforge.get("version-types")
    if not isinstance(raw_version_types, dict) or not raw_version_types:
        raise MetadataError("curseforge.version-types must be a non-empty TOML table")
    version_types: dict[str, str] = {}
    for family, type_name in raw_version_types.items():
        if (
            not isinstance(family, str)
            or re.fullmatch(r"^[0-9]+\.[0-9]+$", family) is None
            or not isinstance(type_name, str)
            or not type_name.strip()
            or "," in type_name
            or ":" in type_name
        ):
            raise MetadataError("invalid curseforge.version-types entry")
        version_types[family] = type_name

    all_versions = {
        version for variant in variants for version in variant.minecraft_versions
    }
    required_families = {
        minecraft_version_family(version) for version in all_versions
    }
    missing_families = sorted(required_families - set(version_types))
    extra_families = sorted(set(version_types) - required_families)
    if missing_families:
        raise MetadataError(
            "missing CurseForge version types for: " + ", ".join(missing_families)
        )
    if extra_families:
        raise MetadataError(
            "unused CurseForge version types for: " + ", ".join(extra_families)
        )

    return ReleaseMetadata(
        version=version,
        variants=variants,
        modrinth_project=modrinth_project,
        curseforge_project=curseforge_project,
        curseforge_version_types=version_types,
    )


def append_github_outputs(path: Path, values: dict[str, str]) -> None:
    for name, value in values.items():
        if "\n" in name or "\n" in value or "\r" in name or "\r" in value:
            raise MetadataError("GitHub output names and values must be single-line")
    with path.open("a", encoding="utf-8", newline="\n") as output:
        for name, value in values.items():
            output.write(f"{name}={value}\n")
