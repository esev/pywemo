#!/usr/bin/env bash
set -euf -o pipefail

SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SELF_DIR/.."

source "$SELF_DIR/common.sh"

assertPython

echo
echo "===Settting up venv==="
enterVenv

echo
echo "===Installing poetry==="
pip install poetry

echo
echo "===Installing dependencies==="
poetry install

echo
echo "===Installing pre-commit hooks==="
pre-commit install

echo
echo "===Validate with rstcheck==="
rstcheck README.rst

echo
echo "===Sort imports with isort==="
ISORT_ARGS=""
if [[ ! -z "${CI:-}" ]]; then
  ISORT_ARGS="--check-only"
fi
isort $ISORT_ARGS .

echo
echo "===Format with black==="
BLACK_ARGS=""
if [[ ! -z "${CI:-}" ]]; then
  BLACK_ARGS="--check"
fi
black $BLACK_ARGS .

echo
echo "===Lint with flake8==="
flake8

echo
echo "===Lint with pylint==="
pylint pywemo scripts

echo
echo "===Lint with mypy==="
mypy .

echo
echo "===Test with pytest and coverage==="
coverage run -m pytest --vcr-record=none
coverage report --skip-covered
coverage lcov

echo
echo "===Building package==="
poetry build

echo
echo "===Calculate checksums==="
(cd dist && set +f && sha256sum *) > .cache/sha256sum.txt

if [[ ! -z "${ENV_OUTPUT_VAR:-}" ]]; then
  echo
  echo "===Generating output variables for CI==="
  END=$(dd if=/dev/urandom bs=15 count=1 status=none | base64)
  cat <<EOF | tee "${!ENV_OUTPUT_VAR}"
hashes=$(base64 -w0 < .cache/sha256sum.txt)
version=$(poetry version -s)
coverage-lcov=.cache/coverage.lcov
build-artifacts<<$END
.cache/coverage.lcov
.cache/sha256sum.txt
dist/
$END
EOF
fi

echo
echo "Build complete"
