#!/usr/bin/env python3

import atexit
import argparse
import os
import pathlib
import platform
import shutil
import subprocess
import sys

if platform.system() == 'Darwin' and platform.processor() == 'arm64' or platform.processor() == 'arm':
    dpkg_admindir = '/Library/dpkg'


def cleanup():
    if os.path.isfile('.tmp/restore-rootfs/.procursus_strapped'):
        subprocess.run(('umount', '.tmp/restore-rootfs'), stdout=subprocess.DEVNULL)

    if os.path.isdir('.tmp'): # Cleanup files from previous run if they exist
        shutil.rmtree('.tmp')    

if os.geteuid() != 0:
    sys.exit('[ERROR] This script must be ran as root. Exiting...')

atexit.register(cleanup)

def main():
    parser = argparse.ArgumentParser(description='Restore RootFS', usage="./restore-rootfs.py")
    args = parser.parse_args()

    if not os.path.isfile('/.procursus_strapped'):
        sys.exit('[ERROR] This script requires your device to be bootstrapped with the Procursus bootstrap (used in Odyssey & Odysseyra1n). Exiting...')

    snaputil_check = subprocess.run(('which', 'snaputil'), stdout=subprocess.DEVNULL)
    if snaputil_check.returncode != 0:
        sys.exit('[ERROR] snaputil is not installed on this device. Exiting...')

    uicache_check = subprocess.run(('which', 'uicache'), stdout=subprocess.DEVNULL)
    if uicache_check.returncode != 0:
        sys.exit('[ERROR] uikittools is not installed on this device. Exiting...')

    print('Mounting pre-jailbreak snapshot...')

    os.makedirs(f'.tmp/restore-rootfs', exist_ok=True)

    snaputil = subprocess.run(('snaputil', '-s', 'orig-fs', '/', '.tmp/restore-rootfs'), stdout=subprocess.DEVNULL)

    if snaputil.returncode != 0:
        sys.exit('[ERROR] Failed to mount pre-jailbreak snapshot. Exiting...')

    if not os.path.isdir('.tmp/restore-rootfs/Applications'):
        sys.exit('[ERROR] /Applications does not exist on pre-jailbreak snapshot. Something must be very wrong. Exiting...')


    snapshot_application_dir = os.listdir('.tmp/restore-rootfs/Applications')
    for x in os.listdir('/Applications'):
        if os.path.isfile(f'/Applications/{x}'):
            continue

        if x not in snapshot_application_dir:
            shutil.rmtree(f'/Applications/{x}')

    unmount = subprocess.run(('umount', '.tmp/restore-rootfs'), stdout=subprocess.DEVNULL)
    if unmount.returncode != 0:
        sys.exit('[ERROR] Failed to unmount pre-jailbreak snapshot. Exiting...')


    print('Getting rid of any leftover jailbreak files in /var...')
    jailbreak_files = ['/var/lib', '/var/cache', '/var/checkra1n.dmg', '/var/dropbear_rsa_host_key', '/var/mobile/.bash_history', '/var/mobile/.forward', '/var/mobile/.ssh', '/var/root/.ssh', '/var/mobile/Downloads', '/var/binpack']
    for x in jailbreak_files:
        if os.path.isfile(x):
            os.remove(x)
            
        elif os.path.isdir(x):
            shutil.rmtree(x)

    print('Running uicache...')

    uicache = subprocess.run(('uicache', '-a'), stdout=subprocess.DEVNULL)
    if uicache.returncode != 0:
        sys.exit('[ERROR] Failed to run uicache (wtf?). Exiting...')

    print('Reverting to pre-jailbreak snapshot...')

    restore_rootfs = subprocess.run(('snaputil', '-r', 'orig-fs', '/'), stdout=subprocess.DEVNULL)
    if restore_rootfs.returncode != 0:
        sys.exit('[ERROR] Failed to revert to pre-jailbreak snapshot.')

    print('Successfully restored root-fs. Exiting...')

    shutil.rmtree(f'.tmp')     

if __name__ == '__main__':
    main()