## gitlab 下载安装
### 安装依赖软件
```
sudo yum install -y curl policycoreutils-python openssh-server
sudo systemctl enable sshd
sudo systemctl start sshd

sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo systemctl reload firewalld

//邮箱服务可选
sudo yum install postfix
sudo systemctl enable postfix
sudo systemctl start postfix
```
### 下载

`wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-10.0.0-ce.0.el7.x86_64.rpm`


### 安装gitlab

`rpm -ivh gitlab-ce-10.0.0-ce.0.el7.x86_64.rpm`

### 修改git配置文件
`vim /etc/gitlab/gitlab.rb`

```
external_url 'http://10.7.11.212:9091'
nginx['listen_port'] = 9091
unicorn['worker_processes'] = 2
```

### 重启gitlab

`gitlab-ctl reconfigure && gitlab-ctl start`

***
## gitlab与gerrit对接
### gerrit replication 插件启用
如果第一次安装gerrit没有安装插件，再次执行gerrit的安装文件，一直回车，到最后几步是询问是否安装插件。这次确认安装安装就可以。安装成功后在`/path/to/review_site/plugins`中会有相关的jar包。同时在gerrit的界面中也可以查看，在`Plugins->Installed`中可以看到。
### 创建项目
1.gitlab创建test项目，在gerrit创建同名的test项目。

2.在gerrit中`/path/to/review_site/git`删除test.git文件夹。

3.重新从gitlab克隆项目。`git clone --bare your_prject_http` 注意：此路径选择采用ssh连接的git路径，不要使用http的路径。选择错误可能会导致replication插件同步失效。

### gerrit配置文件添加
`vim /path/to/review_site/etc/gerrit.config`
```
[plugins]
        allowRemoteAdmin = true
```

### 添加ssh-key
将gerrit机器的is_rsa.pub添加到gitlab管理员账户中

### gerrit 插件 replication 配置
`vim /path/to/review_site/etc/replication.config`

```
[remote "10.180.207.90"] //gitlab地址
projects = test //项目名称
url = git@10.180.207.90:dev-group/test.git //此处还可以配置其他，可能对提交方式有影响，不明确
push = +refs/heads/*:refs/heads/*
push = +refs/tags/*:refs/tags/*
push = +refs/changes/*:refs/changes/*
threads = 3
```
如果有新的项目添加，继续在此文件添加相应的项目即可

### gerrit 与 gitlab互信

在两个机器的`/root/.ssh/authorized_keys`添加两个机器的公钥。公钥位于`/root/.ssh/id_rsa.pub`中。此时需要先ssh互相登录一下。（不登陆可能导致replication不能触发）

修改gerrit的机器上`/root/.ssh/config`文件配置如下：

```
Host 10.180.207.90 //gitlab地址
  User root //git用户
  IdentityFile ~/.ssh/id_rsa
  PreferredAuthentications publickey
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```
### 提交方式修改
```
git push -u origin HEAD:refs/for/master
git push 远程地址 本地分支:refs/for/远程分支
```
如果在提交的时候报错如下：
```
remote: Processing changes: refs: 1, done
remote: ERROR: [b77c8f6] missing Change-Id in commit message footer
remote:
remote: Hint: To automatically insert Change-Id, install the hook:
remote:   gitdir=$(git rev-parse --git-dir); scp -p -P 29418 limk@10.7.11.212:hooks/commit-msg ${gitdir}/hooks/
remote: And then amend the commit:
remote:   git commit --amend
remote:
To http://10.7.11.212:8080/ios
 ! [remote rejected] HEAD -> refs/for/master ([b77c8f6] missing Change-Id in commit message footer)
error: failed to push some refs to 'http://10.7.11.212:8080/ios'
```
可在gerrit界面设置找到相应的项目，在`Projects->General->Project options->Require Change-Id in commit message`改为false即可。
### 参考文档
https://www.cnblogs.com/kevingrace/p/5651447.html
