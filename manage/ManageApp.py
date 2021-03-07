#-*-encoding=utf-8-*-
#对照yaml生成模型，并生成模型对应的crud的前台和后台
import os
import argparse
import sys
import logging
import settings
import yaml
import jinja2
import shutil

# description参数可以用于插入描述脚本用途的信息，可以为空
argparser = argparse.ArgumentParser(description='parse yaml to django model, and generate front and backend')
# 添加--conf标签，标签别名可以为-c，help参数用于描述--conf参数的用途或意义。
argparser.add_argument( '-c', '--conf', help='path to configuration file', dest='confValue')

args = argparser.parse_args()

confDict = None;
with open(args.confValue) as f:
    confDict = yaml.safe_load(f)

logging.info("configuration read successfully")
#生成模型

def addApp(appPara):
    #新建app名字的DIR
    appPath = os.path.join("..", appPara["ModelName"]);
    if os.path.exists(appPath):
        logging.error("app exists")
        overide = input("app exists overide?[Y/n]")
        if overide == "n":
            logging.info("abort creating app")
            return;
        else:
            shutil.rmtree(appPath);
    shutil.copytree("ModelTemplate", appPath)
    #修改DIR下面需要修改的文件内容
    jinjaFile = jinja2.FileSystemLoader(os.path.join("..", appPara["ModelName"]))
    jinjaEnv = jinja2.environment.Environment(loader=jinjaFile)
    messageJinja = jinjaEnv.get_template("apps.py")
    with open(os.path.join("..", appPara["ModelName"], "apps.py"), "w") as f:
        f.write(messageJinja.render(appPara))
    
    models = jinjaEnv.get_template("models.py")
    modelPara = {};
    for collumn in appPara["Collumns"]:
        if collumn["Type"] == "String":
            modelPara[collumn["Name"]] = "models.CharField(max_length=20, default='{defaultValue}')".format(defaultValue=collumn["DefaultVaule"])
        elif collumn["Type"] == "Select":
            modelPara[collumn["Name"]] = "models.CharField(blank=True, choices={selectType}.choices, max_length=10, default='{defaultValue}')".format(
                selectType = "models.TextChoices({choices})".format(choices = ",".join([ "'{item}'".format(item=item) for item in collumn["Values"]])),
                defaultValue = collumn["DefaultValue"]
            )
    modelpara1 = {}
    modelpara1["collumns"] = modelPara
    modelpara1["ModelName"] = appPara["ModelName"];
    modelPara = modelpara1
    with open(os.path.join("..", appPara["ModelName"], "models.py"), "w") as f:
        f.write(models.render(modelPara))
    
    #给主程序增加内容
    settingLines = [];
    with open(os.path.join("..", "revolution", "settings.py")) as f:
        settingLines = f.readlines();
    with open(os.path.join("..", "revolution", "settings.py"), "w") as f:
        for line in settingLines:
            if line.startswith("##APPADD_POINT_START"):
                f.write(line);
                f.write("'{appName}'\n".format(appName=appPara["ModelName"]))
            else:
                f.write(line);

addApp(confDict)