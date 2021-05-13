#!/bin/bash
:<<EOF
Python program automatic installation script
EOF
# TODO: Get script name
script_name=`basename $(dirname $(readlink -f $0))`
cmd0=`sudo systemctl status ${script_name}`
if [[ $cmd0 =~ "loaded" ]]; then
  echo "$(date "+%Y-%m-%d %H:%M:%S"): Service exsit."
else
  echo "$(date "+%Y-%m-%d %H:%M:%S"): Service not exsit."
  exit 1
fi
echo "$(date "+%Y-%m-%d %H:%M:%S"): Service status (Press q to exit!): "
sudo systemctl status $script_name
