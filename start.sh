#!/bin/bash
:<<EOF
Python program automatic installation script
EOF

# TODO: Function to display message
function echo_blue(){
  echo -e "\033[34m$1\033[0m"
}
# green to echo 
function echo_green(){
  echo -e "\033[32m$1\033[0m"
}
# Error
function echo_red(){
  echo -e "\033[31m\033[01m$1\033[0m"
}
# warning
function echo_yellow(){
  echo -e "\033[33m\033[01m$1\033[0m"
}

# TODO: Get script name
script_name=`basename $(dirname $(readlink -f $0))`

# TODO: Start service 
echo_blue "$(date "+%Y-%m-%d %H:%M:%S"): Is judging whether the service is exsit."
cmd0=`sudo systemctl status ${script_name}`
if [[ $cmd0 =~ "loaded" ]]; then
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Service exsit."
else
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Service not exsit, unable to start."
  exit 1
fi
if [[ $cmd0 =~ "running" ]]; then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Service is running."
  exit 0
fi

sudo systemctl start $script_name
cmd1=`sudo systemctl status ${script_name}`
if [[ $cmd1 =~ "running" ]]; then
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): [OK] Start completed."
else
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): [Err] Start failure, status information is as follows."
  sudo systemctl status ${script_name}
fi

