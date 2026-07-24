#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"

BOLD_RED=$'\033[1;31m'
BOLD_GREEN=$'\033[1;32m'
BOLD_CYAN=$'\033[1;36m'
RESET=$'\033[0m'

usage() {
    printf '%s🛠️ Usage:%s %s [version]\n' "${BOLD_CYAN}" "${RESET}" "${0##*/}"
    printf '📦 Builds dist/WireSight-<version>.zip with shaders/ at the archive root.\n'
}

error() {
    printf '%s❌ Error:%s %s\n' "${BOLD_RED}" "${RESET}" "$*" >&2
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
    error "invalid version '${VERSION}'; expected a SemVer-like value such as X.Y.Z"
    exit 1
fi

for required_path in shaders README.md LICENSE; do
    if [[ ! -e "${REPO_ROOT}/${required_path}" ]]; then
        error "required package input is missing: ${required_path}"
        exit 1
    fi
done

if command -v 7z >/dev/null 2>&1; then
    SEVEN_ZIP="7z"
elif command -v 7zz >/dev/null 2>&1; then
    SEVEN_ZIP="7zz"
else
    error "7z or 7zz was not found in PATH; install 7-Zip and add its CLI to PATH"
    exit 1
fi

mkdir -p "${DIST_DIR}"

ARTIFACT_NAME="WireSight-${VERSION}.zip"
ARTIFACT_PATH="${DIST_DIR}/${ARTIFACT_NAME}"
CHECKSUM_PATH="${ARTIFACT_PATH}.sha256"
TEMP_ARCHIVE="${DIST_DIR}/.WireSight-${VERSION}.${BASHPID}.${RANDOM}.zip"
while [[ -e "${TEMP_ARCHIVE}" ]]; do
    TEMP_ARCHIVE="${DIST_DIR}/.WireSight-${VERSION}.${BASHPID}.${RANDOM}.zip"
done
trap 'rm -f -- "${TEMP_ARCHIVE}"' EXIT

printf '%s📦 Building:%s WireSight %s\n' "${BOLD_CYAN}" "${RESET}" "${VERSION}"

if ! (
    cd -- "${REPO_ROOT}"
    "${SEVEN_ZIP}" a -tzip -mx=9 -- "${TEMP_ARCHIVE}" shaders README.md LICENSE >/dev/null
); then
    error "7-Zip failed to create archive"
    exit 1
fi

if ! "${SEVEN_ZIP}" t -- "${TEMP_ARCHIVE}" >/dev/null; then
    error "7-Zip failed to validate archive"
    exit 1
fi
mv -f -- "${TEMP_ARCHIVE}" "${ARTIFACT_PATH}"
trap - EXIT

if command -v sha256sum >/dev/null 2>&1; then
    CHECKSUM_LINE="$(cd -- "${DIST_DIR}" && sha256sum "${ARTIFACT_NAME}")"
else
    CHECKSUM_LINE="$(cd -- "${DIST_DIR}" && shasum -a 256 "${ARTIFACT_NAME}")"
fi
CHECKSUM="${CHECKSUM_LINE%%[[:space:]]*}"
printf '%s  %s\n' "${CHECKSUM}" "${ARTIFACT_NAME}" > "${CHECKSUM_PATH}"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    {
        printf 'version=%s\n' "${VERSION}"
        printf 'artifact_name=%s\n' "${ARTIFACT_NAME}"
        printf 'artifact_path=%s\n' "${ARTIFACT_PATH}"
        printf 'checksum_path=%s\n' "${CHECKSUM_PATH}"
    } >> "${GITHUB_OUTPUT}"
fi

printf '%s✅ Built:%s %s\n' "${BOLD_GREEN}" "${RESET}" "${ARTIFACT_PATH}"
printf '%s🔐 SHA-256:%s ' "${BOLD_CYAN}" "${RESET}"
sed -n '1p' "${CHECKSUM_PATH}"
