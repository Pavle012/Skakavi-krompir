# Skakavi Krompir

A Flappy Bird-like game

<!-- markdownlint-disable MD033 -->
<p align="right">
  <a href="https://github.com/Pavle012/Skakavi-krompir/actions/workflows/buildalpha.yml">
    <img src="https://github.com/Pavle012/Skakavi-krompir/actions/workflows/buildalpha.yml/badge.svg" alt="Build alpha">
  </a>
</p>

## Dependencies

Just need an internet connection on first run if `pygame`, `pymunk`, `pillow`, `customtkinter`, and `pypresence` aren't already installed.
If these packages aren't already installed, the script will automatically install them—either in the virtual environment or globally.

## Download

To download the latest stable version, go to the [Releases](https://github.com/Pavle012/Skakavi-krompir/releases) page and download the latest release.

Want to download the latest alpha version? Download a binary here: [Nightly.link](https://nightly.link/Pavle012/Skakavi-krompir/workflows/buildalpha/main?preview) or you can [download the whole repo](https://github.com/Pavle012/Skakavi-krompir/archive/refs/heads/main.zip) and execute the original/main.py with Python directly.

## Discord Rich Presence

The desktop Pygame build can show your current menu, game mode, score, replay, or
multiplayer-lobby status in Discord. Rich Presence uses the Discord desktop
client's local RPC connection; it does not sign in to Discord or replace the
game's existing accounts and multiplayer services. Discord must be running, and
the user's Discord activity-sharing privacy setting must allow game activity.
While a multiplayer lobby is open, friends can use Discord's Join action to
connect to that lobby; join requests are handled from the game's main menu.

The integration is enabled by default and can be turned off in **Settings**.
Changing this option takes effect the next time the game starts. Rich Presence
displays text only; no Developer Portal changes are required. Uploading Rich
Presence art assets is optional and is not currently used by the game.
This currently targets the native desktop Pygame build; the Kivy/Android build
is not integrated, and Flatpak sandboxing may block access to Discord's local
RPC socket.
