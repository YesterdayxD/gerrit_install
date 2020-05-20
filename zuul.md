### 准备
```
sudo yum install epel-release
sudo yum update
sudo yum install docker docker-compose git python-pip
sudo pip install git-review

sudo systemctl enable docker.service
sudo systemctl start docker.service
```
出现问题
```
git: ‘interpret-trailers’ is not a git command. See ‘git --help’.
cannot insert change-id line in .git/COMMIT_EDITMSG
```
解决方案
```
rpm -e --nodeps git #单独移除git

 yum install -y curl-devel expat-devel gettext-devel openssl-devel zlib-devel gcc perl-ExtUtils-MakeMaker

 wget https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.12.2.tar.gz

 tar xf git-2.12.2.tar.gz -C /usr/src/
 cd /usr/src/git-2.12.2
 
 ./configure prefix=/usr/local/git/
 make && make install
 
 echo PATH=/usr/local/git/bin:$PATH >> /etc/profile.d/git.sh
 . /etc/profile.d/git.sh
 git --version
 
```
参考：https://blog.csdn.net/a10703060237/article/details/89704924


- hosts: all
  tasks:
    - debug:
        msg: Hello world!
### centos基本环境配置
```
sudo yum update -y
sudo systemctl reboot
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
sudo yum install -y git2u-all python35u python35u-pip python35u-devel java-1.8.0-openjdk
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 10
sudo alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.5 10 #如果这一条执行报错，下的命令替换为
sudo pip3 install python-openstackclient bindep
(sudo /usr/bin/pip3.5  install python-openstackclient bindep)
```
### 安装zookeeper
参考：https://zuul-ci.org/docs/zuul/howtos/centos7_setup.html
```
sudo bash -c "cat << EOF > /etc/yum.repos.d/bigtop.repo
[bigtop]
name=Bigtop
enabled=1
gpgcheck=1
type=NONE
baseurl=http://repos.bigtop.apache.org/releases/1.2.1/centos/7/x86_64
gpgkey=https://dist.apache.org/repos/dist/release/bigtop/KEYS
EOF"
sudo yum install -y zookeeper zookeeper-server
sudo systemctl start zookeeper-server.service
sudo systemctl status zookeeper-server.service
sudo systemctl enable zookeeper-server.service
```
如果yum安装出现问题，采用以下离线安装
zookeeper手动安装
```
https://mirrors.tuna.tsinghua.edu.cn/apache/zookeeper/zookeeper-3.4.14/zookeeper-3.4.14.tar.gz
tar zxvf zookeeper-3.4.14.tar.gz -C /usr/local
cd /usr/local/zookeeper-3.4.14/
cp conf/zoo_sample.cfg conf/zoo.cfg
```
#### 修改zoo.cfg
```
tickTime=2000
# The number of ticks that the initial 
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between 
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just 
# example sakes.
dataDir=/tmp/zookeeper
# the port at which the clients will connect
clientPort=2181
```
#### 启动
`/usr/local/zookeeper-3.4.14/bin/zkServer.sh start`
#### 查看状态
`/usr/local/zookeeper-3.4.14/bin/zkServer.sh status`
#### 停止
`/usr/local/zookeeper-3.4.14/bin/zkServer.sh stop`
#### 开机启动
在/etc/init.d/目录下新建名称为zookeeper的文件，文件内容如下：
```
#!/bin/bash
#chkconfig:2345 20 90
#description:zookeeper
#processname:zookeeper
ZK_PATH=/usr/local/zookeeper # 需要修改
export JAVA_HOME=/usr/local/java/jdk1.8.0_171 # 需要修改
case $1 in
         start) sh  $ZK_PATH/bin/zkServer.sh start;;
         stop)  sh  $ZK_PATH/bin/zkServer.sh stop;;
         status) sh  $ZK_PATH/bin/zkServer.sh status;;
         restart) sh $ZK_PATH/bin/zkServer.sh restart;;
         *)  echo "require start|stop|status|restart"  ;;
esac
```
给脚本添加执行权限 
```
chmod +x zookeeper
```
添加到开机自启
```
chkconfig --add zookeeper
chkconfig --list   --查看开机自启的服务
```

