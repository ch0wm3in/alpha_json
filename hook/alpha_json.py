from __future__ import annotations

import argparse
import json
import sys
from difflib import unified_diff
from typing import Mapping
from typing import Sequence


class Sorter(object):

    def sort_by_key(self, data, key):
        
        return sorted(data, key=lambda k: k[key])


def _get_pretty_format(
        contents: str,
        indent: str,
        alpha_key: str
        
) -> str:
    
    sorter = Sorter()
    
    contents = json.loads(contents)

    try:
        contents = sorter.sort_by_key(contents, alpha_key)
    except Exception:
        pass
    contents = json.dumps(contents, indent=indent, ensure_ascii=False)

    
    json_pretty = json.dumps(
        json.loads(contents),
        indent=indent,
        ensure_ascii=False,
    )
    return f'{json_pretty}\n'


def _autofix(filename: str, new_contents: str) -> None:
    print(f'Fixing file {filename}')
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(new_contents)


def parse_num_to_int(s: str) -> int | str:
    """Convert string numbers to int, leaving strings as is."""
    try:
        return int(s)
    except ValueError:
        return s


def parse_topkeys(s: str) -> list[str]:
    return s.split(',')


def get_diff(source: str, target: str, file: str) -> str:
    source_lines = source.splitlines(True)
    target_lines = target.splitlines(True)
    diff = unified_diff(source_lines, target_lines, fromfile=file, tofile=file)
    return ''.join(diff)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--autofix',
        action='store_true',
        dest='autofix',
        help='Automatically fixes encountered not-pretty-formatted files',
    )
    parser.add_argument(
        '--indent',
        type=parse_num_to_int,
        default='2',
        help=(
            'The number of indent spaces or a string to be used as delimiter'
            ' for indentation level e.g. 4 or "\t" (Default: 2)'
        ),
    )

    parser.add_argument(
        '--alphakey',
        type=str,
        default='',
        help=(
            'Key to alpha sort on (Default:)'
        ),
    )
    
    
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    status = 0

    for json_file in args.filenames:
        with open(json_file, encoding='UTF-8') as f:
            contents = f.read()

        try:
            pretty_contents = _get_pretty_format(
                contents, args.indent, args.alphakey
            )
        except ValueError:
            print(
                f'Input File {json_file} is not a valid JSON, consider using '
                f'check-json',
            )
            return 1

        if contents != pretty_contents:
            if args.autofix:
                _autofix(json_file, pretty_contents)
            else:
                diff_output = get_diff(contents, pretty_contents, json_file)
                sys.stdout.buffer.write(diff_output.encode())

            status = 1

    return status


if __name__ == '__main__':
    raise SystemExit(main())