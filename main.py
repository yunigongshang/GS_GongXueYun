import json
import logging
import os
import time
import requests
import datetime

from api.api_all import get_token_userid, get_plan, clock_in, get_attendance_log, submit_daily, get_weeks_date, submit_month_Inquire, submit_weekly, submit_log, submit_month_report
from config.info import Info
from textHandle.get_daily import Daily
from textHandle.get_month_report import MonthReport
from textHandle.get_weekly import Weekly
from textHandle.handle_weeks_date import WeeksDate

logging.basicConfig(format="[%(asctime)s] %(name)s %(levelname)s: %(message)s", level=logging.INFO,
                    datefmt="%Y-%m-%d %I:%M:%S")
main_module_log = logging.getLogger("main_module")

path = os.path.dirname(__file__)
patha=os.path.dirname(__file__)+"/user"

def pushMessage(a,title, content, token):
        server_push_url = "https://sctapi.ftqq.com/"+token+".send"
        params = {
            "text": title,
            "desp": content
        }
        res = requests.post(url=server_push_url, data=params)
        if res.status_code == 200:
            print("Server酱推送成功!")
        else:
            print("Server酱推送失败!")

def load_daily_file() -> Daily:
    with open(os.path.join(path, 'textFile/daily.json'), 'r', encoding="UTF-8") as f:
        daily = json.load(f)
    return Daily(daily)

def load_weekly_file() -> Weekly:
    with open(os.path.join(path, 'textFile/weekly.json'), 'r', encoding="UTf-8") as f:
        weekly = json.load(f)
    return Weekly(weekly)

def load_month_report() -> MonthReport:
    with open(os.path.join(path, 'textFile/month_report.json'), 'r', encoding="UTf-8") as f:
        return MonthReport(json.load(f))

def load_login_info(config_file) -> Info:
    with open(os.path.join(patha, config_file), encoding="utf-8") as f:
        user_info = json.load(f)
    return Info(user_info, os.path.join(patha, config_file))


def login(user_login_info: Info) -> None:
    if not user_login_info.token:
        get_token_userid(user_login_info)
        user_login_info.to_save_local(user_login_info.__dict__)
    else:
        main_module_log.info("使用本地token")


# get plan
def plan_id(user_login_info: Info) -> None:
    if not user_login_info.plan_id:
        get_plan(user_login_info)
    else:
        main_module_log.info("使用本地plan id")


def load_weeks_info(data) -> WeeksDate:
    return WeeksDate(data)

def run(user_login_info):
    login(user_login_info)
    plan_id(user_login_info)
    submit_all = submit_log(user_login_info)
    type_chin=clock_in(user_login_info)
    
    if user_login_info.is_repeat_clock_in:
        get_attendance_log(user_login_info)
    daily = load_daily_file()
    subm=submit_daily(user_login_info, daily=daily, day=submit_all['dayReportNum'])
    if subm:
        submit_d=f'日报提交内容为：{subm}'

    else:
        submit_d="今天已提交日报了,不会重复提交"
        main_module_log.error("今天已提交日报了,不会重复提交")
        
    if user_login_info.is_submit_weekly:
        now_week = int(time.strftime("%w", time.localtime()))
        now_week = now_week if now_week != 0 else 7
        if now_week == user_login_info.submit_weekly_time:
            weeks_dict = get_weeks_date(user_login_info)
            weeks_date = load_weeks_info(weeks_dict)
            now_week = weeks_date.get_now_week_date()
            weekly = load_weekly_file()
            weeks = submit_all['weekReportNum']
            now_week['weeks'] = weeks
            weekly_text=weekly.get_now_weekly(weeks)
            wekkly_tpye=submit_weekly(user_login_info, week=now_week, weekly=weekly_text)
            if wekkly_tpye :
                submit_w=f'周报提交内容为：{weekly_text}'
            else:
                submit_w="今天已提交周报"
                main_module_log.error("今天已提交周报了,不会重复提交")
        else:
            submit_w=f'未到提交周报时间，时间为星期{user_login_info.submit_weekly_time}'
            
    Recent_month=submit_month_Inquire(user_login_info)
    if Recent_month==datetime.date.today():
        date = time.localtime()
        day = date.tm_mday
    
        if day == user_login_info.submit_month_report_time:
            month_report = load_month_report()
            submit_month_report(user_login_info, date=date, month_report=month_report.get_month_report())
            submit_m="月报提交成功"
        else:
            submit_m=f'未到提交月报时间,时间为{user_login_info.submit_month_report_time}号'
    else:
        submit_m="本月已提交月报"
        
     #构建推送消息
    if user_login_info.pushKey!="":
        pushMessage(user_login_info.phone,type_chin+"打卡成功！",
                            "用户:"+user_login_info.phone+',工学云'+type_chin+"打卡成功！\n\n"+submit_d+"\n\n"+submit_w+"\n\n"+submit_m,
                            user_login_info.pushKey)
    else:
        main_module_log.info("未配置推送")
        
def main(self,name):
    main_module_log.info("开始")
    last_directory1=os.path.dirname(os.path.realpath(__file__))+"/user"
    f_list = os.listdir(last_directory1)
    for i in f_list:
        if i.endswith('.json'):
            try:
                user_login_info = load_login_info(i)
                run(user_login_info)
                main_module_log.info("----------签到完成---------")
            except Exception as e:
                main_module_log.info(e)
                if user_login_info.pushKey!="":
                    pushMessage(user_login_info.phone,"打卡失败！",
                                f"用户:{user_login_info.phone},工学云打卡失败！\n\n{e}",
                                user_login_info.pushKey)
    main_module_log.info("运行结束")
    
if __name__ == '__main__':
    main("a","b")
  