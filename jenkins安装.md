### Jenkins安装
`java -jar jenkins.war --httpPort=9090`

```
Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

8b96a8e98758481892a366df946cbda7

This may also be found at: /root/.jenkins/secrets/initialAdminPassword
```

***
### Jenkins安装插件
1. Gerrit Trigger
2. Git Plugin
Gerrit Code Review <root@RD212>
### 参考文档
https://www.cnblogs.com/kevingrace/p/5651427.html
https://www.cnblogs.com/kevingrace/p/5651447.html


***
### 添加Label Verified
1. 下载All-Projects，并在git配置管理员的账号和注册邮箱
```
git clone ssh://admin@10.7.11.212:29418/All-Projects
cd All-Projects/
git checkout -b refs/meta/config
git config  --global user.email "2115935168@qq.com" //管理员邮箱
git config  --global user.name "admin" //管理员账号
```

2. 编辑project.config文件
`vim project.config `
```
[label "Verified"]
       function = MaxWithBlock
       value = -1 Fails
       value =  0 No score
       value = +1 Verified
```

3. 提交
```
git commit -a -m 'Updated permissions'
git push origin HEAD:refs/meta/config
```