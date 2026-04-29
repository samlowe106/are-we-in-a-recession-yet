# install uv using one of the following:
# curl -LsSf https://astral.sh/uv/install.sh | sh
# winget install --id=astral-sh.uv  -e

uv init
uv add pre-commit pytest

pre-commit autoupdate
pre-commit install

rm setup.sh
