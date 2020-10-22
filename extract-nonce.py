#!/usr/bin/env python3

import argparse
import binascii
import os
import platform
import subprocess
import sys

if platform.system() == 'Linux':
    img4tool = './resources/bin/img4tool_linux'
elif platform.system() == 'Darwin':
    img4tool = './resources/bin/img4tool_macos'
else:
    sys.exit('[ERROR] Unsupported OS. Exiting...')

parser = argparse.ArgumentParser(description='Extract ApNonce & SepNonce from SHSH')
parser.add_argument('-s', '--shsh', help='Path to SHSH', nargs=1)
args = parser.parse_args()

if not args.shsh:
    sys.exit(parser.print_help(sys.stderr))

if not os.path.isfile(args.shsh[0]):
    sys.exit(f'[ERROR] SHSH not found at given path: {args.shsh[0]}. Exiting...')

img4tool = subprocess.run(f'{img4tool} -e -s {args.shsh[0]} -m IM4M.tmp', stdout=subprocess.PIPE, universal_newlines=True, shell=True)
if not 'Saved IM4M to IM4M.tmp' in img4tool.stdout:
    sys.exit('[ERROR] Failed to extract IM4M from SHSH. Exiting...')

with open('IM4M.tmp', 'rb') as f:
    IM4M = binascii.hexlify(f.read())

ApNonce = IM4M[160:224].decode('utf-8')
SepNonce = IM4M[526:566].decode('utf-8')

print(f'ApNonce: {ApNonce}')
print(f'SepNonce: {SepNonce}')

if os.path.isfile('IM4M.tmp'):
    os.remove('IM4M.tmp')