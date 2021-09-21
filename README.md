# iOS Tools
A repository with scripts that can be helpful for jailbreaking.

## Requirements
- Python 3
- A macOS or Linux computer (although not all scripts support Linux)
- Required libraries:
    - `pip3 install -r requirements.txt`

## [`extract-nonce.py`](https://github.com/m1stadev/ios-tools/blob/master/extract-nonce.py)
- A script to extract an apnonce and sepnonce from an SHSH blob.

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-h` | `--help` | Shows all options avaiable |
| `-s` | `--shsh SHSH` | Path to SHSH |

## [`asr-fetcher.py`](https://github.com/m1stadev/ios-tools/blob/master/asr-fetcher.py)
- A script (macOS only) to extract ASR binaries from each iOS version's IPSW for an iOS device.

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-h` | `--help` | Shows all options avaiable |
| `-d` | `--device DEVICE` | Device identifier (ex. iPhone9,3) |
| `-i` | `--version VERSION` | Fetch ASR binaries from a single iOS version's IPSW (ex. 13.5) |

## [`redeb.py`](https://github.com/m1stadev/ios-tools/blob/master/redeb.py)
- A script to package installed debian packages back into a DEB. Works on both iOS and Debian-based Linux distributions.

| Option (short) | Option (long) | Description |
|----------------|---------------|-------------|
| `-h` | `--help` | Shows all options avaiable |
| `-p` | `--package PACKAGE` | Path to installed package |

## [`wiki-proxy.py`](https://github.com/m1stadev/ios-tools/blob/master/wiki-proxy.py)
- A rewrite of [tihmstar](https://twitter.com/tihmstar)'s [wikiproxy.py](https://github.com/tihmstar/libipatcher/blob/master/wikiproxy.py) that utilizes MediaWiki browsing libraries instead of parsing raw HTML documents from The iPhone Wiki with firmware keys.
