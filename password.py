# coding=utf-8
import os
import sys

###
# 使用方式
# 1. 创建批量账号
#    a. 创建name列表，例如group_A=["zhangsan","lisi"]
#    b. 将group_A添加到all_group中
#    c. 执行如下命令：python password.py
# 2. 修改存在账号的密码或者创建单个账号
#    执行如下命令：python password.py modify name password（name为账号名字，password为新的密码）或者 python password.py create name password
# 3. 清除存在账号
#    执行如下命令：python password.py delete name （name为账号名字）
###
GERRIT_PATH = "/usr/local/gerrit/gerrit.password"
PASSWORD = "qwerty123456"
group_A = ["wangzhen02", "zhengyuhui", "zhaorenming", "wangjiyu",
           "xingliangzh", "wangwenxiao01"]
group_B = ["sunliaodong", "zhangshubo", "caowenkang", "chenlihua01"
           , "liuxuewen" ]
group_C = ["sunliangchen", "jiguiyang","yuanlijie","xuruqing01","liuhuixing"]
group_D = ["fangty", "zhang.hao02","lubing","limeiying","lishigang01"]
group_E = ["wangkaibj", "yangzhiguang","zhaoxiaoyao","liuyiliang","houxiaoyu01"]
group_F = ["wangdekui", "linxinyu", "wangb.in"]
group_G = ["chaowang", "zhangyuyan"]
group_H = ["chenpei01"]
all_group = [group_A, group_B, group_C, group_D, group_E, group_F, group_G]
if len(sys.argv) < 2:
    for group in all_group:
        for name in group:
            # os.popen("htpasswd -b /gerrit.password {name} {password}".format(name,password=name))
            os.popen("htpasswd -b {gerrit_path} {name} {password}".format(
                gerrit_path=GERRIT_PATH, name=name, password=PASSWORD))
    sys.exit()
if len(sys.argv) == 4 and sys.argv[1] == "modify" or sys.argv[1] == "create":
    os.popen("htpasswd -b {gerrit_path} {name} {password}".format(
        gerrit_path=GERRIT_PATH, name=sys.argv[2], password=sys.argv[3]))
    sys.exit()
if len(sys.argv) == 3 and sys.argv[1] == "delete":
    os.popen("htpasswd -D {gerrit_path} {name} ".format(gerrit_path=GERRIT_PATH,
                                                     name=sys.argv[2]))
    sys.exit()

print("parameter error ")
sys.exit()
