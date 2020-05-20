## puppet的工作机制
定义：通过puppet的声明性配置语言定义基础设置配置的目标状态；

模拟：强制应用改变的配置之前先进行模拟性应用；

强制：自动、强制部署达成目标状态，纠正任何偏离的配置；

报告：报告当下状态及目标状态的不同，以及达成目标状态所进行的任何强制性改变；

## 资源
### 资源抽象
1. 相似的资源被抽象成同一种资源**“类型”** ，如程序包资源、用户资源及服务资源等；
2. 将资源属性或状态的描述与其实现方式剥离开来，如仅说明安装一个程序包而不用关心其具体是通过yum、pkgadd、ports或是其它方式实现；
3. 仅描述资源的目标状态，也即期望其实现的结果，而不是其具体过程，如“确定nginx 运行起来” 而不是具体描述为“运行nginx命令将其启动起来”；
### 资源属性中的三个特殊属性
1. Namevar：可简称为name；
2. ensure：资源的目标状态；
3. Provider：指明资源的管理接口；
### 资源的特殊属性
puppet中也提供了before、require、notify和subscribe四个参数来定义资源之间的依赖关系和通知关系。

>before：表示需要依赖于某个资源   
>require：表示应该先执行本资源，在执行别的资源    
>notify：A notify B：B依赖于A，且A发生改变后会通知B；   
>subscribe：B subscribe A：B依赖于A，且B监控A资源的变化产生的事件；

同时，依赖关系还可以使用->和～>来表示：
>-> 表示后资源需要依赖前资源  
>~> 表示前资源变动通知后资源调用
## file 
管理系统本地文件

1. 设置文件权限和属主
2. 管理文件内容,可以基于模板的内容管理
3. 支持管理目录
4. 从远程服务器复制整个目录到本地

### 示例

设置文件权限
```
file { "/var/www/my/file":
    source => "/path/in/nfs/or/something",
    mode   => 666
}
```
设置文件内容
```
# 把文件的内容设置为content 参数后面的字符串, 新行,tab,空格可用 escaped syntax 表示. 
# 这个参数主要用于提供一种简洁的基于模板的的文件内容设置.例如
define resolve(nameserver1, nameserver2, domain, search) {
    $str = "search $search
            domain $domain
            nameserver $nameserver1
            nameserver $nameserver2"
    file { "/etc/resolv.conf":
        content => $str
    }
}
```
从远程拷贝
```
class sendmail {
    file { "/etc/mail/sendmail.cf":
        source => "puppet://server/module/sendmail.cf"
    }
}
# 上面的代码从puppet服务器上面下载sendmail.cf,覆盖到 /etc/mail/sendmail.cf
```
## package
管理软件包的安装和升级

管理软件包,现在分成两派,一派是自己能解决软件依赖,例如apt-get,yum ; 另一类是不能解决软件依赖,例如 dpkg,rpm ; puppet会根据你运行puppet的环境来自动判断你是用的什么包管理系统.当然你也可以手工设定 provider 参数让puppet用什么命令来管理软件包. 每个provider需要一些依赖来完成各项功能. 因此你必须为provider提供这些依赖
### 重要参数
1. ensure
设置该软件包应该在什么状态. installed 表示要安装该软件,也可以写成present; absent 表示反安装该软件,pureged 表示干净的移除该软件,latest 表示安装软件包的最新版本.
2. source
去那里找软件的安装包,例如rpm的包地址,必须是本地地址或者URL
3. namevar
该资源的namevar ; 软件包的名字
### 示例
```
package {
    ["vim","iproute","x-window-system","fcitx","netenv","xtrlock","ssh-askpass","mplayer","rxvt-unicode","curl","mtr"]:
    ensure => installed;
    ["pppoe","pppoe-conf"]:
    ensure => absent;
    }
```

## service

