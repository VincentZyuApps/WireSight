#!/usr/bin/env python3
"""
Usage:
    uv venv
    uv run python ./scripts/build_shaderpack.py
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import uuid
import zipfile
from pathlib import Path

from _metadata import MetadataError, append_github_outputs, load_metadata


PACKAGE_INPUTS = ("LICENSE", "README.md", "shaders")
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644
DIRECTORY_MODE = 0o40755
BOLD_RED = "\033[1;31m"
BOLD_GREEN = "\033[1;32m"
BOLD_CYAN = "\033[1;36m"
RESET = "\033[0m"


class BuildError(RuntimeError):
    pass


def normalized_content(path: Path) -> bytes:
    data = path.read_bytes()
    if b"\0" in data:
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


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


def create_archive(repo_root: Path, destination: Path) -> None:
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
                b"" if is_directory else normalized_content(source),
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


def build(repo_root: Path) -> tuple[Path, Path, str]:
    metadata = load_metadata(repo_root / "metadata.toml")
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    artifact_name = f"WireSight-{metadata.version}.zip"
    artifact_path = dist_dir / artifact_name
    checksum_path = dist_dir / f"{artifact_name}.sha256"
    temporary_archive = dist_dir / f".{artifact_name}.{uuid.uuid4().hex}.tmp"
    temporary_checksum = dist_dir / f".{artifact_name}.sha256.{uuid.uuid4().hex}.tmp"

    try:
        create_archive(repo_root, temporary_archive)
        checksum = sha256(temporary_archive)
        temporary_checksum.write_text(
            f"{checksum}  {artifact_name}\n", encoding="utf-8", newline="\n"
        )
        os.replace(temporary_archive, artifact_path)
        os.replace(temporary_checksum, checksum_path)
    finally:
        temporary_archive.unlink(missing_ok=True)
        temporary_checksum.unlink(missing_ok=True)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        append_github_outputs(
            Path(github_output),
            {
                "version": metadata.version,
                "artifact_name": artifact_name,
                "artifact_path": str(artifact_path),
                "checksum_path": str(checksum_path),
            },
        )
    return artifact_path, checksum_path, checksum


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a reproducible WireSight shaderpack ZIP and SHA-256 file."
    )
    parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    try:
        print(f"{BOLD_CYAN}📦 Building:{RESET} WireSight")
        artifact_path, _, checksum = build(repo_root)
    except (BuildError, MetadataError, OSError, zipfile.BadZipFile) as error:
        print(f"{BOLD_RED}❌ Error:{RESET} {error}", file=sys.stderr)
        return 1

    print(f"{BOLD_GREEN}✅ Built:{RESET} {artifact_path}")
    print(f"{BOLD_CYAN}🔐 SHA-256:{RESET} {checksum}  {artifact_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
