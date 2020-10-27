# pip install schedule
# pip  install pyyaml
# pip install gitpython
import os
from git.repo import Repo
import yaml
import datetime
import schedule
import time
import requests
import json


class Git:

    def __init__(self):
        pass

    def update(self, root_path, git_url, branch):
        self.clone(root_path, git_url, branch)
        return self.pull(root_path)

    def clone(self, root_path, git_url, branch):
        # print('git clone ' + git_url + ' ' + branch)
        ### 检出代码
        try:
            Repo.clone_from(git_url, to_path=root_path,
                            branch=branch)
        except Exception as e:
            pass
            # print("已经存在,忽略clone")

    def pull(self, root_path):
        print('git pull ' + root_path)
        repo = Repo(root_path)
        ret = repo.git.pull()
        print(ret)
        if 'Already up to date' in ret:
            return False, ret
        return True, ret


class Maven:

    def __init__(self, ):
        pass

    def package(self, setting_xml, service_path):
        os.chdir(service_path)
        print('mvn -s "' + setting_xml + '" clean package -Dmaven.test.skip=true')
        result = os.popen('mvn -s "' + setting_xml + '" clean package -Dmaven.test.skip=true')
        res = result.read()
        ret = False
        content = ""
        for line in res.splitlines():
            if 'BUILD SUCCESS' in line:
                ret = True
            content = content + line + "\r\n"
        return ret, content


class Cmd:
    def __init__(self):
        pass

    def exec(self, cmdStr):
        result = os.popen(cmdStr)
        content = ""
        res = result.read()
        for line in res.splitlines():
            content = content + line + "\r\n"
        return content


class Alert:
    def __init__(self):
        self.hint = '''
        {
            "msgtype":"markdown",
            "markdown":{
                "title":"a",
                "text":"%s"
            }
        }
        '''

    def alert(self, webwork, content):
        headers = {
            'Content-Type': 'application/json'
        }
        send = {
            "msgtype": "markdown",
            "markdown": {
                "title": "uc",
                "text": "<font color='#ff0000'>" + content + "</font>"
            }
        }
        requests.post(webwork, data=json.dumps(send), headers=headers)


# 加载 yml ,返回字典类型
def readYml(yamlPath):
    f = open(yamlPath, 'r', encoding='utf-8')
    return yaml.load(f.read(), Loader=yaml.FullLoader)


last_update = 1603267052.2131498
yml = readYml('deploy.yml')
project_path = yml['src']
# project_path = os.path.abspath(os.path.dirname(__file__))
git = Git()
maven = Maven()
alert = Alert()
service_path = project_path + "/" + yml['service']
cmd = Cmd()


def func2():
    now = datetime.datetime.now()
    str_time = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " + str(now.hour) + ":" + str(
        now.minute) + ":" + str(now.second)
    print(str_time + "    ----执行jenkins任务----")
    # 拉代码
    isUpdate, ret = git.update(project_path, yml['git'], yml['git-branch'])
    if not isUpdate:
        return
    alert.alert(yml['webwork'], "【代码更新成功】" + ret)
    print("远端文件有修改,开始执行构建")
    service = project_path + "/" + yml['service']
    ret, content = maven.package(yml['settings'], service)
    if not ret:
        print(content)
        alert.alert(yml['webwork'], "【自动化构建失败】" + content)
        return
    ## 查看jar
    jar_name = yml['service'][yml['service'].rindex('/') + 1:]
    jar_full_path = service + '/target/' + jar_name + ".jar"
    ##构建成功 ,  启动jar 包
    os.system('pkill -f ' + jar_name)
    ## 启动jar
    print(r"开始启动 ：" + jar_full_path)
    ret = cmd.exec(
        "java -jar -Xms128m -Xmx256m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=128m  -DNACOS_CONFIG_ADDR=http://172.21.16.184:8848 " + jar_name + ".jar" + " &")
    print(ret)
    alert.alert(yml['webwork'], "【自动化构建启动" + jar_name + "】" + ret)


# 创建一个按2秒间隔执行任务
schedule.every(15).seconds.do(func2)
# 构建代码
# maven.package(yml['settings'], project_path + "/" + yml['service'])
while True:
    schedule.run_pending()
    time.sleep(1)
