# AGENTS

## Project snapshot

- This repository is a Python game project called Skakavi Krompir. See [README.md](README.md) for the high-level overview and release notes.
- The primary game implementation is the Pygame version under [original](original); it is the mainline build and the code most likely to contain the authoritative gameplay logic.
- [main.py](main.py) is a launcher for the separate Kivy variant, which is experimental and partially unfinished; treat it as secondary unless a task specifically mentions Kivy.
- Shared utilities live in [shared](shared), and packaging is driven by [build.sh](build.sh) and Nuitka; asset files are bundled from [assets](assets).

## Working conventions

- Prefer the mainline logic in [original](original) for gameplay fixes and new features unless the task explicitly targets the experimental Kivy version in [kivy_game](kivy_game).
- Keep shared logic in [shared](shared) when it is used by both builds, especially updater-related behavior.
- Preserve exact matching semantics for release assets and updater behavior; a loose substring comparison can select the wrong asset. See [shared/updater.py](shared/updater.py) and [tests/test_updater_asset_filter.py](tests/test_updater_asset_filter.py).
- Do not modify generated build output or release artifacts unless the task specifically requires it.

## Commands

- Run the repository tests that do not require the full desktop runtime: `python3 -m unittest discover -s tests -p 'test_*.py' -q`
- If the Kivy app itself is needed, first install the runtime deps from [README.md](README.md) and the bootstrap flow in [build.sh](build.sh): `pip install pygame nuitka requests Pillow customtkinter`
- Build the packaged binary: `./build.sh`
- Launch locally: `python3 main.py`

## Useful files

- [README.md](README.md)
- [build.sh](build.sh)
- [main.py](main.py)
- [shared/updater.py](shared/updater.py)
- [tests/test_updater_asset_filter.py](tests/test_updater_asset_filter.py)
