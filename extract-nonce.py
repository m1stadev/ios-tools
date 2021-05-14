#!/usr/bin/env python3

import atexit
import argparse
import binascii
import os
import platform
import shutil
import subprocess
import sys

if platform.system() == 'Linux':
    img4tool_binary = os.path.dirname(os.path.abspath(__file__)) + '/resources/bin/img4tool_linux'
elif platform.system() == 'Darwin':
    img4tool_binary = os.path.dirname(os.path.abspath(__file__)) + '/resources/bin/img4tool_macos'
else:
    sys.exit('[ERROR] Unsupported OS. Exiting...')

def cleanup():
    if os.path.isdir('.tmp'):
        shutil.rmtree('.tmp')

atexit.register(cleanup)

def main():
    parser = argparse.ArgumentParser(description='Extract ApNonce & SepNonce from SHSH')
    parser.add_argument('-s', '--shsh', help='Path to SHSH', nargs=1)
    args = parser.parse_args()

    if not args.shsh:
        sys.exit(parser.print_help(sys.stderr))

    if not os.path.isfile(args.shsh[0]):
        sys.exit(f'[ERROR] SHSH not found at given path: {args.shsh[0]}. Exiting...')

    cleanup()

    os.makedirs('.tmp')

    img4tool = subprocess.run((img4tool_binary, '-e', '-s', args.shsh[0], '-m', '.tmp/IM4M'), stdout=subprocess.PIPE, universal_newlines=True)
    if not 'Saved IM4M to .tmp/IM4M' in img4tool.stdout:
        sys.exit('[ERROR] Failed to extract IM4M from SHSH. Exiting...')

    with open('.tmp/IM4M', 'rb') as f:
        IM4M = binascii.hexlify(f.read())

    ApNonce = IM4M[160:224].decode('utf-8')
    SepNonce = IM4M[526:566].decode('utf-8')

    print(f'ApNonce: {ApNonce}')
    print(f'SepNonce: {SepNonce}')

    shutil.rmtree('.tmp')

if __name__ == '__main__':
    main()