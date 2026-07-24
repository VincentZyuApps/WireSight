#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$")
PACKAGE_INPUTS = ("shaders", "README.md", "LICENSE")
BOLD_RED = "\033[1;31m"
BOLD_GREEN = "\033[1;32m"
BOLD_CYAN = "\033[1;36m"
RESET = "\033[0m"


def usage(program_name: str) -> None:
    print(f"{BOLD_CYAN}🛠️ Usage:{RESET} {program_name} [version]")
    print("📦 Builds dist/WireSight-<version>.zip with shaders/ at the archive root.")


def print_error(message: str) -> None:
    print(f"{BOLD_RED}❌ Error:{RESET} {message}", file=sys.stderr)


def read_version(repo_root: Path, arguments: list[str]) -> str:
    if arguments:
        version = arguments[0]
    else:
        version = "".join((repo_root / "VERSION").read_text(encoding="utf-8").split())

    if version.startswith("v"):
        version = version[1:]

    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError(
            f"invalid version {version!r}; expected a SemVer-like value such as X.Y.Z"
        )

    return version


def find_seven_zip() -> str:
    for executable in ("7z", "7zz"):
        path = shutil.which(executable)
        if path is not None:
            return path
    raise FileNotFoundError(
        "7z or 7zz was not found in PATH; install 7-Zip and add its CLI to PATH"
    )


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_github_outputs(
    output_path: str,
    version: str,
    artifact_name: str,
    artifact_path: Path,
    checksum_path: Path,
) -> None:
    with open(output_path, "a", encoding="utf-8", newline="\n") as output:
        output.write(f"version={version}\n")
        output.write(f"artifact_name={artifact_name}\n")
        output.write(f"artifact_path={artifact_path}\n")
        output.write(f"checksum_path={checksum_path}\n")


def build(repo_root: Path, version: str, seven_zip: str) -> tuple[Path, Path, str]:
    for relative_path in PACKAGE_INPUTS:
        if not (repo_root / relative_path).exists():
            raise FileNotFoundError(f"required package input is missing: {relative_path}")

    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    artifact_name = f"WireSight-{version}.zip"
    artifact_path = dist_dir / artifact_name
    checksum_path = artifact_path.with_name(f"{artifact_name}.sha256")

    temporary_archive = dist_dir / f".WireSight-{version}.{uuid.uuid4().hex}.zip"
    try:
        try:
            subprocess.run(
                [
                    seven_zip,
                    "a",
                    "-tzip",
                    "-mx=9",
                    "--",
                    str(temporary_archive),
                    *PACKAGE_INPUTS,
                ],
                cwd=repo_root,
                stdout=subprocess.DEVNULL,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError("7-Zip failed to create archive") from error

        try:
            subprocess.run(
                [seven_zip, "t", "--", str(temporary_archive)],
                stdout=subprocess.DEVNULL,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError("7-Zip failed to validate archive") from error

        os.replace(temporary_archive, artifact_path)
    finally:
        temporary_archive.unlink(missing_ok=True)

    checksum = calculate_sha256(artifact_path)
    with checksum_path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(f"{checksum}  {artifact_name}\n")

    return artifact_path, checksum_path, checksum


def main() -> int:
    arguments = sys.argv[1:]
    program_name = Path(sys.argv[0]).name

    if arguments and arguments[0] in ("-h", "--help"):
        usage(program_name)
        return 0

    repo_root = Path(__file__).resolve().parent.parent

    try:
        version = read_version(repo_root, arguments)
        seven_zip = find_seven_zip()
        print(f"{BOLD_CYAN}📦 Building:{RESET} WireSight {version}")
        artifact_path, checksum_path, checksum = build(repo_root, version, seven_zip)
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        print_error(str(error))
        return 1

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        append_github_outputs(
            github_output,
            version,
            artifact_path.name,
            artifact_path,
            checksum_path,
        )

    print(f"{BOLD_GREEN}✅ Built:{RESET} {artifact_path}")
    print(f"{BOLD_CYAN}🔐 SHA-256:{RESET} {checksum}  {artifact_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
