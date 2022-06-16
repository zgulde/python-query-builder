import sys
import os
from time import sleep, strftime
import argparse
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--poll-time', type=float, default=1.0)
parser.add_argument('file')
parser.add_argument('cmd')
args = parser.parse_args()

if not os.path.isfile(args.file):
    print(f'Error: {args.file} is not a file.')
    sys.exit(1)

hash = hashlib.md5(open(args.file).read().encode()).hexdigest()

while True:
    sleep(args.poll_time)
    new_hash = hashlib.md5(open(args.file).read().encode()).hexdigest()
    if new_hash == hash:
        continue
    print(f'{strftime("%Y-%m-%d %H:%M:%S")} File changed! Running {args.cmd}')
    os.system(args.cmd)
    hash = new_hash

