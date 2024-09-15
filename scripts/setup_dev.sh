# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# deps
uv sync
# playwright
uv run playwright install-deps && uv run playwright install