### 安装nodepool
参考：https://zuul-ci.org/docs/zuul/howtos/nodepool_install.html   
初始在root的用户的home目录下执行，即`cd ~`
```
sudo groupadd --system nodepool
sudo useradd --system nodepool --home-dir /var/lib/nodepool --create-home -g nodepool
ssh-keygen -t rsa -m PEM -b 2048 -f nodepool_rsa -N ''
sudo mkdir /etc/nodepool/
sudo mkdir /var/log/nodepool
sudo chgrp -R nodepool /var/log/nodepool/
sudo chmod 775 /var/log/nodepool/
```
```
# All:
git clone https://opendev.org/zuul/nodepool
pushd nodepool/

# For Fedora and CentOS:
sudo yum -y install $(bindep -b compile)

# For openSUSE:
sudo zypper install -y $(bindep -b compile)

# All:
sudo pip3 install .
popd
```
```
pushd nodepool/
sudo cp etc/nodepool-launcher.service /etc/systemd/system/nodepool-launcher.service
sudo chmod 0644 /etc/systemd/system/nodepool-launcher.service
popd
```
```
pushd nodepool/
sudo mkdir /etc/systemd/system/nodepool-launcher.service.d
sudo cp etc/nodepool-launcher.service.d/centos.conf \
        /etc/systemd/system/nodepool-launcher.service.d/centos.conf
sudo chmod 0644 /etc/systemd/system/nodepool-launcher.service.d/centos.conf
popd
```
### 安装zuul
参考：https://zuul-ci.org/docs/zuul/howtos/zuul_install.html   
初始在root的用户的home目录下执行，即`cd ~`
```
$ sudo groupadd --system zuul
$ sudo useradd --system zuul --home-dir /var/lib/zuul --create-home -g zuul
$ sudo mkdir /etc/zuul/
$ sudo mkdir /var/log/zuul/
$ sudo chown zuul:zuul /var/log/zuul/
$ sudo mkdir /var/lib/zuul/.ssh
$ sudo chmod 0700 /var/lib/zuul/.ssh
$ sudo mv nodepool_rsa /var/lib/zuul/.ssh
$ sudo chown -R zuul:zuul /var/lib/zuul/.ssh
```
```
# All:
$ git clone https://opendev.org/zuul/zuul
$ pushd zuul/

# For Fedora and CentOS:
$ sudo yum -y install $(bindep -b compile)

# For openSUSE:
$ zypper install -y $(bindep -b compile)

# All:
$ tools/install-js-tools.sh

# All:
$ sudo pip3 install .
$ sudo zuul-manage-ansible
$ popd
```
#### 添加服务
```
$ pushd zuul/
$ sudo cp etc/zuul-scheduler.service /etc/systemd/system/zuul-scheduler.service
$ sudo cp etc/zuul-executor.service /etc/systemd/system/zuul-executor.service
$ sudo cp etc/zuul-web.service /etc/systemd/system/zuul-web.service
$ sudo chmod 0644 /etc/systemd/system/zuul-scheduler.service
$ sudo chmod 0644 /etc/systemd/system/zuul-executor.service
$ sudo chmod 0644 /etc/systemd/system/zuul-web.service
$ popd
```
```
$ pushd zuul/
$ sudo mkdir /etc/systemd/system/zuul-scheduler.service.d
$ sudo cp etc/zuul-scheduler.service.d/centos.conf \
    /etc/systemd/system/zuul-scheduler.service.d/centos.conf
$ sudo chmod 0644 /etc/systemd/system/zuul-scheduler.service.d/centos.conf
$ sudo mkdir /etc/systemd/system/zuul-executor.service.d
$ sudo cp etc/zuul-executor.service.d/centos.conf \
    /etc/systemd/system/zuul-executor.service.d/centos.conf
$ sudo chmod 0644 /etc/systemd/system/zuul-executor.service.d/centos.conf
$ sudo mkdir /etc/systemd/system/zuul-web.service.d
$ sudo cp etc/zuul-web.service.d/centos.conf \
    /etc/systemd/system/zuul-web.service.d/centos.conf
$ sudo chmod 0644 /etc/systemd/system/zuul-web.service.d/centos.conf
$ popd
```
