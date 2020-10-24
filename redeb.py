#!/usr/bin/env python3

import atexit
import argparse
import os
import platform
import shutil
import subprocess
import sys

if platform.system() == 'Darwin' and platform.processor() == 'arm64' or platform.processor() == 'arm':
    dpkg_admindir = '/Library/dpkg'

elif platform.system() == 'Linux':
    dpkg_admindir = '/var/lib/dpkg'

def cleanup():
    if os.path.isdir('.tmp'): # Cleanup files from previous run if they exist
        shutil.rmtree('.tmp')    

atexit.register(cleanup)

def main():
    parser = argparse.ArgumentParser(description='ReDEB', usage="./redeb.py -p 'package'")
    parser.add_argument('-p', '--package', help='Name of installed package', nargs=1)
    args = parser.parse_args()

    if not args.package:
        sys.exit(parser.print_help(sys.stderr))

    if os.geteuid() != 0:
        sys.exit('[ERROR] This script must be ran as root. Exiting...')

    package = args.package[0]

    dpkg_check = subprocess.run(('which', 'dpkg-deb'), stdout=subprocess.DEVNULL)

    if dpkg_check.returncode != 0:
        sys.exit('[ERROR] dpkg is not on this system. Exiting...')

    if not os.path.isfile(f'{dpkg_admindir}/info/{package}.list'):
        sys.exit(f'[ERROR] Package {package} is not installed or does not exist. Exiting...')

    if os.path.isfile(f'{package}.deb'):
        os.remove(f'{package}.deb')

    os.makedirs(f'.tmp/dpkg/{package}/DEBIAN')

    with open(f'{dpkg_admindir}/info/{package}.list', 'r+') as f:
        package_files = f.read()

    package_files = package_files.split('\n')

    for x in package_files: # Copy files in package from filesystem to work directory
        if x == '': # If there's an empty line, we've hit the end of the file
            break
        elif x == '/.' or os.path.isdir(x):
            continue

        if not os.path.isfile(x):
            print(f"[NOTE] '{x}' is included with {package}, but file not found. Continuing...")

        path = ''
        for y in range(1, len(x.split('/')) - 1):
            path += '/{}'.format(x.split('/')[y])


        if not os.path.isdir(f'.tmp/dpkg/{package}/{path[1:]}'):
            os.makedirs(f'.tmp/dpkg/{package}/{path[1:]}')

        shutil.copyfile(x, f'.tmp/dpkg/{package}/{x[1:]}')

        package_scripts = ['preinst', 'postinst', 'prerm', 'postrm']

    for x in package_scripts: # Copy any package maintainer scripts
        if not os.path.isfile(f'{dpkg_admindir}/info/{package}.{x}'):
            continue

        shutil.copyfile(f'{dpkg_admindir}/info/{package}.{x}', f'.tmp/dpkg/{package}/DEBIAN/{x}')

        os.chmod(f'.tmp/dpkg/{package}/DEBIAN/{x}', 0o755)

    with open(f'{dpkg_admindir}/status', 'r+') as f: # Get control file of package from dpkg's status file
        status = f.read()

    status = status.split('\n')

    package_status = status.index(f'Package: {package}')
    status = status[package_status:]

    package_control = ''

    for x in status:
        if x.startswith('Status:'): # Don't include installed status in control
            continue
        elif x == '':
            break

        package_control += f'{x}\n'

    with open(f'.tmp/dpkg/{package}/DEBIAN/control', 'w+') as f:
        f.write(package_control)


    build_deb = subprocess.run(('dpkg-deb', '-b', f'.tmp/dpkg/{package}', f'{package}.deb'), stdout=subprocess.DEVNULL)

    if build_deb.returncode != 0:
        sys.exit('[ERROR] Failed to build package back into deb. Exiting...')

    print(f'Package successfully rebuilt to deb: {package}.deb')  

    shutil.rmtree(f'.tmp')     

if __name__ == '__main__':
    main()