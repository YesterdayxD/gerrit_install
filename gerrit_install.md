## gerrit下载安装
### 安装前的注意事项
关闭防火墙 

```
systemctl stop firewalld
systemctl disable firewalld #禁止开机启动
```

永久关闭selinux

```
修改/etc/selinux/config 文件
将SELINUX=enforcing改为SELINUX=disabled
```

修改主机名(可能会影响replication的同步，但是不确定，建议执行)
```
# vim /etc/hosts

127.0.0.1   localhost gerrit localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

10.7.11.211 gerrit

# reboot
```

### 数据库在线安装
#### 删除原有的安装的mariadb
```
yum remove mysql mysql-server mysql-libs compat-mysql51
```
#### 创建MariaDB.repo文件
```
vim /etc/yum.repos.d/MariaDB.repo
```

```
[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.1/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
或者
[mariadb]
name = MariaDB
baseurl = https://mirrors.ustc.edu.cn/mariadb/yum/10.1/centos7-amd64/
gpgkey=https://mirrors.ustc.edu.cn/mariadb/yum/RPM-GPG-KEY-MariaDB
gpgcheck=1
```
#### 更新yum cache
```
yum clean all
yum makecache
```
#### 安装
```
yum  install MariaDB-server MariaDB-client
```
#### 启动
```
systemctl start mariadb #启动服务
systemctl status mariadb #查看状态
systemctl enable mariadb #设置开机启动

# 以下参考，不必执行
systemctl restart mariadb #重新启动
systemctl stop mariadb.service #停止MariaDB
```
#### 登录
```
mysql -uroot -p
#第一次登录密码为空，出现输入密码的提示后直接回车。退出：exit;
```
#### 简单配置
```
mysql_secure_installation


首先是设置密码，会提示先输入密码
 
Enter current password for root (enter for none):<–初次运行直接回车
 
设置密码
 
Set root password? [Y/n] <– 是否设置root用户密码，输入y并回车或直接回车
New password: <– 设置root用户的密码
Re-enter new password: <– 再输入一次你设置的密码
 
其他配置
 
Remove anonymous users? [Y/n] <– 是否删除匿名用户，回车
 
Disallow root login remotely? [Y/n] <–是否禁止root远程登录,回车（后面授权配置）
 
Remove test database and access to it? [Y/n] <– 是否删除test数据库，回车
```
#### 配置MariaDB的字符集
```
# 使用vim /etc/my.cnf.d/server.cnf命令编辑server.cnf文件，在[mysqld]标签下添加:

init_connect='SET collation_connection = utf8_unicode_ci' 
init_connect='SET NAMES utf8' 
character-set-server=utf8 
collation-server=utf8_unicode_ci 
skip-character-set-client-handshake

# 配置初始化完成，重启Mariadb
systemctl restart mariadb

# 进入mysql查看字符集
show variables like "%character%";show variables like "%collation%";
```
#### 添加用户 设置权限
```
# 创建用户，username password 字段自行修改
create user username@localhost identified by 'password';
# 授予外网登陆权限
grant all privileges on *.* to username@'%' identified by 'password';
```