管理系统运行的服务进程,不幸的是不同的系统管理服务的方式是多样的. 有些系统上面对于服务管理很简单,有些系统提供复杂的强大的服务管理功能.puppet提供最基本的服务管理,你也可以指定provider,使用一些特性.

注意,当一个服务从另一个资源收到一个事件,服务会重启,例如配置文件修改,可以要求相应的服务重启.不同的平台重启命令不同,你也可以手工指定重启服务的命令.
### 重要参数
1. enable
服务在开机的时候是否启动,可以设置的值是true和false,需要provider支持enableable

2. ensure
是否运行服务, running表示运行服务,stopped 表示停止服务
### 示例
```
service { 
            "ssh":
             ensure => running;
            "nfs":
             ensure => stopped;
           }
```
## cron
安装和管理crontab任务
### 重要参数
1. command
crontab要执行的命令, 环境变量按照系统本地规则进行管理,推荐使用绝对路径.
2. user
把该crontab加到那个用户的crontab列表,默认是运行puppet的用户
3. hour
运行crontab的小时,可设置成0-23
### 示例
```
# 除了用户和command两个参数以外,其他的参数都是可选项.
cron { logrotate:
    command => "/usr/sbin/logrotate",
    user => root,
    hour => 2,
    minute => 0
}
```
## exec
让puppet执行外部命令

多次反复用这个方式执行命令是有威胁性的,因此建议对执行的命令进行加锁或者类似的处理. 你也可以让exec只有在收到一个其他资源的事件的时候才执行. 因为exec资源是一种挥发性资源,命令执行完了,这个资源可以说就处理完了. 因此在不同的类里面,exec资源的名字可以是相同的,这是exec资源特殊的地方。
### 重要参数
1. cwd
指定命令执行的目录。如果目录不存在，则命令执行失败。
2. path
命令执行的搜索路径。如果path没有被定义，命令需要使用绝对路径。路径可以以数组或以冒号分隔的形式来定义。
3. creates
指定命令所生成的文件。如果提供了这个参数，那么命令只会在所指定的文件不存在的情况的被执行。
### 示例
```
exec { "tar xf /my/tar/file.tar":
    cwd => "/var/tmp",
    creates => "/var/tmp/myfile",
    path => ["/usr/bin", "/usr/sbin"]
}
```
## 类
类可以把多个相关的资源定义在一起,组成一个类，类可以继承。
```
class   ssh {
    file    {
    "/etc/ssh/sshd_config" :
    source  =>   " puppet://$fileserver/ssh/sshd_config.cfg " ;
    }
    package  {
    " ssh " :
    ensure  =>   installed;
    }
    service    {
    " ssh " :
    ensure  =>  running ;
    }
}
```
这里，file/etc/ssh/sshd_config的内容是从puppet服务器上面下载的，file资源的内容可以从

别的url得到，也可以erb模板生成，erb模板是很强大的工具，这个后面会说到。package

资源安装ssh软件，service资源保证ssh服务在运行状态。
## 函数
函数（在puppet中称为“defination”）可以把多个资源包装成一个资源，或者把一个资源包装成一个模型，便于使用。

例如，在debian里面管理一个apache虚拟机非常简单,把一个虚拟主机的配置文件放到/etc/sites-available/里面,

然后做一个符号链接到/etc/sites-enabled目录。 

