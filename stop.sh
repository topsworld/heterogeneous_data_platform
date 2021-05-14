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

read -p "Are you sure to stop the script(yes/no)?  :" result
if [[ $result == "yes" || $result == "y" ]]; then
  echo_green "Start stopping the ${script_name} service."
else
  echo_green "Cancel stop service."
  exit 0
fi
# TODO: Stop service 
echo_blue "$(date "+%Y-%m-%d %H:%M:%S"): Is judging whether the service is exsit."
cmd0=`sudo systemctl status ${script_name}`
if [[ $cmd0 =~ "loaded" ]]; then
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Service exsit."
else
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Service not exsit."
  exit 1
fi
if [[ $cmd0 =~ "running" ]]; then
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Stopping service."
  sudo systemctl stop ${script_name}
else
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Service has stopped."
fi
cmd1=`sudo systemctl status ${script_name} | grep "inactive"`
if [[ $cmd1 =~ "inactive" ]]; then
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): [OK] Stop completed."
else
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): [Err] Stop failure, status information is as follows."
  sudo systemctl status ${script_name}
fi