### 数据库离线安装方式一（不推荐）
1. 准备用户
```
    groupadd -r -g 306 mysql
    useradd -r -g 306 -u 306  -d /app/data mysql  /app/data  将来用来放数据，因此建议用单独的逻辑卷，随着数据量的增加，可以扩容
    不建议创建家目录
```
2. 准备数据目录
```
    以/app/data为例,建议使用逻辑卷
    chown mysql:mysql /app/data  修改文件夹和文件的权限
```
3. 准备二进制程序
```
    tar xf mariadb-VERSION-linux-x86_64.tar.gz -C /usr/local  /usr/local为编译时候指定的路径 
    cd /usr/local;ln -sv mariadb-VERSION mysql   解压后带版本号，创建软连接，便于以后升级
    chown -R root:mysql /usr/local/mysql/   记得修改权限
```
4. 准备配置文件
```
    mkdir /etc/mysql/
    cp support-files/my-large.cnf /etc/mysql/my.cnf   复制配置文件
    [mysqld]中添加三个选项：
    datadir = /app/data
    innodb_file_per_table = on  每个表生成一个独立的文件，默认是所有表一个文件，不方便管理。10.2以后的版本默认此项
    skip_name_resolve = on 禁止主机名解析，建议使用
```
5. 创建必要数据库
```
    cd /usr/local/mysql/
    ./scripts/mysql_install_db --datadir=/app/data --user=mysql    必须在mysql/目录下执行，因为bin文件在此目录下，而不是在scripts下
    此命令默认必须在/usr/local/mysql 执行，script/mysql_install_db --datadir......
```
6. 准备日志文件
```
touch /var/log/mysqld.log

chown mysql:mysql /var/log/mysqld.log
```
7. 准备服务脚本，并启动服务
```
    cp ./support-files/mysql.server /etc/rc.d/init.d/mysqld
    chkconfig --add mysqld
    systemcl start mysqld 
```
8. 安全初始化
```
     /usr/local/mysql/bin/mysql_secure_installation 执行此脚本，设置root登录范围，禁止匿名用户登录等。
```
9. 修改环境变量
```
    echo PATH=/usr/local/mysql/bin:$PATH >> /etc/profile.d/mysql.sh
    . /etc/profile.d/mysql.sh # 使之生效
```
10. 创建数据库
```
mysql

>create user  gerrit  identified  by  '123456lq?';              ##账号及密码

>create database  reviewdb  default  character  set  'utf8';   ##创建数据库并设置utf-8格式

>grant  all on reviewdb.* to gerrit;                                 ##归属

>flush  privileges;                                                                              ##刷新

systemctl restart mariadb   重启数据库服务

```
### 数据库离线安装方式二（推荐）
采用rpm包来安装

一共有四个rpm包分别是：
```
# 版本号根据实际情况选择
mariadb-5.5.64-1.el7.x86_64
mariadb-devel-5.5.64-1.el7.x86_64
mariadb-libs-5.5.64-1.el7.x86_64
mariadb-server-5.5.64-1.el7.x86_64
```
执行命令 
```
yum localinstall 包名

systemctl start mariadb #启动服务
systemctl status mariadb #查看状态
systemctl enable mariadb #设置开机启动
```
配置安全选项
```
mysql_secure_installation
```
创建数据库
```
同方式一 第10条
```

### 安装Gerrit

#### 安装java
```
yum install -y java
```

#### 下载
以下的安装使用的是root用户，安装目录为`/usr/local/gerrit`

```
mkdir -p /usr/local/gerrit
cd /usr/local/gerrit
wget https://gerrit-releases.storage.googleapis.com/gerrit-2.12.2.war
```

#### 安装

```
java -jar gerrit-2.12.2.war init -d /usr/local/gerrit # 也可以使用2.14.3版本
```

此时可一直回车采用默认配置（安装过程中最后部分是插件安装，可以此时安装(在外网的情况下)，也可后续安装），生成的配置文件。
此时可能会出现mysql-connector-java-5.1.41.jar的下载安装提示，可以选择no，后续将这个jar包复制到/usr/local/gerrit/lib下即可。（gerrit-2.12.2.war对应的jar包版本为5.1.21，gerrit-2.14.3.war对应的jar包版本为5.1.41）
`/usr/local/gerrit/etc/gerrit.config`内容如下：
```
[gerrit]
        basePath = git
        serverId = 5553780e-2bae-49a4-b253-37a587766d29
        canonicalWebUrl = http://10.7.11.212:8080/ # 访问地址，后续需要设置反向代理，实际的访问端口不再是8080
[database]
        type = mysql 
        hostname = 你的机器ip
        database = reviewdb # 之前在mysql创建的数据库
        username = gerrit # 数据库的用户 
        # database = /var/gerrit/review_site/db/ReviewDB
[auth]
        type = HTTP # 原始设置为OPENID，改为HTTP
[receive]
        enableSignedPush = false
[sendemail]
        smtpServer = localhost
[container]
        user = root
        javaHome = /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.232.b09-0.el7_7.x86_64/jre
[sshd]
        listenAddress = *:29418
[httpd]
        listenUrl = http://*:8080/
[cache]
        directory = cache                         
```
### 生成管理员账号
```
touch /usr/local/gerrit/gerrit.password
htpasswd -b /usr/local/gerrit/gerrit.password gerrit 123456lq?
```
### 添加其他账号
```
htpasswd -b /usr/local/gerrit/gerrit.password Jack 123456lq?
```
### 修改账号
```
htpasswd -b /usr/local/gerrit/gerrit.password Jack 123456jack?
```
### 删除账号
```
htpasswd -D /usr/local/gerrit/gerrit.password Jack
```

 
没有htpasswd工具，执行 `yum install httpd-tools`