你可以为你每个虚拟主机复制同样的配置代码，但是如果你使用下面的代码就会更好和更简单：
```
define virtual_host($docroot, $ip, $order = 500, $ensure = “enabled”) {

    $file = “/etc/sites-available/$name.conf”

    # The template fills in the docroot, ip, and name.

    file { $file:

    content => template(“virtual_host.erb”),

    notify  => Service[apache]

    }
}
    file { “/etc/sites-enabled/$order-$name.conf”:

    ensure => $ensure ? {

    enabled  => $file,

    disabled => absent
    }
}
```
然后,你就可以使用这个定义来管理一个apache虚拟主机，如下面代码所示：
```
virtual_host { “reductivelabs.com”:

    order   => 100,
    ip      => “192.168.0.100″,
    docroot => “/var/www/reductivelabs.com/htdocs”
}
```
## 节点
puppet如何区分不同的客户端，并且给不同的服务端分配manifest呢？puppet使用叫做node的语法来做这个事情，node 后面跟客户端的主机名3,例如下面的例子：
```
node 'host1.example.com' {
    include ssh
}
node 'host2.example.com' {
    include apache, mysql, php
}
```
当主机host1.example.com来连服务端时，只会执行node 'host1.example.com'里面的代码，不会执行node host2.example.com里面的代码。正如前面所说，可以定义一个default
结点。比如没有针对host3的node配置，host3就用default的配置了。在这里include的意思是include 类。同样，节点也支持继承。
## 变量和数组
### 变量
puppet也和其他语言一样，支持变量和数组，puppet用$符号定义变量，变量的内容用双引号括起来。
### 示例
```
$test="hello, guys"

file{
    "/tmp/test":
    content => $test;
}
```
### 数组
puppet利用方括号来定义数组，数组的内容由逗号分割，
```
[ "apache2" , "httpd" , "ssh"]
```
## 模块
1. 一个模块就是一个/etc/puppet/modules目录下面的一个目录和它的子目录，在puppet的主文件site.pp里面用import modulename可以插入模块。新版本的puppet可以自动插入/etc/puppet/modules目录下的模块。
2. 引入模块，可以结构化代码，便于分享和管理。例如关于apache的所有配置都写到apache模块下面。
3. 一个模块目录下面通常包括三个目录：files，manifests，templates。manifests 里面必须要包括一个init.pp的文件，这是该模块的初始（入口）文件，导入一个模块的时候，会从init.pp开始执行。可以把所有的代码都写到init.pp里面，也可以分成多个pp文件，init 再去包含其他文件。files目录是该模块的文件发布目录，puppet提供一个文件分发机制，类似rsync的模块。templates 目录包含erb模型文件，这个和file资源的template属性有关。
4. puppet安装好以后，modules目录是没有的，自己建立一个就行，然后在里面可以新增加你的模块。
## 实例
实例：一个slave从master中获取其manifest，该maniftest要求slave依次做以下工作：安装gcc，创建文件夹/home/dxc/test，下载文件hello.c程序，编译hello.c。
```
Master上代码的目录结构(/etc/puppet目录）如下：
|– auth.conf
|– fileserver.conf   #puppet文件服务器配置文件
|– manifests   #puppet主文件所在目录
|   |– modules.pp        #puppet各个模块汇总
|   |– nodes         #各个slave要处理的模块
|   |   `– execHello.pp      #hello模块对应由那些slave处理
|   `– site.pp                  #puppet主文件（入口文件）
|– modules     #puppet的各个模块所在文件
|   `– hello   #hello模块
|       |– files    #该模块对应的文件资源，可能是要发送给slave的配置文件等
|       |   `– hello.c
|       `– manifests   #模块的manifest文件
|           `– init.pp                  #模块入口文件
`– ssl       #puppet的证书文件目录
```
程序执行流程

代码调用顺序是：

Slave发起连接请求 ＝》site.pp ＝》nodes ＝》modules ＝》init.pp

首先，slave向发起master连接请求，进行证书验证；

接着，证书验证通过后，master会直接找到入口文件manifests目录下的site.pp文件，该文件可能包含一些全局变量，参数缺省值（当各个模块没有设置这些参数时，它们的缺省值）以及其它pp文件的调用（在该例子中，会调用modules.pp和nodes下的各个pp文件）；

然后，master通过nodes下的各个pp文件定位到该slave要执行的模块（init.pp是各个模块的入口），汇总这些模块代码返回给slave；

最后，slave根据master发过来的manifest，配置信息。


