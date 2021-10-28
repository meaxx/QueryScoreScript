# -*- codeing = utf-8 -*-
# @Time : :2021/8/14 22:57
# @Author : meaxx
# @File : main.py
# @Software : PyCharm
# -*— coding: utf-8 -*-
__author__ = 'meaxx'
__date__ = '2021/08/14 七夕节'

import datetime
import io
import os
import requests
import pytesseract
import json
from PIL import Image
from bs4 import BeautifulSoup
from wxpy import *

# 读取配置文件
config = json.load(open("config.json", encoding="utf-8"))


class Logger(object):
    def __init__(self, filename="Default.log", path="./"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        self.terminal = sys.stdout
        self.log = open(os.path.join(path, filename), "a", encoding='utf8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


class Item:
    def __init__(self, tr):
        tds = tr.select('td')
        self.name = tds[3].get_text().replace('（', '(').replace('）', ')')  # 课程名
        self.bz = ""
        cj_text = tds[8].get_text()  # 成绩
        cj_text = cj_text.replace(".0", "")
        if cj_text.isdigit():
            self.cj = float(tds[8].get_text())
        else:
            if cj_text == "优秀":
                self.cj = 90
            elif cj_text == "良好":
                self.cj = 80
            elif cj_text == "中等":
                self.cj = 70
            elif cj_text == "及格":
                self.cj = 60
            else:
                self.cj = 0
            self.bz = "五级制：" + cj_text


def parse_secret_code():
    # 识别验证码
    im = Image.open("ccimg.png")
    im = im.convert("RGBA")  # PIL库函数
    pixs = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            if ((pixs[x, y][0] > 20 or pixs[x, y][1] > 20) and pixs[x, y][2] < 100) or \
                    (pixs[x, y][0] > 100 or pixs[x, y][1] > 100):
                pixs[x, y] = (255, 255, 255, 255)
    rst = pytesseract.image_to_string(im).replace(" ", "")
    return rst[0: 4]


def send_email(name_list, score_list, recipient):
    import smtplib
    from email.mime.text import MIMEText

    msg_from = config["sendEmail"]
    passwd = config["sendPass"]  # 填入发送方邮箱的授权码
    msg_to = recipient  # 收件人邮箱

    subject = "你课程有新的成绩已经上传学分制主页了哦"  # 主题
    content = "温馨提醒：\n\t你有" + str(len(name_list)) + "课门程的成绩已经上传学分制主页了哦：\n"
    for k in range(len(name_list)):
        content += name_list[k] + ":" + str(score_list[k]) + "\n"
    content += "\n\n\t\tmeaxx"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 邮件服务器及端口号
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("向" + recipient + "发送成功，内容：" + content)
    except Exception as e:
        print("发送失败")
    finally:
        s.quit()


if __name__ == '__main__':
    sys.stdout = Logger('querySource.log')
    print('-----' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + '-------')
    # 查询文件中所有人的成绩
    for man in range(len(config["man"])):
        username = config["man"][man]['username']
        password = config["man"][man]['password']
        header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/48.0.2564.116 Safari/537.36'}
        sc_try_count = 0
        se = requests.session()
        se.headers = header
        se.get("http://202.200.112.210")
        print("用户%s尝试识别验证码登录..."%username)
        while True:
            sc_try_count += 1
            ccimg = se.get("http://202.200.112.210/CheckCode.aspx")
            ccfile = open("ccimg.png", "wb")
            ccfile.write(ccimg.content)
            ccfile.close()
            postdata = {
                "__VIEWSTATE": "dDwtNTE2MjI4MTQ7Oz74/gDxTawfZAV831VtlWiI90NFVg==",
                "__VIEWSTATEGENERATOR": "92719903",
                "txtUserName": username,
                "TextBox2": password,
                "txtSecretCode": parse_secret_code(),
                "Button1": ""
            }
            rs = se.post("http://202.200.112.210/default2.aspx?xh=%s" % username, data=postdata)
            if "成绩查询" in rs.text:
                break
        print("登录成功,正在查询成绩")
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/48.0.2564.116 Safari/537.36",
            "Referer": "http://202.200.112.210/xscj_gc.aspx?xh=%s" % username
        }
        postdata = {
            "__VIEWSTATE": "dDwxODI2NTc3MzMwO3Q8cDxsPHhoOz47bDwzMTcwOTIxMDQ3Oz4+O\
            2w8aTwxPjs+O2w8dDw7bDxpPDE+O2k8Mz47aTw1PjtpPDc+O2k8OT47aTwxMT47aTwxMz\
            47aTwxNj47aTwyNj47aTwyNz47aTwyOD47aTwzNT47aTwzNz47aTwzOT47aTw0MT47aTw\
            0NT47PjtsPHQ8cDxwPGw8VGV4dDs+O2w85a2m5Y+377yaMzE3MDkyMTA0Nzs+Pjs+Ozs+\
            O3Q8cDxwPGw8VGV4dDs+O2w85aeT5ZCN77ya5byg5a6H5by6Oz4+Oz47Oz47dDxwPHA8b\
            DxUZXh0Oz47bDzlrabpmaLvvJrorqHnrpfmnLrnp5HlrabkuI7lt6XnqIvlrabpmaI7Pj\
            47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOS4k+S4mu+8mjs+Pjs+Ozs+O3Q8cDxwPGw8VGV\
            4dDs+O2w86L2v5Lu25bel56iLOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzooYzmlL/n\
            j63vvJrova/ku7YxNzI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwMTcwOTIxOz4+O\
            z47Oz47dDx0PHA8cDxsPERhdGFUZXh0RmllbGQ7RGF0YVZhbHVlRmllbGQ7PjtsPFhOO1\
            hOOz4+Oz47dDxpPDM+O0A8XGU7MjAxOC0yMDE5OzIwMTctMjAxODs+O0A8XGU7MjAxOC0\
            yMDE5OzIwMTctMjAxODs+Pjs+Ozs+O3Q8cDw7cDxsPG9uY2xpY2s7PjtsPHdpbmRvdy5w\
            cmludCgpXDs7Pj4+Ozs+O3Q8cDw7cDxsPG9uY2xpY2s7PjtsPHdpbmRvdy5jbG9zZSgpX\
            Ds7Pj4+Ozs+O3Q8cDxwPGw8VmlzaWJsZTs+O2w8bzx0Pjs+Pjs+Ozs+O3Q8QDA8Ozs7Oz\
            s7Ozs7Oz47Oz47dDxAMDw7Ozs7Ozs7Ozs7Pjs7Pjt0PEAwPDs7Ozs7Ozs7Ozs+Ozs+O3Q\
            8O2w8aTwwPjtpPDE+O2k8Mj47aTw0Pjs+O2w8dDw7bDxpPDA+O2k8MT47PjtsPHQ8O2w8\
            aTwwPjtpPDE+Oz47bDx0PEAwPDs7Ozs7Ozs7Ozs+Ozs+O3Q8QDA8Ozs7Ozs7Ozs7Oz47O\
            z47Pj47dDw7bDxpPDA+O2k8MT47PjtsPHQ8QDA8Ozs7Ozs7Ozs7Oz47Oz47dDxAMDw7Oz\
            s7Ozs7Ozs7Pjs7Pjs+Pjs+Pjt0PDtsPGk8MD47PjtsPHQ8O2w8aTwwPjs+O2w8dDxAMDw\
            7Ozs7Ozs7Ozs7Pjs7Pjs+Pjs+Pjt0PDtsPGk8MD47aTwxPjs+O2w8dDw7bDxpPDA+Oz47\
            bDx0PEAwPHA8cDxsPFZpc2libGU7PjtsPG88Zj47Pj47Pjs7Ozs7Ozs7Ozs+Ozs+Oz4+O\
            3Q8O2w8aTwwPjs+O2w8dDxAMDxwPHA8bDxWaXNpYmxlOz47bDxvPGY+Oz4+Oz47Ozs7Oz\
            s7Ozs7Pjs7Pjs+Pjs+Pjt0PDtsPGk8MD47PjtsPHQ8O2w8aTwwPjs+O2w8dDxwPHA8bDx\
            UZXh0Oz47bDxYQVVUOz4+Oz47Oz47Pj47Pj47Pj47dDxAMDw7Ozs7Ozs7Ozs7Pjs7Pjs+\
            Pjs+Pjs+/59vDHvz5idNBQ5w4XC0o4eD2XA=",
            "__VIEWSTATEGENERATOR": "DB0F94E3",
            "ddlXN": "",
            "ddlXQ": "",
            "Button1": ""
        }
        rs = se.post("http://202.200.112.210/xscj_gc.aspx?xh=%s" % username, data=postdata, headers=header)

        soup = BeautifulSoup(rs.text, "html.parser")
        table = soup.select("table")
        items_soup = table[0].select("tr")
        item_list = []
        for i in range(1, len(items_soup)):
            item_list.append(Item(items_soup[i]))

        # 有新课程
        if config["man"][man]['last_num'] != len(item_list):
            send_name_list = []
            send_score_list = []
            config["man"][man]['last_num'] = len(item_list)
            name = []
            conf_name = config["man"][man]['name']
            for i in range(0, len(item_list)):
                name.append(item_list[i].name)
                if item_list[i].name not in conf_name:
                    send_name_list.append(item_list[i].name)
                    send_score_list.append(item_list[i].cj)
            # 发送邮件通知
            send_email(send_name_list, send_score_list, config["man"][man]['email'])
            print("有新成绩，已发送邮件")
            config["man"][man]['name'] = name[:]
            with open("./config.json", 'w', encoding='utf-8') as json_file:
                json.dump(config, json_file, ensure_ascii=False, indent=1)

        print("已完成")