### 安装httpd（暂时不用）

1. 安装 `yum install httpd`

2. 配置 `vim /etc/httpd/conf/httpd.conf`，增加以下配置

```
IncludeOptional conf.d/*.conf
<VirtualHost *:8082>
  ProxyRequests Off
  ProxyVia Off
  ProxyPreserveHost On
  <Proxy *>
    Order deny,allow
    Allow from all
  </Proxy>
  <Location />
    AuthType Basic
    AuthName "Gerrit Code Review"
    Require valid-user
    AuthUserFile /gerrit.password
   </Location>
 <Location /login/>
    AuthType Basic
    AuthName "Gerrit Code Review"
    Require valid-user
    AuthUserFile /gerrit.password
 </Location>
    ProxyPass / http://127.0.0.1:8082/
</VirtualHost>
```

### 安装nginx

1. 添加yum源，因为默认没有源没有

`rpm -Uvh http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm`

2. 安装 `yum install -y nginx`

3. 配置 `vim /etc/nginx/nginx.conf`

用以下代码替换源文件中的http部分，主要是serve部分

```
http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    server {
        listen       1357 default_server;
        server_name  _;
        root         /usr/share/nginx/html;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location / {
            auth_basic              "Gerrit Code Review";
            auth_basic_user_file    /usr/local/gerrit/gerrit.password;
            proxy_pass              http://127.0.0.1:8080;
            proxy_set_header        X-Forwarded-For $remote_addr;
            proxy_set_header        Host $host;
        }

        error_page 404 /404.html;
            location = /40x.html {
        }

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }
}
```

启动
```
systemctl start nginx #启动服务
systemctl status nginx #查看状态
systemctl enable nginx #设置开机启动
```

文件中的`listen 1357 default_server`为新的访问端口号


注意`proxy_pass http://127.0.0.1:8080`中的端口号需要跟安装gerrit时的设置保持一致，后续可以通过修改`gerrit中etc/gerrit.config`进行设置

###
启动服务

``` 
systemctl start nginx 
/usr/local/gerrit/bin/gerrit.sh start # 重启start改为restart
```

>出现问题：nginx启动失败

