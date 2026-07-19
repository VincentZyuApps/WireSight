#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"

usage() {
    printf 'Usage: %s [version]\n' "${0##*/}"
    printf 'Builds dist/WireSight-<version>.zip with shaders/ at the archive root.\n'
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

VERSION="${1:-$(tr -d '[:space:]' < "${REPO_ROOT}/VERSION")}"
VERSION="${VERSION#v}"

if [[ ! "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
    printf 'error: invalid version %q; expected a SemVer-like value such as X.Y.Z\n' "${VERSION}" >&2
    exit 1
fi

for required_path in shaders README.md LICENSE; do
    if [[ ! -e "${REPO_ROOT}/${required_path}" ]]; then
        printf 'error: required package input is missing: %s\n' "${required_path}" >&2
        exit 1
    fi
done

if command -v 7z >/dev/null 2>&1; then
    SEVEN_ZIP="7z"
elif command -v 7zz >/dev/null 2>&1; then
    SEVEN_ZIP="7zz"
else
    printf 'error: 7z or 7zz is required to build WireSight\n' >&2
    exit 1
fi

mkdir -p "${DIST_DIR}"

ARTIFACT_NAME="WireSight-${VERSION}.zip"
ARTIFACT_PATH="${DIST_DIR}/${ARTIFACT_NAME}"
CHECKSUM_PATH="${ARTIFACT_PATH}.sha256"
TEMP_DIR="$(mktemp -d "${DIST_DIR}/.WireSight-${VERSION}.XXXXXX")"
TEMP_ARCHIVE="${TEMP_DIR}/${ARTIFACT_NAME}"
trap 'rm -f -- "${TEMP_ARCHIVE}"; rmdir -- "${TEMP_DIR}" 2>/dev/null || true' EXIT

(
    cd -- "${REPO_ROOT}"
    "${SEVEN_ZIP}" a -tzip -mx=9 -- "${TEMP_ARCHIVE}" shaders README.md LICENSE >/dev/null
)

"${SEVEN_ZIP}" t -- "${TEMP_ARCHIVE}" >/dev/null
mv -f -- "${TEMP_ARCHIVE}" "${ARTIFACT_PATH}"
rmdir -- "${TEMP_DIR}"
trap - EXIT

if command -v sha256sum >/dev/null 2>&1; then
    (
        cd -- "${DIST_DIR}"
        sha256sum "${ARTIFACT_NAME}" > "${ARTIFACT_NAME}.sha256"
    )
else
    (
        cd -- "${DIST_DIR}"
        shasum -a 256 "${ARTIFACT_NAME}" > "${ARTIFACT_NAME}.sha256"
    )
fi

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    {
        printf 'version=%s\n' "${VERSION}"
        printf 'artifact_name=%s\n' "${ARTIFACT_NAME}"
        printf 'artifact_path=%s\n' "${ARTIFACT_PATH}"
        printf 'checksum_path=%s\n' "${CHECKSUM_PATH}"
    } >> "${GITHUB_OUTPUT}"
fi

printf 'Built %s\n' "${ARTIFACT_PATH}"
printf 'Checksum: '
sed -n '1p' "${CHECKSUM_PATH}"
