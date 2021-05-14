#!/bin/bash
:<<EOF
Python program automatic installation script
EOF
program_description="Python-based heterogeneous data platform"
program_main_name="main.py"
program_apk_package="python3:python3 pip3:python3-pip"
program_python_package="sqlalchemy:sqlalchemy paho.mqtt:paho-mqtt json:json logging:log pymysql:pymysql sqlalchemy_utils:sqlalchemy-utils threading:threading"
# TODO: Function to display message

function echo_blue()
{
  echo -e "\033[34m$1\033[0m"
}
# green to echo 
function echo_green()
{
  echo -e "\033[32m$1\033[0m"
}
# Error
function echo_red()
{
  echo -e "\033[31m\033[01m$1\033[0m"
}
# warning
function echo_yellow()
{
  echo -e "\033[33m\033[01m$1\033[0m"
}
# TODO: Function to determine whether the module exists
python_model_check()
{
  if python3 -c "import $1" >/dev/null 2>&1
  then
      echo "0"
  else
      echo "1"
  fi
}
func_apt_check()
{
  array_one=(${1//:/ })
  if ! [ ${#array_one[@]} == 2 ]; then
    echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Wrong format: ${1}, The correct format is [check_name:package_name]."
    exit 1
  fi
  if ! [ -x "$(command -v ${array_one[0]})" ]; then
    echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Installing ${array_one[1]}."
    sudo apt -y install ${array_one[1]}
  else
    echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Package [${array_one[1]}] already exists."
  fi
}
func_apt_check_all()
{
  for var in ${program_apk_package[@]}
  do
    func_apt_check $var
  done
}
#function test
#func_apt_check "pip3:python3-pip"
#func_apt_check_all
func_python_check()
{
  array_one=(${1//:/ })
  if ! [ ${#array_one[@]} == 2 ]; then
    echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Wrong format: ${1}, The correct format is [check_name:package_name]."
    exit 1
  fi
  if [ `python_model_check ${array_one[0]}` == "1" ]; then
    echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Installing python3 model: ${array_one[1]}."
    sudo pip3 install ${array_one[1]}
  else
    echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Python3 model [${array_one[1]}] already exists."
  fi
}
func_python_check_all()
{
  for var in ${program_python_package[@]}
  do
    func_python_check $var
  done
}
#func_python_check "testd:redis"
#func_python_check_all
#exit 1

# TODO: Get script name
script_name=`basename $(dirname $(readlink -f $0))`
config_name="${script_name}.config"
service_name="${script_name}.service"
folder_bin="/usr/local/bin/"
folder_config="/usr/local/etc/${script_name}/"
folder_service="/usr/lib/systemd/system/"
full_folder_bin="${folder_bin}${script_name}" 
full_folder_config="${folder_config}${config_name}" 
full_folder_service="${folder_service}${service_name}"

echo_green "Start installing the ${script_name} service."
echo "$(date "+%Y-%m-%d %H:%M:%S"): Detect script integrity."
# TODO: Check files
if ! [ -d "$(dirname $(readlink -f $0))/bin" ]
then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Missing script folder: bin."
  exit 1
fi
if ! [ -f "$(dirname $(readlink -f $0))/bin/${program_main_name}" ]
then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Missing script main file: ${program_main_name}."
  exit 1
fi
if ! [ -f "$(dirname $(readlink -f $0))/program.config" ]
then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Missing configuration file: program.config."
  exit 1
fi
if ! [ -f "$(dirname $(readlink -f $0))/program.service" ]
then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): Missing service file: program.service."
  exit 1
fi
# TODO: Determine network.
echo "$(date "+%Y-%m-%d %H:%M:%S"): Determine whether to connect to the network?"
ping -c 1 114.114.114.114 > /dev/null 2>&1
if [ ! $? -eq 0 ]; then
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): [Error]The network is not connected. Please continue after connecting!"
  exit 1
fi
# TODO: Check script Exsit
cmd0=`sudo systemctl status ${script_name}`
if [[ $cmd0 =~ "loaded" ]]; then
  read -p "$(date "+%Y-%m-%d %H:%M:%S"): Service exsit, Is it reinstalled (yes/no)?  :" result
  if [[ $result == "yes" || $result == "y" ]]; then
    echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Start reinstalling the ${script_name} service."
  else
    echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Cancel install."
    exit 0
  fi
fi
# TODO: Configuring the runtime environment.
echo "$(date "+%Y-%m-%d %H:%M:%S"): Start configuring the runtime environment."
func_apt_check_all
func_python_check_all

# TODO: Create script file
echo "$(date "+%Y-%m-%d %H:%M:%S"): Create and move the script to folder: ${full_folder_bin}."
if [ -d "${full_folder_bin}" ]
then
  sudo rm -r "${full_folder_bin}"
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Remove folder:${full_folder_bin}, and create new folder."
fi
#sudo mkdir "${full_folder_bin}"
sudo cp -R "$(dirname $(readlink -f $0))/bin" "${full_folder_bin}"
sudo chmod -R 777 "${full_folder_bin}"
# TODO: Create script config file
echo "$(date "+%Y-%m-%d %H:%M:%S"): Create the script config file: ${config_name}."
if [ -d "${folder_config}" ]; then
  sudo rm -R "${folder_config}"
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Remove folder: ${folder_config}, and create new folder."
fi
sudo mkdir "${folder_config}"
sudo cp "$(dirname $(readlink -f $0))/program.config" "${full_folder_config}"
sudo chmod -R 777 "${folder_config}"
# TODO: Create script service file
echo "$(date "+%Y-%m-%d %H:%M:%S"): Create the script self-starting service: ${service_name}."
if ! [ -d "${folder_service}" ]; then
  sudo mkdir -p "${folder_service}"
fi
if [ -f "${full_folder_service}" ]
then
  sudo rm "${full_folder_service}"
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Remove file: ${full_folder_service}, and create new file."
fi
echo "sudo sed -e \"s/program_name/${script_name}/g\" \"$(dirname $(readlink -f $0))/program.service\" > \"${full_folder_service}\"" | sudo bash
sudo sed -i "s/program_main_name/${program_main_name}/g" "${full_folder_service}"
sudo sed -i "s/program_description/${program_description}/g" "${full_folder_service}"
sudo chmod -R 777 "${full_folder_service}"
# # TODO: Create script log file
# echo "$(date "+%Y-%m-%d %H:%M:%S"): Create the script log folder: ${log_name}."
# if [ ! -d "${folder_log}" ]
# then
#   sudo mkdir "${folder_log}"
#   sudo chmod -R 777 "${folder_log}"
# fi
# if [ -f "${full_folder_log}" ]
# then
#   sudo rm "${full_folder_log}"
#   echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Remove file: ${log_name}, and create new file."
# fi

echo "$(date "+%Y-%m-%d %H:%M:%S"): Starting service: ${service_name}."
sudo systemctl daemon-reload
cmd1=`sudo systemctl status ${script_name} | grep "running"`
if [ "${cmd1}" != "" ]; then
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Service[${service_name}] exsit, restarting."
  sudo systemctl restart ${service_name}
else
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): Service[${service_name}] not exsit,creating and starting it."
  sudo systemctl enable ${service_name}
  sudo systemctl start ${service_name}
fi

echo_blue "$(date "+%Y-%m-%d %H:%M:%S"): Is judging whether the service is started."
sleep 0.5s
cmd2=`sudo systemctl status ${script_name} | grep "running"`
if [[ $cmd2 =~ "running" ]]; then
  echo_green "$(date "+%Y-%m-%d %H:%M:%S"): [OK] Service has started."
  exit 0
else
  echo_red "$(date "+%Y-%m-%d %H:%M:%S"): [Err] Service not started, please continue after troubleshooting."
  sudo systemctl status ${service_name}
  exit 1
fi

