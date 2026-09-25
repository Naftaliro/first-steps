# first steps

a setup wizard for zorin os 18 and other ubuntu based distros. it doesn't just show you links, it actually does the stuff: codecs, flathub, drivers, backups, firewall and more, all with checkboxes so new linux people never have to open a terminal.

built with python, gtk4 and libadwaita.

## install

one line:

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/first-steps/main/scripts/install-online.sh | sudo bash
```

that installs the dependencies, downloads the latest release, checks its sha256, and sets it up. to remove it: `sudo apt remove first-steps`.

or grab the `.deb` from [releases](https://github.com/Naftaliro/first-steps/releases/latest) and double click it. from a terminal:

```bash
DEB_URL=$(curl -fsSL https://api.github.com/repos/Naftaliro/first-steps/releases/latest \
  | grep -o '"browser_download_url"[^"]*\.deb"' | grep -o 'https://[^"]*')
wget "$DEB_URL" -O first-steps-latest.deb
sudo apt install ./first-steps-latest.deb
```

or from source:

```bash
git clone https://github.com/Naftaliro/first-steps.git
cd first-steps
sudo ./install.sh          # sudo ./install.sh remove to uninstall
```

## the pages

| page | what it does |
|---|---|
| welcome | your system info (os, cpu, gpu, ram, disk) and an overview |
| codecs & media | `ubuntu-restricted-extras`, gstreamer plugins, dvd support, va-api |
| flatpak & apps | turns on flathub, then pick from 16 apps (media, productivity, internet, gaming, dev) |
| drivers | runs `ubuntu-drivers`, shows what's recommended, one click install |
| windows apps | installs bottles, optional wine stuff + gamemode, helps you make your first bottle |
| backup | sets up timeshift: schedule, how many to keep, skip home, first snapshot |
| power | power profile, what the lid does on ac / battery, auto suspend, screen dimming |
| firewall | turns on ufw (deny incoming, allow outgoing) with 8 common exceptions |
| network | connectivity check, dns (cloudflare / google / quad9), network tools |
| privacy | turns off ubuntu telemetry, whoopsie and popularity-contest, gnome privacy settings, browser extension picks |
| development | git config, editors (vs code / codium / zed and more), docker / podman, language runtimes, dev tools |
| language | language packs, input methods (ibus / fcitx5), spell check, fonts (noto / fira / cascadia) |
| extras | theme switcher, theme packs, system update, accessibility, utilities |
| summary | everything you did, what to do next, and you can export it as a markdown report |

other stuff:

- dark / light toggle (ctrl+d)
- checkmarks in the sidebar for pages you've finished
- skip button on every page if you already did something yourself
- ctrl+1-0 to jump between pages, ctrl+q to quit
- checks github for updates when it opens
- a little popup after every action saying if it worked
- uses `pkexec` with its own polkit policy, so it's one password prompt and no terminal
- installs run in the background with a spinner so the window doesn't freeze

## working on it

it's python with pygobject (gtk4 + libadwaita).

| what | where |
|---|---|
| main app | `first_steps/app.py` |
| updater | `first_steps/updater.py` |
| the 14 pages | `first_steps/pages/` |
| base page class | `first_steps/pages/__init__.py` |
| root helper | `scripts/first-steps-helper` |
| polkit policy | `data/io.github.firststeps.policy` |
| installer | `install.sh` |
| online installer | `scripts/install-online.sh` |
| .deb build | `packaging/build-deb.sh` |
| tests | `tests/` |

```bash
./first-steps                        # run it from the source folder
./packaging/build-deb.sh             # build the .deb
python3 -m pytest tests/ -v          # run the tests
```

found a bug or want something added? see [CONTRIBUTING.md](CONTRIBUTING.md). security stuff goes through [SECURITY.md](SECURITY.md).

## license

GPL-3.0-or-later, see [LICENSE](LICENSE). the icon was made for this project and is under the same license. dependencies and their licenses are listed in [NOTICE](NOTICE). not affiliated with or endorsed by zorin group.
