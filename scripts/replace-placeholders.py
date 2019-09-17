#!/usr/bin/env python3.7

import argparse
import re


def main(args):
    with open(args.source) as file:
        content = file.read()

    for pattern, filename in re.findall(r'(\{!(.*)!\})', content):
        with open(filename) as file:
            match_content = file.read()

        dest_content = re.sub(pattern, match_content, content)

        with open(args.dest, mode='w') as file:
            file.write(dest_content)

        with open(args.dest) as file:
            content = file.read() 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Replace placeholders with it's file contents"
    )
    parser.add_argument(
        'source',
        metavar='SOURCE',
        type=str,
        help='File to parse'
    )
    parser.add_argument(
        'dest',
        metavar='DEST',
        type=str,
        help='destination file'
    )
    args = parser.parse_args()
    main(args)
