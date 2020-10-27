import os
from git.repo import Repo

dir_ = r'''C:\Users\Administrator\Desktop\test'''
# repo = git.Repo.init(path=dir_)

### 检出代码
try:
    Repo.clone_from('https://gitee.com/community-operation-group/daily-study.git', to_path=dir_, branch='dev')
except Exception as e:
    print(e)
    print("已经存在")

### 拉代码
repo = Repo(dir_)
repo.git.pull()

## 打包
settings_path = r"F:\\mvn-res\\settings-bilin.xml"
os.chdir(dir_ + "/study/study-service")
print('mvn -s "' + settings_path + '" clean package -Dmaven.test.skip=true')
os.system('mvn -s "' + settings_path + '" clean package -Dmaven.test.skip=true')
