# 基于Python的异构数据平台

简体中文 | English

目前支持TCP、UDP、MQTT协议



# 部署说明

## 安装

打开文件夹，运行 `install.sh` 脚本

```shell
./install
```

## 卸载

打开文件夹，运行 `uninstall.sh` 脚本

```shell
./uninstall
```

## 停止

打开文件夹，运行 `stop.sh` 脚本

```shell
./stop
```

或者

```shell
sudo systemctl stop <服务名>
```

## 开启

打开文件夹，运行 `start.sh` 脚本

```shell
./start
```

或者

```shell
sudo systemctl start <服务名>
```

## 重启

打开文件夹，运行 `restart.sh` 脚本

```shell
./restart
```

或者

```shell
sudo systemctl restart <服务名>
```

## 查看状态

打开文件夹，运行 `status.sh` 脚本

```shell
./status
```

或者

```shell
sudo systemctl status <服务名>
```

【注】出现无法退出情况，按下“q”。