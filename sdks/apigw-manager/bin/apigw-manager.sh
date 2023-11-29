#!/bin/bash

bin_dir=$(dirname "$0")
root_dir=$(dirname "${bin_dir}")

python "${root_dir}/manage.py" "$@"