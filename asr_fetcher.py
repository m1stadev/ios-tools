#!/usr/bin/env python3

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

def device_check(device):
    api = requests.get('https://api.ipsw.me/v2.1/firmwares.json/condensed')
    data = api.json()
    if device in data['devices']:
        return True

    return False

def main():
    parser = argparse.ArgumentParser(description='ASR Fetcher', usage="./asr_fetcher.py -d 'device' [-i 'version']")
    parser.add_argument('-d', '--device', help='Device identifier (ex. iPhone9,3)', nargs=1)
    parser.add_argument('-i', '--version', help='Fetch ASR binaries for one major iOS version (ex. 13)', nargs=1)
    args = parser.parse_args()

    if not args.device:
        sys.exit(parser.print_help(sys.stderr))

    if not device_check(args.device[0]):
        sys.exit(f'[ERROR] Device {args.device[0]} does not exist. Exiting...')

    hdiutil_check = subprocess.run('which hdiutil', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if hdiutil_check.returncode != 0:
        sys.exit('[ERROR] hdiutil binary not found. Exiting...')

    img4lib_check = subprocess.run('which img4', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if img4lib_check.returncode == 0:
        img4lib = True
    else:
        img4lib = False

    img4tool_check = subprocess.run('which img4tool', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    if img4tool_check.returncode == 0:
        img4tool = True
    else:
        img4tool = False

    if os.path.isdir('.tmp/dl/ramdisk'):
        subprocess.run('hdiutil detach .tmp/dl/ramdisk', stdout=subprocess.PIPE, universal_newlines=True, shell=True)

    if os.path.isdir('.tmp/'):
        shutil.rmtree('.tmp/')

    os.makedirs('.tmp/dl')
    os.chdir('.tmp/dl')

    api = requests.get(f'https://api.ipsw.me/v4/device/{args.device[0]}?type=ipsw')
    data = api.json()
    device_identifier = data['identifier']

    for x in range(0, len(data['firmwares'])):
        ipsw_download = data['firmwares'][x]['url']
        dmg_sizes = []
        ramdisk_path = f'ramdisk_{device_identifier}_{data["firmwares"][x]["version"]}_{data["firmwares"][x]["buildid"]}.dmg'
        if args.version:
            if not data['firmwares'][x]['version'].startswith(args.version[0]):
                continue

        try:
            with remotezip.RemoteZip(ipsw_download) as f:
                for i in f.infolist():
                    if i.filename.endswith('.dmg') and not i.filename.startswith('._'):
                        dmg_sizes.append(i.file_size)
                
                dmg_sizes.sort()
                for i in f.infolist():
                    if i.file_size == dmg_sizes[0]:
                        f.extract(i.filename)

                        print(f'Extracting ASR from iOS {data["firmwares"][x]["version"]}\'s IPSW')

                        if img4lib:
                            subprocess.run(f'img4 -i {i.filename} -o {ramdisk_path}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                        elif img4tool:
                            subprocess.run(f'img4tool -e -o {ramdisk_path} {i.filename}', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                        else:
                            sys.exit('[ERROR] Neither img4 or img4tool were found. Exiting...')

                        os.remove(i.filename)
                        break
        except remotezip.RemoteIOError:
            print(f'[ERROR] Unable to extract ASR from iOS {data["firmwares"][x]["version"]}\'s IPSW, continuing...')
            continue

        attach_dmg = subprocess.run(f'hdiutil attach {ramdisk_path} -mountpoint ramdisk', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        if attach_dmg.returncode != 0:
            sys.exit(f'[ERROR] Mounting DMG failed.')

        os.makedirs(f'../../ASR_Binaries/{device_identifier}/{data["firmwares"][x]["version"]}/{data["firmwares"][x]["buildid"]}', exist_ok=True)

        if os.path.isfile(f'../../ASR_Binaries/{device_identifier}/{data["firmwares"][x]["version"]}/{data["firmwares"][x]["buildid"]}/asr'):
            os.remove(f'../../ASR_Binaries/{device_identifier}/{data["firmwares"][x]["version"]}/{data["firmwares"][x]["buildid"]}/asr')

        shutil.move('ramdisk/usr/sbin/asr', f'../../ASR_Binaries/{device_identifier}/{data["firmwares"][x]["version"]}/{data["firmwares"][x]["buildid"]}')

        subprocess.run('hdiutil detach ramdisk', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        os.remove(f'ramdisk_{device_identifier}_{data["firmwares"][x]["version"]}_{data["firmwares"][x]["buildid"]}.dmg')

    print('Done!')

if __name__ == '__main__':
    main()