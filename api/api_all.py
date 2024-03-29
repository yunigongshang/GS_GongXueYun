import calendar
import json
import logging
import random
import time
from functools import wraps
import requests

from SimpleError.error import SimpleError
from createSign.sign import create_sign
from decry.encrypt import aes_encrypt
from textHandle.count import count_day

logging.basicConfig(format="[%(asctime)s] %(name)s %(levelname)s: %(message)s", level=logging.INFO,
                    datefmt="%Y-%m-%d %I:%M:%S")
api_module_log = logging.getLogger("api_module")
headers = {
    'Host': 'api.moguding.net:9000',
    'accept-language': 'zh-CN,zh;q=0.8',
    'user-agent': 'Mozilla/5.0 (Linux; U; Android 9; zh-cn; SM-G977N Build/LMY48Z) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
    'authorization': "",
    'rolekey': "",
    'content-type': 'application/json; charset=UTF-8',
    'content-length': '161',
    'accept-encoding': 'gzip',
    'cache-control': 'no-cache'
}
basic_url = "https://api.moguding.net:9000/"

def save_token(user_login_info):
    user_login_info.to_save_local(user_login_info.__dict__)

def get_token_userid(user_info):
    url = 'session/user/v3/login'
    data = {"password": aes_encrypt(user_info.password), "loginType": "android",
            "t": aes_encrypt(int(time.time() * 1000)), "uuid": "", "phone": aes_encrypt(user_info.phone)}
    try:
        rsp = requests.post(headers=headers, url=basic_url + url, data=json.dumps(data)).json()
    except Exception as f:
        api_module_log.error(f)
        raise SimpleError("大概率ip被拉黑了(deny),当前环境可能存在问题(处于服务器上或开了代理,非国内代理)")
    data = rsp['data']
    user_info.token = data["token"]
    user_info.user_id = data['userId']

def get_plan(user_login_info) -> None:
    url = 'practice/plan/v3/getPlanByStu'
    data = {"state": ''}
    headers['sign'] = create_sign(user_login_info.user_id, 'student')
    headers['authorization'] = user_login_info.token
    rsp = requests.post(url=basic_url + url, headers=headers, data=json.dumps(data)).json()
    plan_id = rsp["data"][0]['planId']
    user_login_info.plan_id = plan_id

def clock_in(user_login_info) -> None:
    url = 'attendence/clock/v2/save'
    now = time.strftime('%H', time.localtime())
    upload_type = "START"
    type_chin="上班"
    if int(now) >= 12:
        upload_type="END"
        type_chin="下班"
    api_module_log.info("开始打卡")
    data = {"device": "Android",
            "address": user_login_info.address,
            "t": aes_encrypt(int(time.time() * 1000)),
            "description": "",
            "country": "中国",
            "longitude": user_login_info.longitude,
            "city": user_login_info.city,
            "latitude": user_login_info.latitude,
            "planId": user_login_info.plan_id,
            "province": user_login_info.province,
            "type": upload_type}
    headers['sign'] = create_sign("Android", upload_type, user_login_info.plan_id, user_login_info.user_id,
                                  user_login_info.address)
    headers['authorization'] = user_login_info.token
    rsp = requests.post(url=basic_url + url, headers=headers, data=json.dumps(data)).json()
    return type_chin

def submit_log(user_login_info) -> dict:
    url = 'statistics/stu/practice/v1/find'
    data = {"t": aes_encrypt(int(time.time() * 1000)), "planId": user_login_info.plan_id}
    headers['authorization'] = user_login_info.token
    rsp = requests.post(basic_url + url, headers=headers, data=json.dumps(data)).json()
    return rsp['data']

def get_weeks_date(user_login_info) -> dict:
    url = 'practice/paper/v1/getWeeks1'
    data = {'planId': user_login_info.plan_id}
    headers['sign'] = ''
    headers['authorization'] = user_login_info.token
    rsp = requests.post(basic_url + url, headers=headers, data=json.dumps(data)).json()
    return rsp

def submit_weekly(user_login_info, week, weekly):
    url = "practice/paper/v2/save"
    data = {"yearmonth": "", "address": "", "title": "周报", "longitude": "0.0", "latitude": "0.0",
            "weeks": f"第{week['weeks']}周",
            "endTime": week["endTime"], "startTime": week["startTime"],
            "planId": user_login_info.plan_id, "reportType": "week", "content": weekly, "attachments": "",
            }
    headers['authorization'] = user_login_info.token
    headers['sign'] = create_sign(user_login_info.user_id, "week", user_login_info.plan_id, '周报')
    rsp = requests.post(basic_url + url, headers=headers, data=json.dumps(data)).json()
    if rsp['msg'] == "此时间段已经写过周记":
        return False

def submit_daily(user_login_info, daily, day):
    url = 'practice/paper/v2/save'
    title = f"第{day}天日报"
    daily_text=daily.get_daily()['data']
    headers['sign'] = create_sign(user_login_info.user_id, "day", user_login_info.plan_id, title)
    headers['authorization'] = user_login_info.token
    data = {"yearmonth": "", "address": "", "t": aes_encrypt(int(time.time() * 1000)), "title": title,
            "longitude": "0.0",
            "latitude": "0.0", "planId": user_login_info.plan_id, "reportType": "day",
            "content": daily_text}
    rsp = requests.post(basic_url + url, headers=headers, data=json.dumps(data)).json()
    if rsp['msg'] == "今天已经写过日报":
        return False
    return daily_text

def submit_month_Inquire(user_login_info):
    url = 'practice/paper/v2/listByStu'
    headers['sign'] = create_sign(user_login_info.user_id,"student","month")
    headers['authorization'] = user_login_info.token
    data={
        "currPage": 1,
        "pageSize": 25,
        "planId": user_login_info.plan_id,
        "reportType": "month",
        "t": aes_encrypt(int(time.time() * 1000))
    }
    rsp = requests.post(basic_url + url, headers=headers, data=json.dumps(data)).json()
    if rsp["flag"]!=0:
        mou=rsp["data"][0]["yearmonth"]
        if mou in "-" or mou!=None:
            mou_dat=mou[mou.find('-') + 1:mou.find('-') + 2]
        return mou_dat
    else:
        return False

def submit_month_report(user_login_info, date, month_report):
    url = 'practice/paper/v2/save'
    title = f"{date.tm_mon}月的月报"
    data = {"yearmonth": f"{date.tm_year}-{date.tm_mon}", "address": "", "t": aes_encrypt(int(time.time() * 1000)),
            "title": title,
            "longitude": "0.0", "latitude": "0.0", "planId": user_login_info.plan_id, "reportType": "month",
            "content": month_report}
    headers['authorization'] = user_login_info.token
    headers['sign'] = create_sign(user_login_info.user_id + "month" + user_login_info.plan_id + title)
    rsp = requests.post(basic_url + url, headers=headers, data=json.dumps(data)).json()