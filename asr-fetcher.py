#!/usr/bin/env python3

import atexit
import argparse
import os
import platform
import remotezip
import requests
import shutil
import subprocess
import sys

if not platform.system() == 'Darwin':
    sys.exit('[ERROR] Unsupported OS. Exiting...')

def cleanup():
    if os.path.isdir('.tmp/asr-fetcher/ramdisk'):
        subprocess.run(('hdiutil', 'detach', '.tmp/asr-fetcher/ramdisk'), stdout=subprocess.DEVNULL)
    elif os.path.isdir('.tmp'):
        shutil.rmtree('.tmp')

def device_check(device):
    api = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed')
    data = api.json()
    if device in data['devices']:
        return True

    return False

atexit.register(cleanup)

def main():
    parser = argparse.ArgumentParser(description='ASR Fetcher', usage="./asr_fetcher.py -d 'device' [-i 'version']")
    parser.add_argument('-d', '--device', help='Device identifier (ex. iPhone9,3)', nargs=1)
    parser.add_argument('-i', '--version', help='Fetch ASR binaries for a specific iOS version (ex. 13.5)', nargs=1)
    args = parser.parse_args()

    if not args.device:
        sys.exit(parser.print_help(sys.stderr))

    if not device_check(args.device[0]):
        sys.exit(f'[ERROR] Device {args.device[0]} does not exist. Exiting...')

    hdiutil_check = subprocess.run(('which', 'hdiutil'), stdout=subprocess.DEVNULL)
    if hdiutil_check.returncode != 0:
        sys.exit("[ERROR] hdiutil binary not found. Something is very wrong (unless you're running this on an iOS device). Exiting...")

    img4lib_check = subprocess.run(('which', 'img4'), stdout=subprocess.DEVNULL)
    if img4lib_check.returncode == 0:
        img4lib = True
    else:
        img4lib = False

    img4tool_check = subprocess.run(('which', 'img4tool'), stdout=subprocess.DEVNULL)
    if img4tool_check.returncode == 0:
        img4tool = True
    else:
        img4tool = False

    cleanup()

    os.makedirs('.tmp/asr-fetcher')
    os.chdir('.tmp/asr-fetcher')

    api = requests.get(f'https://api.ipsw.me/v4/device/{args.device[0]}?type=ipsw')
    data = api.json()
    device_identifier = data['identifier']

    for x in range(0, len(data['firmwares'])):
        ipsw_download = data['firmwares'][x]['url']
        dmg_sizes = []
        ramdisk_path = f'ramdisk_{device_identifier}_{data["firmwares"][x]["version"]}_{data["firmwares"][x]["buildid"]}.dmg'
        if args.version:
            if not data['firmwares'][x]['version'] == args.version[0]:
                continue

        try:
            with remotezip.RemoteZip(ipsw_download) as f:
                for i in f.infolist():
                    if i.filename.endswith('.dmg') and not i.filename.startswith('._'):
                        dmg_sizes.append(i.file_size)
                
                dmg_sizes.sort()
                for i in f.infolist():
                    if not i.file_size == dmg_sizes[0]:
                        continue

                    print(f"Extracting ASR from iOS {data['firmwares'][x]['version']}'s IPSW")

                    f.extract(i.filename)

                    if img4lib:
                        subprocess.run(('img4', '-i', i.filename, '-o', ramdisk_path), stdout=subprocess.DEVNULL)
                    elif img4tool:
                        subprocess.run(('img4tool', '-e', '-o', ramdisk_path, i.filename), stdout=subprocess.DEVNULL)
                    else:
                        sys.exit('[ERROR] Neither img4 or img4tool were found. Exiting...')

                    os.remove(i.filename)
                    break

        except remotezip.RemoteIOError:
            print(f"[ERROR] Unable to extract ASR from iOS {data['firmwares'][x]['version']}'s IPSW, continuing...")
            continue

        attach_dmg = subprocess.run(('hdiutil', 'attach', ramdisk_path, '-mountpoint', 'ramdisk'), stdout=subprocess.DEVNULL)
        if attach_dmg.returncode != 0:
            sys.exit(f'[ERROR] Mounting DMG failed.')

        os.makedirs(f'../../ASR_Binaries/{device_identifier}/{data["firmwares"][x]["version"]}/{data["firmwares"][x]["buildid"]}')

        shutil.move('ramdisk/usr/sbin/asr', f'../../ASR_Binaries/{device_identifier}/{data["firmwares"][x]["version"]}/{data["firmwares"][x]["buildid"]}/asr')

        subprocess.run(('hdiutil', 'detach', 'ramdisk'), stdout=subprocess.DEVNULL)
        os.remove(f'ramdisk_{device_identifier}_{data["firmwares"][x]["version"]}_{data["firmwares"][x]["buildid"]}.dmg')

        if args.version:
            break

    print('Done!')

if __name__ == '__main__':
    main()