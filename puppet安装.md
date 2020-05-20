### puppet 安装
```
sudo su -
wget https://git.openstack.org/cgit/openstack-infra/system-config/plain/install_puppet.sh
bash install_puppet.sh
exit
```
***
### puppet module安装
```
sudo su -
git clone https://git.openstack.org/openstack-infra/system-config
cd system-config
./install_modules.sh
exit
```
***
### 安装single node ci server
#### 创建git 记录改动历史
```
cd /etc/puppet
git init
echo "modules/" >> .gitignore
git add .
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git commit -m "initial files"
```
#### 拷贝文件
```
cp /etc/puppet/modules/openstackci/contrib/hiera.yaml /etc/puppet
mkdir manifests
cp /etc/puppet/modules/openstackci/contrib/single_node_ci_site.pp /etc/puppet/manifests/site.pp
mkdir environments
cp /etc/puppet/modules/openstackci/contrib/single_node_ci_data.yaml /etc/puppet/environments/common.yaml
```
#### 配置文件
修改/etc/puppet/environments/common.yaml
#### 部署前
在/etc/hosts添加
```
127.0.0.1 localhost jenkins
```
#### 部署
```
sudo puppet apply --verbose /etc/puppet/manifests/site.pp
```
***
### 安装log server
#### 创建git 记录改动历史
```
cd /etc/puppet
git init
echo "modules/" >> .gitignore
git add .
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
git commit -m "initial files"
```
#### 拷贝文件
```
cp /etc/puppet/modules/openstackci/contrib/hiera.yaml /etc/puppet
mkdir manifests
cp /etc/puppet/modules/openstackci/contrib/log_server_site.pp /etc/puppet/manifests/site.pp
mkdir environments
cp /etc/puppet/modules/openstackci/contrib/log_server_data.yaml /etc/puppet/environments/common.yaml
```
#### 配置文件
修改/etc/puppet/environments/common.yaml 
```
# See parameter documetation inside ../manifests/single_node_ci.pp
# Fields commented out have reasonable default values
domain: your-domain.example.com
jenkins_ssh_public_key: your-jenkins-public-key-no-whitespace
ara_middleware: false
#swift_authurl:
#swift_user:
#swift_key:
#swift_tenant_name:
#swift_region_name:
#swift_default_container:
```
***
### 安装中出现的问题
1 报错如下
```
Error: Puppet::Parser::AST::Resource failed with error ArgumentError: Could not find declared class ::jenkins::master at /etc/puppet/modules/openstackci/manifests/jenkins_master.pp:43 on node yuyan211
```
没有安装jenkins模块
```
puppet module install puppet-jenkins
```
或者
```
puppet module install puppet-jenkins --ignore-dependencies
```
2 报错如下
```
Error: Syntax error at 'String'; expected ')' at /etc/puppet/modules/jenkins/manifests/init.pp:294 on node yuyan211
```
### 参考文档

https://docs.openstack.org/infra/openstackci/

