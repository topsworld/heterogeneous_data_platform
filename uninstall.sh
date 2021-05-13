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
config_name="${script_name}.config"
service_name="${script_name}.service"
log_name="${script_name}.log"
folder_bin="/usr/local/bin/"
folder_config="/usr/local/etc/${script_name}/"
folder_service="/usr/lib/systemd/system/"
folder_log="/home/swlog/"
full_folder_bin="${folder_bin}${script_name}" 
full_folder_config="${folder_config}${config_name}" 
full_folder_service="${folder_service}${service_name}"
full_folder_log="${folder_log}${log_name}"

read -p "Are you sure to uninstall the script(yes/no)?  :" result
if [[ $result == "yes" || $result == "y" ]]; then
  echo_green "Start uninstalling the ${script_name} service."
else
  echo_green "Cancel uninstall."
  exit 0
fi
# TODO: Stop service 
echo_blue "$(date "+%Y-%m-%d %H:%M:%S"): Is judging whether the service is started."
sleep 0.1s
cmd1=`sudo systemctl status ${script_name}`
if [[ $cmd1 =~ "running" ]]; then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Stopping service."
  sudo systemctl stop ${script_name}
  cmd1=`sudo systemctl status ${script_name}`
else
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Service has stopped."
fi
if [[ $cmd1 =~ "inactive" ]]; then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Disable service."
  sudo systemctl disable ${script_name}
fi

# TODO: Delete related file
echo_blue "$(date "+%Y-%m-%d %H:%M:%S"): Start deleting related files."
if [ -d "${full_folder_bin}" ]
then
  sudo rm -r "${full_folder_bin}"
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Remove folder:${full_folder_bin}."
fi
if [ -d "${folder_config}" ]; then
  sudo rm -R "${folder_config}"
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Remove folder: ${folder_config}."
fi
if [ -f "${full_folder_service}" ]
then
  sudo rm "${full_folder_service}"
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Remove file: ${full_folder_service}."
fi
if [ -f "${full_folder_log}" ]
then
  sudo rm "${full_folder_log}"
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Remove file: ${log_name}."
fi

echo_green "$(date "+%Y-%m-%d %H:%M:%S"): [OK] Uninstallation completed."