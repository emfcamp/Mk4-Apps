#!/usr/bin/env bash

TARGET=$(dirname `pwd`)"/upip"
rm -rf "/tmp/upip.zip"
curl -L "https://github.com/micropython/micropython-lib/archive/master.zip" -o "/tmp/upip.zip"
rm -rf "/tmp/upip"
unzip -q -a "/tmp/upip.zip" -d "/tmp/upip"
cd "/tmp/upip/micropython-lib-master"
rm -rf "$TARGET/*"
for d in `find . -maxdepth 1 -type d ! -name ".*"`; do
    echo $d;
    find "$d" -maxdepth 1 -mindepth 1 \( -name '*.py' -not -name 'test_*' -not -name 'example_*' -not -name 'setup.py' -size +10c \) -or \( -type d -not -name 'dist' -not -name '*.egg-info' -not -name '__pycache__' \) | xargs -I{} bash -c -- 'ditto {} "'"$TARGET"'/"`echo "{}" | sed -e "s/\.\/[^\/]*\///"`';
done

