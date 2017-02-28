#!/usr/bin/env bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT="$( dirname "${DIR}" )"

docker build --pull -t agentarchives:py2 -f ${DIR}/Dockerfile.2 ${ROOT}
docker run agentarchives:py2 py.test tests

docker build --pull -t agentarchives:py3 -f ${DIR}/Dockerfile.3 ${ROOT}
docker run agentarchives:py3 py.test tests