>解决方法：
>
>1.使用`systemctl status nginx.service -l`查看出错原因，一般是端口刚才启动的http占用80端口
>
>2.使用`sudo lsof -i:80`确认占用情况
>
>3.修改`vim /etc/httpd/conf/httpd.conf`中的
>```
>#Listen 12.34.56.78:80
>Listen 84
>```
>将原来的80改为84
>
>4.最后再次启动httpd和nginx服务
### 启动报错
1. ERROR com.google.gerrit.pgm.Daemon : Unable to start daemon
```
[gerrit@115 ~]$ /home/gerrit/gerrit_site/bin/gerrit.sh start
Starting Gerrit Code Review: FAILED

查看日志，报错如下：
[gerrit@115 ~]$ tail -f /home/gerrit/gerrit_site/logs/error_log
[2016-07-14 10:52:07,317] INFO com.google.gerrit.server.cache.h2.H2CacheFactory : Enabling disk cache /home/gerrit/gerrit_site/cache
[2016-07-14 10:52:08,110] INFO com.google.gerrit.server.config.ScheduleConfig : gc schedule parameter "gc.interval" is not configured
[2016-07-14 10:52:08,859] INFO org.eclipse.jetty.util.log : Logging initialized @4743ms
[2016-07-14 10:52:09,278] INFO com.google.gerrit.server.git.LocalDiskRepositoryManager : Defaulting core.streamFileThreshold to 2047m
[2016-07-14 10:52:09,320] INFO com.google.gerrit.server.plugins.PluginLoader : Loading plugins from /home/gerrit/gerrit_site/plugins
[2016-07-14 10:52:09,322] ERROR com.google.gerrit.pgm.Daemon : Unable to start daemon
com.google.inject.ProvisionException: Unable to provision, see the following errors:

1) No index versions ready; run Reindex

1 error
at com.google.gerrit.lucene.LuceneVersionManager.start(LuceneVersionManager.java:119)
at com.google.gerrit.lifecycle.LifecycleManager.start(LifecycleManager.java:74)
at com.google.gerrit.pgm.Daemon.start(Daemon.java:293)
at com.google.gerrit.pgm.Daemon.run(Daemon.java:205)
at com.google.gerrit.pgm.util.AbstractProgram.main(AbstractProgram.java:64)
at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
at java.lang.reflect.Method.invoke(Method.java:498)
at com.google.gerrit.launcher.GerritLauncher.invokeProgram(GerritLauncher.java:166)
at com.google.gerrit.launcher.GerritLauncher.mainImpl(GerritLauncher.java:93)
at com.google.gerrit.launcher.GerritLauncher.main(GerritLauncher.java:50)
at Main.main(Main.java:25)

解决办法：运行reindex
[gerrit@115 ~]$ java -jar gerrit-2.11.3.war reindex -d /home/gerrit/gerrit_site
[2016-07-14 10:03:43,957] [main] WARN com.google.gerrit.pgm.util.ThreadLimiter : Limiting program to 8 threads due to database.poolLimit
[2016-07-14 10:03:44,031] [main] INFO com.google.gerrit.server.git.LocalDiskRepositoryManager : Defaulting core.streamFileThreshold to 2047m
[2016-07-14 10:03:44,492] [main] INFO com.google.gerrit.server.cache.h2.H2CacheFactory : Enabling disk cache /home/gerrit/gerrit_site/cache
Reindexing changes: done
Reindexed 0 changes in 0.0s (0.0/s)

再次启动gerrit就成功了
[gerrit@115 ~]$ /home/gerrit/gerrit_site/bin/gerrit.sh start
Starting Gerrit Code Review: OK
```
2. Starting nginx: nginx: [emerg] bind() to 0.0.0.0:8091 failed (13: Permission denied)
```
nginx 启动失败,日志里面报错信息如下:


 Starting nginx: nginx: [emerg] bind() to 0.0.0.0:8095 failed (13: Permission denied)


权限拒绝，经检查发现是开启selinux 导致的。 直接关闭


getenforce   这个命令可以查看当前是否开启了selinux 如果输出 disabled 或 permissive 那就是关闭了
如果输出 enforcing 那就是开启了 selinux


1、临时关闭selinux


setenforce 0            ##设置SELinux 成为permissive模式
setenforce 1    ##设置SELinux 成为enforcing模式


2、永久关闭selinux,


修改/etc/selinux/config 文件
将SELINUX=enforcing改为SELINUX=disabled

重启机器即可

Tags: selinux , nginx绑定端口失败
```
3. 在初始化gerrit的时候出现mysql-connect的错误

将connect的jar放到`/usr/local/gerrit/lib`文件夹下

### 邮箱配置
在内网环境下关于邮箱的配置

在accounts中的preferred的字段和account_external_ids中的email_address字段添加邮箱，重启Gerrit服务

### 关于refs/for/*和refs/heads/*的问题

将reference设置为refs/heads/*，会出现直接提交到gitlab的情况，设置为refs/for/*会走相应的Gerrit流程。



### 参考文档
https://www.cnblogs.com/kevingrace/p/5651447.html

