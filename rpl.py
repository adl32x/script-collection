#!/usr/bin/env python3
import subprocess
import json
import re
import argparse
from argparse import RawTextHelpFormatter

desc = """
Search with a regexp using rg, and convert the matches
using python's re.sub.

First argument: search pattern
Second argument: replace pattern

Examples:
---------
./rpl.py foo bar --dry-run
# changes foo to bar

./rpl.py "import (?P<word>[a-z]*)" "export \g<word>" --dry-run
# changes import statements to export statements.

./rpl.py "foo ([A-Z]*) bar" "foo bar \g<1>" --dry-run
# Numbered groups. 0 is the whole match.
"""

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description=desc)
parser.add_argument('strings', metavar='N', type=str, nargs=2,
                    help='the search and replace strings.')
parser.add_argument('--dry-run', action='store_true')

args = parser.parse_args()

dry_run = args.dry_run
find = args.strings[0]
rpl = args.strings[1]



def run(args):
    run = subprocess.run(args, capture_output=True)
    return run.stdout.decode("utf-8")

rg = run(["rg", find, "--json"])

files = set()
for line in rg.splitlines():
    rg_line = json.loads(line)
    if rg_line['type'] == 'match':
        filename = rg_line['data']['path']['text']
        lnumber = rg_line['data']['line_number']
        text = rg_line['data']['lines']['text'].rstrip()
        #print("%s:%s:%s" % (filename, lnumber, text))
        files.add(filename)

for filename in files:
    mode = 'r' if dry_run else 'r+'
    with open(filename, mode) as source:
        code = source.read()
        code_replaced = re.sub(find, rpl, code)

        if not dry_run:
            source.seek(0)
            source.write(code_replaced)
        else:
            print("\033[93m%s\033[39m:" % (filename,))
            code_replaced_dry = re.sub(find, r'\033[91m\g<0>\033[39m > \033[92m'+rpl+'\033[39m', code)
            print(code_replaced_dry)
        source.close()
