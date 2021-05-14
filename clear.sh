echo "Clear cache file"
script_path=$(dirname $(readlink -f $0))
sudo rm ${script_path}/bin/*.pyc > /dev/null
sudo rm -R ${script_path}/bin/__*__ > /dev/null
sudo rm -R ${script_path}/bin/log/*.log > /dev/null
sudo rm -R ${script_path}/bin/*.conf.current > /dev/null
echo "Cache file cleanup completed"