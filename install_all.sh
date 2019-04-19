#!/bin/bash

set -eu

echo "Installing every script under /usr/local/bin"
sudo cp rpl.py /usr/local/bin/rpl
echo "rpl.py available as rpl"
