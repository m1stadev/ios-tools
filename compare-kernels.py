#!/usr/bin/env python3

#Copyright (c) 2020, @mcg29_
#Code modified by marijuanARM

import argparse
import os
import sys

def main():
	parser = argparse.ArgumentParser(description="compare-kernels.py - A script to create a diff file between 2 raw kernelcaches that img4lib can utilize.")
	parser.add_argument('-i', '--input', help='Input kernelcache', nargs=1)
	parser.add_argument('-p', '--patched', help='Patched kernelcache', nargs=1)
	parser.add_argument('-d', '--diff', help='Diff file to write to', nargs=1)
	args = parser.parse_args()

	if not args.input or not args.patched or not args.diff:
		sys.exit(parser.print_help(sys.stderr))

	if not os.path.isfile(args.input[0]):
		sys.exit(f"[ERROR] Input kernel {args.input[0]} does not exist. Exiting...")

	if not os.path.isfile(args.patched[0]):
		sys.exit(f"[ERROR] Patched kernel {args.patched[0]} does not exist. Exiting...")

	with open(args.patched[0], 'rb') as f:
		patched = f.read()

	with open(args.input[0], 'rb') as f:
		original = f.read()

	if len(patched) != len(original):
		sys.exit(f"[ERROR] Input kernel {args.input[0]} and patched kernel {args.patched[0]} are not the same size. Exiting...")

	diff = []
	for i in range(len(original)):
		originalByte = original[i]
		patchedByte = patched[i]

		if originalByte != patchedByte:
			diff.append([hex(i), hex(originalByte), hex(patchedByte)])

	with open(args.diff[0], 'w+') as f:
		f.write('#AMFI\n\n')
		for x in diff:
			data = f'{str(x[0])} {(str(x[1]))} {(str(x[2]))}'
			f.write(f'{data}\n')

	print(f'Diff file written to: {args.diff[0]}. Exiting...')

if __name__ == "__main__":
	main()
