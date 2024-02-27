
整合了这两个项目，能少干活就少干嘛

https://github.com/github123666/gonxueyun 

https://github.com/XuanRanDev/Auto-GongXueYun-2

---
> 邮箱：gongshang0130@qq.com
>
> 如果此项目侵犯您的合法权益，可通过邮件联系我下架此项目。
>


## 有问题可以issues


## 项目更改

>增加了多用户
>
>适配华为云部署，原来的项目直接部署到华为云有诸多问题
>
>去除了一些程序运行日志，华为云运行日志只能显示2K，不方便我看日志
>
>增加了Server酱推送，可自己更改,pushplus推送加在华为云ip被封
>
>取消了原项目的打卡时间，运行了就打卡

## 云函数部署自动打卡

华为云函数部署，工学云ip在某腾和某里被封，建议使用华为云函数部署

1.上传代码到华为云，函数入口设置为main.main，执行超时时间建议为300秒

2.设置俩个定时器，建议一个设置12点前一个设置12点后

云函数使用教程https://note.youdao.com/s/UHDGuOwj

### 不想自己部署可以+V 
```
lc287045
```

## 声明

**仅供学习交流使用**，项目遵循MIT协议


## 基本使用

>1.clone项目到本地

```
git clone https://github.com/yunigongshang/GS_GongXueYun.git
```

>2.安装依赖

```
pip install -r requirements.txt
```

>3.在user文件夹下配置 .json 文件,文件后缀改为.json,多用户就再创建一个


```angular2html
"phone": "手机号",   \\ 手机号
"password": "密码", \\ 密码
"address": "山东省菏泽市曹县某某街道",
"latitude": "34.830624",   \\ 纬度 
"longitude": "115.545005", \\ 经度
"province": "山东省",
"city": "菏泽市",
"is_repeat_clock_in": false \\ 默认不补签
"is_submit_daily": false, \\ 默认不提交日报
"is_submit_weekly": false,\\ 默认不提交周报
"is_submit_month_report": false,\\ 默认不提交月报
"submit_weekly_time": 1 ,\\ 星期几提交周报
"submit_month_report_time": 15 \\ 每个月的几号提交月报,不要写28,29,30或31！！！
"pushKey":"" \\Server酱推送token，
```

Server酱https://sct.ftqq.com/sendkey

经纬度查询 https://api.map.baidu.com/lbsapi/getpoint/index.html

>4.运行main.py
```
python main.py
```


**说明:**  
对日报和月报说明:月报文件里面只有3篇,日报只有20多篇,请自行补充.且都是采用**随机取的方式提交**.


## **补签说明**：

1. 默认补签前30天的数据(只能补签到前30天的)
2. 默认只补签上班(app默认只支持上班,保存和app统一原则),若学校有要求只需要修改请求的type改END,变成打下班卡
3. 补签时间说明,默认是早上8或9点随机时间,随机秒打卡,若修改则自行修改
