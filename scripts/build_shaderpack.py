#!/usr/bin/env python3
"""
Usage:
    uv venv
    uv run python ./scripts/build_shaderpack.py

The command always builds the Iris/Oculus source package and an ASCII-safe
OptiFine package. It accepts no version override; metadata.toml is authoritative.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

from _metadata import (
    BuildVariant,
    MetadataError,
    append_github_outputs,
    load_metadata,
)


PACKAGE_INPUTS = ("LICENSE", "README.md", "shaders")
GLSL_EXTENSIONS = {".vsh", ".fsh", ".glsl"}
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644
DIRECTORY_MODE = 0o40755
BOLD_RED = "\033[1;31m"
BOLD_GREEN = "\033[1;32m"
BOLD_CYAN = "\033[1;36m"
RESET = "\033[0m"


class BuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class BuildResult:
    variant: BuildVariant
    artifact_path: Path
    checksum_path: Path
    checksum: str


def normalized_content(path: Path) -> bytes:
    data = path.read_bytes()
    if b"\0" in data:
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _replace_comment_character(character: str) -> str:
    return character if ord(character) < 128 else " "


def ascii_safe_glsl(text: str, archive_name: str) -> str:
    result: list[str] = []
    state = "code"
    quote = ""
    escaped = False
    line = 1
    column = 1
    index = 0

    while index < len(text):
        character = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""

        if state == "code":
            if character == "/" and following == "/":
                result.extend(("/", "/"))
                state = "line-comment"
                index += 2
                column += 2
                continue
            if character == "/" and following == "*":
                result.extend(("/", "*"))
                state = "block-comment"
                index += 2
                column += 2
                continue
            if character in {'"', "'"}:
                state = "string"
                quote = character
                escaped = False
            if ord(character) >= 128:
                raise BuildError(
                    f"OptiFine source contains non-ASCII code at "
                    f"{archive_name}:{line}:{column}"
                )
            result.append(character)
        elif state == "string":
            if ord(character) >= 128:
                raise BuildError(
                    f"OptiFine source contains non-ASCII string data at "
                    f"{archive_name}:{line}:{column}"
                )
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                state = "code"
        elif state == "line-comment":
            result.append(_replace_comment_character(character))
            if character == "\n":
                state = "code"
        else:
            if character == "*" and following == "/":
                result.extend(("*", "/"))
                state = "code"
                index += 2
                column += 2
                continue
            result.append(_replace_comment_character(character))

        if character == "\n":
            line += 1
            column = 1
        else:
            column += 1
        index += 1

    if state == "block-comment":
        raise BuildError(f"unterminated block comment in {archive_name}")
    if state == "string":
        raise BuildError(f"unterminated string in {archive_name}")
    return "".join(result)


def ascii_safe_properties(text: str, archive_name: str) -> str:
    result: list[str] = []
    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        if line.lstrip().startswith("#"):
            result.append("".join(_replace_comment_character(char) for char in line))
            continue
        for column, character in enumerate(line, start=1):
            if ord(character) >= 128:
                raise BuildError(
                    f"OptiFine properties contain non-ASCII data at "
                    f"{archive_name}:{line_number}:{column}"
                )
        result.append(line)
    return "".join(result)


def content_for_variant(
    source: Path, archive_name: str, variant: BuildVariant
) -> bytes:
    content = normalized_content(source)
    if variant.name != "optifine":
        return content
    if Path(archive_name).suffix.lower() not in GLSL_EXTENSIONS and (
        archive_name != "shaders/shaders.properties"
    ):
        return content
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise BuildError(f"OptiFine source must be UTF-8: {archive_name}") from error
    if archive_name == "shaders/shaders.properties":
        return ascii_safe_properties(text, archive_name).encode("ascii")
    return ascii_safe_glsl(text, archive_name).encode("ascii")


def archive_entries(repo_root: Path) -> list[tuple[str, Path | None]]:
    entries: list[tuple[str, Path | None]] = []
    for relative in PACKAGE_INPUTS:
        path = repo_root / relative
        if not path.exists():
            raise BuildError(f"required package input is missing: {relative}")
        if path.is_symlink():
            raise BuildError(f"package input must not be a symbolic link: {relative}")
        if path.is_file():
            entries.append((relative, path))
            continue
        entries.append((f"{relative}/", None))
        for child in path.rglob("*"):
            if child.is_symlink():
                raise BuildError(
                    "package input must not contain symbolic links: "
                    + child.relative_to(repo_root).as_posix()
                )
            archive_name = child.relative_to(repo_root).as_posix()
            entries.append(
                (f"{archive_name}/", None)
                if child.is_dir()
                else (archive_name, child)
            )
    return sorted(entries, key=lambda item: item[0])


def zip_info(name: str, is_directory: bool) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIMESTAMP)
    info.create_system = 3
    info.flag_bits |= 0x800
    if is_directory:
        info.compress_type = zipfile.ZIP_STORED
        info.external_attr = (DIRECTORY_MODE << 16) | 0x10
    else:
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = FILE_MODE << 16
    return info


def create_archive(
    repo_root: Path, destination: Path, variant: BuildVariant
) -> None:
    with zipfile.ZipFile(
        destination,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as archive:
        for name, source in archive_entries(repo_root):
            is_directory = source is None
            archive.writestr(
                zip_info(name, is_directory),
                b""
                if is_directory
                else content_for_variant(source, name, variant),
                compress_type=(
                    zipfile.ZIP_STORED if is_directory else zipfile.ZIP_DEFLATED
                ),
                compresslevel=None if is_directory else 9,
            )

    with zipfile.ZipFile(destination, mode="r") as archive:
        broken_entry = archive.testzip()
    if broken_entry is not None:
        raise BuildError(f"ZIP integrity check failed at: {broken_entry}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_variant(
    repo_root: Path, version: str, variant: BuildVariant
) -> BuildResult:
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    artifact_name = variant.artifact_name(version)
    artifact_path = dist_dir / artifact_name
    checksum_path = dist_dir / f"{artifact_name}.sha256"
    temporary_archive = dist_dir / f".{artifact_name}.{uuid.uuid4().hex}.tmp"
    temporary_checksum = dist_dir / f".{artifact_name}.sha256.{uuid.uuid4().hex}.tmp"

    try:
        create_archive(repo_root, temporary_archive, variant)
        checksum = sha256(temporary_archive)
        temporary_checksum.write_text(
            f"{checksum}  {artifact_name}\n", encoding="utf-8", newline="\n"
        )
        os.replace(temporary_archive, artifact_path)
        os.replace(temporary_checksum, checksum_path)
    finally:
        temporary_archive.unlink(missing_ok=True)
        temporary_checksum.unlink(missing_ok=True)

    return BuildResult(variant, artifact_path, checksum_path, checksum)


def build(repo_root: Path) -> tuple[BuildResult, ...]:
    metadata = load_metadata(repo_root / "metadata.toml")
    results = tuple(
        build_variant(repo_root, metadata.version, variant)
        for variant in metadata.variants
    )

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        outputs = {"version": metadata.version}
        for result in results:
            prefix = result.variant.output_prefix
            outputs.update(
                {
                    f"{prefix}_artifact_name": result.artifact_path.name,
                    f"{prefix}_artifact_path": str(result.artifact_path),
                    f"{prefix}_checksum_path": str(result.checksum_path),
                }
            )
        append_github_outputs(Path(github_output), outputs)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build reproducible Iris/Oculus and ASCII-safe OptiFine WireSight "
            "shaderpack ZIPs with SHA-256 files."
        )
    )
    parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    try:
        print(f"{BOLD_CYAN}📦 Building:{RESET} WireSight variants")
        results = build(repo_root)
    except (BuildError, MetadataError, OSError, zipfile.BadZipFile) as error:
        print(f"{BOLD_RED}❌ Error:{RESET} {error}", file=sys.stderr)
        return 1

    for result in results:
        print(f"{BOLD_GREEN}✅ Built:{RESET} {result.artifact_path}")
        print(
            f"{BOLD_CYAN}🔐 SHA-256:{RESET} {result.checksum}  "
            f"{result.artifact_path.name}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
