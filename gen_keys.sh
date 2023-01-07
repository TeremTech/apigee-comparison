#!/bin/bash
set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h]

Generates TLS keys and certificates required for the coordinator to authenticate with the client.

Available options:
-h, --help      Print this help and exit
EOF
  exit
}

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
}

msg() {
  echo >&2 -e "${1-}"
}

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

parse_params() {
  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -?*) die "Unknown option: $1" ;;
    *) break ;;
    esac
    shift
  done
  return 0
}

parse_params "$@"

subj="/C=AU/ST=NSW/O=API Test"
openssl req -x509 -newkey rsa:4096 -subj "${subj}" -keyout "${script_dir}/client/code/client_key.pem" -out "${script_dir}/client/code/client_cert.pem" -sha256 -days 14 -nodes
openssl req -x509 -newkey rsa:4096 -subj "${subj}" -keyout "${script_dir}/coordinator/coordinator_key.pem" -out "${script_dir}/coordinator/coordinator_cert.pem" -sha256 -days 14 -nodes
cp "${script_dir}/coordinator/coordinator_cert.pem" "${script_dir}/client/code/coordinator_cert.pem"
