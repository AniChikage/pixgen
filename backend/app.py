# -*- coding: utf-8 -*-
import os
import io
import json
import hashlib
import logging
import random
import time
import queue
import string
import requests
import subprocess
import multiprocessing
from pathlib import Path
from datetime import datetime, timedelta

import sqlite3
from flask_socketio import SocketIO
from flask_cors import CORS
from flasgger import Swagger
from flask import Flask,request,send_file,cli, make_response,send_from_directory,jsonify
from PIL import Image, ImageOps, PngImagePlugin

import smtplib
from email.mime.text import MIMEText
from email.header import Header

"""
MODEL
"""
from plugins.remove_bg import RemoveBG
from plugins.realesrgan import RealESRGANUpscaler
from plugins.remove_object import RemoveObject
from plugins.blur_background import BlurBackground
from plugins.face_swap import FaceSwap

"""
wechat login
"""
from helper.wx import WXObject 

# mysql
from helper.mysql import MySQLConnector

import config as CONFIG
from utils import (
     resize_mask,
     enrich_mask,
     upload_file, 
     download_image,
     generate_token, 
     filter_wx_code,
     down_image_size,
     get_email_from_token, 
     read_image_from_url,
     generate_random_string, 
     generate_validation_code,
     get_validation_code_from_email
)

NUM_THREADS = str(multiprocessing.cpu_count())
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
os.environ["OMP_NUM_THREADS"] = NUM_THREADS
os.environ["OPENBLAS_NUM_THREADS"] = NUM_THREADS
os.environ["MKL_NUM_THREADS"] = NUM_THREADS
os.environ["VECLIB_MAXIMUM_THREADS"] = NUM_THREADS
os.environ["NUMEXPR_NUM_THREADS"] = NUM_THREADS

app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "PIXGEN API DOCUMENT",
    "uiversion": 3,
    "info": {
        "title": "PIXGEN API DOCUMENT",
        "version": "1.0",
        "description": "PIXGEN相关API使用说明 \n * 2023-12-29: 增加换脸功能 \n * 2023-12-26: token放入header",
    },
    "tags": [
        {"name": "User", "description": "用户"},
        {"name": "Plugin", "description": "功能"},
        {"name": "Order", "description": "订单"},
    ],
}
# CORS(app)
cors = CORS(app, origins="*")
swagger = Swagger(app)

# logging.basicConfig(filename='app.log',
#                     level=logging.INFO, 
#                     format="%(asctime)s %(levelname)s %(message)s", 
#                     filemode="a",)
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s %(levelname)s %(message)s", 
                    filemode="a",)
logger = logging.getLogger(__name__)


# alipay related
import traceback

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.FileItem import FileItem
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradePayModel import AlipayTradePayModel
from alipay.aop.api.domain.GoodsDetail import GoodsDetail
from alipay.aop.api.domain.SettleDetailInfo import SettleDetailInfo
from alipay.aop.api.domain.SettleInfo import SettleInfo
from alipay.aop.api.domain.SubMerchant import SubMerchant
from alipay.aop.api.request.AlipayOfflineMaterialImageUploadRequest import AlipayOfflineMaterialImageUploadRequest
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradePayRequest import AlipayTradePayRequest
from alipay.aop.api.response.AlipayOfflineMaterialImageUploadResponse import AlipayOfflineMaterialImageUploadResponse
from alipay.aop.api.response.AlipayTradePayResponse import AlipayTradePayResponse
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.constant.ParamConstants import *
from alipay.aop.api.domain.AlipayEbppInvoiceTitleListGetModel import AlipayEbppInvoiceTitleListGetModel
from alipay.aop.api.request.AlipayEbppInvoiceTitleListGetRequest import AlipayEbppInvoiceTitleListGetRequest
from alipay.aop.api.response.AlipayEbppInvoiceTitleListGetResponse import AlipayEbppInvoiceTitleListGetResponse

from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest

alipay_client_config = AlipayClientConfig()
alipay_client_config.server_url = "https://openapi.alipay.com/gateway.do"
alipay_client_config.app_id = os.environ.get("APPID")
alipay_client_config.app_private_key = os.environ.get("APP_PRIVATE_KEY")
alipay_client_config.alipay_public_key = os.environ.get("ALIPAY_PUBLIC_KEY")

client = DefaultAlipayClient(alipay_client_config=alipay_client_config, logger=logger)

import warnings

warnings.filterwarnings("ignore")

# global
global_queue = queue.Queue()


"""
USER
"""
@app.route("/api/user/register_user", methods=["POST"])
def register_user():
    """
    用户注册

    ---
    tags:
      - User
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: 邮箱地址
      - name: username
        in: formData
        type: string
        required: true
        description: 用户名
      - name: password
        in: formData
        type: string
        required: true
        description: 密码
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1", "-2", "-3"]
              description: 1 => 成功; -1 => 失败; -2 => 验证码过期; -3 => 验证码不正确
            msg:
              type: string
              enum: ["注册成功", "该邮件已经注册", "验证码不正确", "验证码过期"]
              description: 提示信息. status==1 => "注册成功"; status==-1 => "该邮件已经注册"; status==-2 => "验证码过期"; status==-3 => "验证码不正确"
            token:
              type: string
              description: status==1 => 一个24位的字符串; status==-1/-2 => 空字符串
    """
    email = request.form["email"]
    username = request.form["username"]
    password = request.form["password"]
    # validation_code = request.form["validation_code"]
    logging.info(f"{email} registering...")


    # stored_validation_code = get_validation_code_from_email(email)
    # if stored_validation_code is None:
    #     return jsonify({"status": "-2", "msg": "验证码过期", "token": ""})
    # if stored_validation_code != validation_code:
    #     return jsonify({"status": "-3", "msg": "验证码不正确", "token": ""})

    mysql_connector = MySQLConnector()
    mysql_connector.connect()

    # check if user is registered
    query = f"SELECT COUNT(*) FROM user WHERE email = '{email}'"
    result = mysql_connector.execute_query(query)
    logging.info(f"registering ... {query}")
    logging.info(f"registering ... {result}")
    logging.info(f"registering ... {result[0]}")
    logging.info(f"registering ... {result[0][0]}")
    if result[0][0] != 0:
        return jsonify({"status": "-1", "msg": "该邮件已经注册", "token": ""})
    
    created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = f"INSERT INTO user (email, username, password, created_timestamp, \
                     effective_timestamp, effective_counts) VALUES \
                   ('{email}', '{username}', '{password}', '{created_time}', '{created_time}', 0)"
    result = mysql_connector.execute_query(query)
    mysql_connector.disconnect()

    token = generate_token(email)

    return jsonify({"status": "1", "msg": "注册成功", "token": token})


@app.route("/api/user/get_validation_code", methods=["POST"])
def get_validation_code():
    """
    获取邮箱验证码

    ---
    tags:
      - User
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: 邮箱地址
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1"]
              description: 1 => 成功; -1 => 失败
            msg:
              type: string
              enum: ["发送邮件成功", "发送邮件失败"]
              description: 提示信息. status==1 => "发送邮件成功"; status==-1 => "发送邮件失败"
    """
    email = request.form["email"]

    mail_host = "smtp.163.com" 
    mail_user = os.environ.get("SENDER_MAIL")
    mail_pass = os.environ.get("MAIL_PASS")
    
    sender = mail_user
    receivers = [email] 
    
    validation_code = generate_validation_code(email)
    message = MIMEText(f"验证码是: {validation_code}, 有效期5分钟。(如果不是您的请求，请忽略)", "plain", "utf-8")   
    message["From"] = mail_user
    message["To"] = email     
    
    subject = "PIXGEN验证码"
    message["Subject"] = Header(subject, "utf-8")
    
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25) 
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        logging.info("邮件发送成功")
    except smtplib.SMTPException:
        logging.info("Error: 无法发送邮件")
        return jsonify({"status": "-1", "msg": "发送邮件失败"})

    return jsonify({"status": "1", "msg": "发送邮件成功"})


@app.route("/api/user/forgetpassword", methods=["POST"])
def forget_password():
    """
    获取邮箱验证码

    ---
    tags:
      - User
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: 邮箱地址
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1"]
              description: 1 => 成功; -1 => 失败
            msg:
              type: string
              enum: ["发送邮件成功", "发送邮件失败"]
              description: 提示信息. status==1 => "发送邮件成功"; status==-1 => "发送邮件失败"
    """
    email = request.form["email"]

    mail_host = "smtp.163.com" 
    mail_user = os.environ.get("SENDER_MAIL")
    mail_pass = os.environ.get("MAIL_PASS")
    
    sender = mail_user
    receivers = [email] 
    
    validation_code = generate_validation_code(email)

    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT password FROM user WHERE email = '{email}'"
    result = mysql_connector.execute_query(query)
    if not result:
        return jsonify({"status": "-1", "msg": "邮箱不存在"})
    mysql_connector.disconnect()

    password = result[0][0]

    message = MIMEText(f"您的密码是: {password}", "plain", "utf-8")   
    message["From"] = mail_user
    message["To"] = email     
    
    subject = "PIXGEN密码"
    message["Subject"] = Header(subject, "utf-8")
    
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25) 
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        logging.info("邮件发送成功")
    except smtplib.SMTPException:
        logging.info("Error: 无法发送邮件")
        return jsonify({"status": "-1", "msg": "发送邮件失败"})

    return jsonify({"status": "1", "msg": "发送邮件成功"})


@app.route("/api/user/login_user", methods=["POST"])
def login_user():
    """
    用户登录

    ---
    tags:
      - User
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: 邮箱地址
      - name: password
        in: formData
        type: string
        required: true
        description: 密码
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1"]
              description: 1 => 成功; -1 => 失败
            msg:
              type: string
              enum: ["注册成功", "该邮件已经注册"]
              description: 提示信息. status==1 => "登陆成功"; status==-1 => "邮箱或密码错误"
            token:
              type: string
              description: status==1 => 一个24位的字符串; status==-1 => 空字符串
    """
    email = request.form["email"]
    password = request.form["password"]
    logging.info(f"{email} login...")

    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT username FROM user WHERE email = '{email}' and password = '{password}'"
    result = mysql_connector.execute_query(query)
    if not result:
        return jsonify({"status": "-1", "msg": "邮箱或密码错误", "username": "", "token": ""})
    mysql_connector.disconnect()

    username = result[0]
    token = generate_token(email)

    return jsonify({"status": "1", "msg": "登陆成功", "username": username, "token": token})


@app.route("/api/user/wx_login_user", methods=["POST"])
def wx_login_user():
    """
    微信用户登录

    ---
    tags:
      - User
    parameters:
      - name: code
        in: formData
        type: string
        required: true
        description: 请求的code
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1"]
              description: 1 => 成功; -1 => 失败
            msg:
              type: string
              enum: ["登陆成功", "邮箱或密码错误"]
              description: 提示信息. status==1 => "登陆成功"; status==-1 => "邮箱或密码错误"
            token:
              type: string
              description: status==1 => 一个24位的字符串; status==-1 => 空字符串
    """
    try:
      code = request.form["code"]
    except:
      return {"status": "-1", "msg": "缺少参数", "username": "", "token": ""}

    logging.info(f"wx user login...{code}")

    # get wx username
    wxObject = WXObject(code)
    unionid, username = wxObject.getUserInfo()
    logging.info(f"wx user login...unionid: {unionid}")
    if unionid == "":
        return jsonify({"status": "-1", "msg": "unionid is empty", "username": "", "token": ""})

    # check if user registered
    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT username FROM user WHERE email = '{unionid}'"
    result = mysql_connector.execute_query(query)
    if result:
      logging.info("user is already registered")
    else:
      created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      query = f"INSERT INTO user (email, username, password, created_timestamp, \
                      effective_timestamp, effective_counts) VALUES \
                    ('{unionid}', '{username}', '', '{created_time}', '{created_time}', 0)"
      logging.info(f"wx user login...query: {query}")
      mysql_connector.execute_query(query)
    mysql_connector.disconnect()
    
    token = generate_token(unionid)

    return jsonify({"status": "1", "msg": "登陆成功", "username": username, "token": token})


@app.route("/api/user/user_profile", methods=["POST"])
def user_profile():
    """
    获取用户信息

    ---
    tags:
      - User
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Access token (Bearer token)
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1", "-10"]
              description: 1 => 成功; -1 => 失败; -10 => 已过登录有效期
            msg:
              type: string
              enum: ["登录有效期已过，请重新登陆", "获取资料失败", "获取资料成功"]
              description: 提示信息. status==1 => "获取资料成功"; status==-1 => "获取资料失败"; status==-10 => "登录有效期已过，请重新登陆"
            username:
              type: string
              description: 提示信息. status==1 => 用户名; status==-1 => 空字符串; status==-10 => 空字符串
            effective_timestamp:
              type: string
              description: 提示信息. status==1 => 时间字符串, e.g. "2023-01-01 00:00:00"; status==-1 => 空字符串; status==-10 => 空字符串
            effective_counts:
              type: int
              description: 提示信息. status==1 => 次数; status==-1 => -1; status==-10 => -1
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "username": "", "effective_timestamp": "", "effective_counts": -1, "api_token": "暂未购买API token", "api_count": 0})
    email = get_email_from_token(token)
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "username": "", "effective_timestamp": "", "effective_counts": -1, "api_token": "暂未购买API token", "api_count": 0})
    logging.info(f"{email} login...")

    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT username, effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    result = mysql_connector.execute_query(query)
    mysql_connector.disconnect()
    if not result:
        return jsonify({"status": "-1", "msg": "获取资料失败", "username": "", "effective_timestamp": "", "effective_counts": -1, "api_token": "暂未购买API token", "api_count": 0})

    username, effective_timestamp, effective_counts = result[0]

    if effective_timestamp != "-1":
        # logging.info(f"ssssss-: {effective_timestamp}")
        current_time = datetime.now()
        target_time = datetime.strptime(effective_timestamp, '%Y-%m-%d %H:%M:%S')
        logging.info(f"current_time-: {current_time}")
        logging.info(f"target_time-: {target_time}")
        if current_time > target_time:
            effective_timestamp = "-"

    api_token = "暂未购买API token"
    api_counts = 0
    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT token, counts FROM apiusage WHERE email = '{email}'"
    result = mysql_connector.execute_query(query)
    mysql_connector.disconnect()
    if result:
        api_token = result[0][0]
        api_counts = result[0][1]

    return jsonify({"status": "1", "msg": "获取资料成功", "username": username, \
                    "effective_timestamp": effective_timestamp, \
                    "effective_counts": effective_counts, "api_token": api_token, "api_count": api_counts})


def check_user_pro(email):
    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    result = mysql_connector.execute_query(query)
    effective_timestamp, effective_counts = result[0]
    mysql_connector.disconnect()

    if effective_timestamp != "-1":
        current_time = datetime.now()
        target_time = datetime.strptime(effective_timestamp, '%Y-%m-%d %H:%M:%S')
        if current_time <= target_time:
            return {"status": "1", "msg": "有效", "effective": "1"}
        
    if int(effective_counts) > 0:
        return {"status": "1", "msg": "有效", "effective": "1"}

    return {"status": "-1", "msg": "无效", "effective": "0"}
 

@app.route("/api/user/check_pro", methods=["POST"])
def check_pro():
    """
    检查用户是否是付费会员

    ---
    tags:
      - User
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Access token (Bearer token)
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1", "-10"]
              description: 1 => 成功; -1 => 失败; -10 => 已过登录有效期
            msg:
              type: string
              enum: ["登录有效期已过，请重新登陆", "有效", "无效"]
              description: 提示信息. status==1 => "有效"; status==-1 => "无效"; status==-10 => "登录有效期已过，请重新登陆"
            effective:
              type: string
              description: 是否有效. status==1 => "1"; status==-1 => "0"; status==-10 => "0"
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})
    logging.info(f"token:  {token}")
    email = get_email_from_token(token)
    logging.info(f"email:  {email}")
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})
    logging.info(f"{email} checking pro...")
    
    result = check_user_pro(email)
    return jsonify(result)


@app.route("/api/user/update_pro", methods=["POST"])
def update_pro():
    """
    每次下载有效次数减一

    ---
    tags:
      - User
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Access token (Bearer token)
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1", "-10"]
              description: 1 => 成功; -1 => 失败; -10 => 已过登录有效期
            msg:
              type: string
              enum: ["登录有效期已过，请重新登陆", "无剩余次数", "更新完成"]
              description: 提示信息. status==1 => "更新完成"; status==-1 => "无剩余次数"; status==-10 => "登录有效期已过，请重新登陆"
            effective:
              type: string
              description: 是否有效. status==1 => "1"; status==-1 => "0"; status==-10 => "0"
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})
    email = get_email_from_token(token)
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})
    logging.info(f"{email} updating pro...")

    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    result = mysql_connector.execute_query(query)
    _, effective_counts = result[0]

    if int(effective_counts) <= 0:
        return jsonify({"status": "-1", "msg": "无剩余次数", "effective": "0"})

    effective_counts -= 1
    query = f"update user set effective_counts={effective_counts} where email = '{email}'"
    result = mysql_connector.execute_query(query)

    mysql_connector.disconnect()

    return jsonify({"status": "1", "msg": "更新完成", "effective": "1"})


"""
plugins
"""
@app.route("/api/plugin/remove_bg", methods=["POST"])
def remove_bg():
    """
    去除背景

    ---
    tags:
      - Plugin
    parameters:
      - name: Authorization
        in: header
        type: string
        required: false
        description: Access token (Bearer token)
      - name: image
        in: formData
        type: file
        required: true
        description: 图片文件
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["消除背景完成"]
              description: 提示信息. status==1 => "消除背景完成"
            image_high_url:
              type: string
              description: 处理后的原始分辨率图片url. status==1 => url
            image_low_url:
              type: string
              description: 处理后的低分辨率图片url. status==1 => url
    """
    image = request.files["image"]
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = get_email_from_token(token)
    else:
        email = None

    filename = image.filename
    image_pil = Image.open(image)
    image_removed_pil = RemoveBG()(image_pil)
    upload_file(image_pil, filename, processed=False, plugin_name="removebg")
    _, image_high_url, image_low_url = upload_file(image_removed_pil, filename, processed=True, plugin_name="removebg")

    # if email is None:
    #     image_high_url = ""
    # else:
    #     user_pro = check_user_pro(email)
    #     if user_pro["effective"] == "0":
    #         image_high_url = ""

    return jsonify({"status": "1", "msg": "消除背景完成", "image_high_url": image_high_url, "image_low_url": image_low_url})

"""
plugins
"""
@app.route("/api/plugin/blur_bg", methods=["POST"])
def blur_bg():
    """
    模糊背景

    ---
    tags:
      - Plugin
    parameters:
      - name: Authorization
        in: header
        type: string
        required: false
        description: Access token (Bearer token)
      - name: image
        in: formData
        type: file
        required: true
        description: 图片文件
      - name: degree
        in: formData
        type: string
        required: false
        description: 模糊度
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["模糊背景完成"]
              description: 提示信息. status==1 => "模糊背景完成"
            image_high_url:
              type: string
              description: 处理后的原始分辨率图片url. status==1 => url
            image_low_url:
              type: string
              description: 处理后的低分辨率图片url. status==1 => url
    """
    image = request.files["image"]
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = get_email_from_token(token)
    else:
        email = None
    degree = 10
    if "degree" in request.form:
        degree = request.form["degree"]

    filename = image.filename
    image_pil = Image.open(image)
    image_removed_pil = BlurBackground()(image_pil, degree)
    upload_file(image_pil, filename, processed=False, plugin_name="blur")
    _, image_high_url, image_low_url = upload_file(image_removed_pil, filename, processed=True, plugin_name="blur")

    # if email is None:
    #     image_high_url = ""
    # else:
    #     user_pro = check_user_pro(email)
    #     if user_pro["effective"] == "0":
    #         image_high_url = ""

    return jsonify({"status": "1", "msg": "模糊背景完成", "image_high_url": image_high_url, "image_low_url": image_low_url})


@app.route("/api/plugin/upscaler", methods=["POST"])
def upscaler():
    """
    图片放大

    ---
    tags:
      - Plugin
    parameters:
      - name: Authorization
        in: header
        type: string
        required: false
        description: Access token (Bearer token)
      - name: image
        in: formData
        type: file
        required: true
        description: 图片文件
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["图片放大完成"]
              description: 提示信息. status==1 => "图片放大完成"
            image_high_url:
              type: string
              description: 处理后的原始分辨率图片url. status==1 => url
            image_low_url:
              type: string
              description: 处理后的低分辨率图片url. status==1 => url
    """
    image = request.files["image"]
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = get_email_from_token(token)
    else:
        email = None

    logging.info(f"{email}")

    # wating for all requests done
    queue_id = generate_random_string()
    global_queue.put(queue_id)
    while True:
        if not global_queue.empty() and global_queue.queue[0] == queue_id:
            break
        time.sleep(1)

    filename = image.filename
    image_pil = Image.open(image)

    image_pil, down_ratio = down_image_size(image_pil)

    upscaler_object = RealESRGANUpscaler()
    upsampled_pil = upscaler_object.upscale(image_pil)
    upload_file(image_pil, filename, processed=False, plugin_name="upscaler")
    _, image_high_url, image_low_url = upload_file(upsampled_pil, filename, processed=True, plugin_name="upscaler",down_ratio=down_ratio)

    # if email is None:
    #     image_high_url = ""
    # else:
    #     user_pro = check_user_pro(email)
    #     if user_pro["effective"] == "0":
    #         image_high_url = ""

    global_queue.get()
    logging.info(f"finished: upscaler: {queue_id} from the queue.")

    return jsonify({"status": "1", "msg": "放大完成", "image_high_url": image_high_url, "image_low_url": image_low_url})


@app.route("/api/plugin/remove_object", methods=["POST"])
def remove_object():
    """
    消除物体

    ---
    tags:
      - Plugin
    parameters:
      - name: Authorization
        in: header
        type: string
        required: false
        description: Access token (Bearer token)
      - name: image
        in: formData
        type: file
        required: true
        description: 图片文件
      - name: mask
        in: formData
        type: file
        required: true
        description: 遮罩，也是图片文件
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["消除物体完成"]
              description: 提示信息. status==1 => "消除物体完成"
            image_high_url:
              type: string
              description: 处理后的原始分辨率图片url. status==1 => url
            image_low_url:
              type: string
              description: 处理后的低分辨率图片url. status==1 => url
    """
    image = request.files["image"]
    mask = request.files["mask"]
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = get_email_from_token(token)
    else:
        email = None

    logging.info(f"{email}")

    # wating for all requests done
    queue_id = generate_random_string()
    global_queue.put(queue_id)
    while True:
        if not global_queue.empty() and global_queue.queue[0] == queue_id:
            break
        time.sleep(1)

    filename = image.filename
    image_pil = Image.open(image)
    mask_pil = Image.open(mask)

    image_pil = image_pil.convert("RGB")
    mask_pil = resize_mask(image_pil, mask_pil)
    mask_pil = enrich_mask(mask_pil)

    # random_string = generate_random_string()
    # logging.info(f"{random_string}")
    # image_pil.save(f"image_{random_string}.png")
    # mask_pil.save(f"mask_{random_string}.png")

    
    image_file_path = os.path.join(CONFIG.LOCAL_PATH, filename)
    mask_file_path = os.path.join(CONFIG.LOCAL_PATH, f"mask_{filename}")
    tmp_path = os.path.join(CONFIG.LOCAL_PATH, "tmp")
    image_pil.save(image_file_path)
    mask_pil.save(mask_file_path)
    command = [
        'iopaint',
        'run',
        '--model=ldm',
        '--device=cuda',
        f'--model-dir={CONFIG.MODEL_PATH}',
        f'--image={image_file_path}',
        f'--mask={mask_file_path}',
        f'--output={tmp_path}'
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    image_removed_pil = Image.open(os.path.join(tmp_path, filename))
    

    # image_removed_pil = RemoveObject()(image_pil, mask_pil)
    upload_file(image_pil, filename, processed=False, plugin_name="remove_object")
    _, image_high_url, image_low_url = upload_file(image_removed_pil, filename, processed=True, plugin_name="remove_object")

    # if email is None:
    #     image_high_url = ""
    # else:
    #     user_pro = check_user_pro(email)
    #     if user_pro["effective"] == "0":
    #         image_high_url = ""

    global_queue.get()
    logging.info(f"finished: remove object: {queue_id} from the queue.")

    return jsonify({"status": "1", "msg": "消除物体完成", "image_high_url": image_high_url, "image_low_url": image_low_url})


@app.route("/api/plugin/swap_face", methods=["POST"])
def swap_face():
    """
    换脸

    ---
    tags:
      - Plugin
    parameters:
      - name: Authorization
        in: header
        type: string
        required: false
        description: Access token (Bearer token)
      - name: source
        in: formData
        type: file
        required: true
        description: 源人脸图片
      - name: target
        in: formData
        type: file
        required: true
        description: 待被替换人脸图片
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["换脸完成"]
              description: 提示信息. status==1 => "换脸完成"
            image_high_url:
              type: string
              description: 处理后的原始分辨率图片url. status==1 => url
            image_low_url:
              type: string
              description: 处理后的低分辨率图片url. status==1 => url
    """
    source = request.files["source"]
    target = request.files["target"]
    ip = request.form.get('ip')
    if not ip:
        logging.info(f"ip is none")
    else:
        logging.info(f"ip: {ip}") 

    api_token = request.form.get('token')

    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    if ip:
        query = f"select ip from denied where ip='{ip}'"
        result = mysql_connector.execute_query(query)
        logging.info(f"result: {len(result)}") 
        if len(result) == 1:
            return jsonify({"status": "-20", "msg": "ip被禁止", "image_high_url": "", "image_low_url": ""})
  
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        email = get_email_from_token(token)
    else:
        email = None

    logging.info(f"email: {email}")

    filename = source.filename
    filename_target = target.filename
    source_pil = Image.open(source)
    target_pil = Image.open(target)


    # source_pil.save("source.jpg")
    # target_pil.save("target.jpg")
    if source_pil.mode == "RGBA":
        source_pil = source_pil.convert("RGB")
    if target_pil.mode == "RGBA":
        target_pil = target_pil.convert("RGB")
    try:
        swapped_image_pil = FaceSwap()(source_pil, filename, target_pil)
    except:
        return jsonify({"status": "-100", "msg": "源或目标图片未能检测到完整的人脸，请上传新的图片尝试，不会扣除有效次数", "image_high_url": "", "image_low_url": ""})
    upload_file(source_pil, f"faceswap_source_{filename}", processed=False, plugin_name="")
    upload_file(target_pil, f"faceswap_target_{filename_target}", processed=False, plugin_name="")
    _, image_high_url, image_low_url = upload_file(swapped_image_pil, filename, processed=True, plugin_name="face_swapped")

    # if email is None:
    #     image_high_url = ""
    # else:
    #     user_pro = check_user_pro(email)
    #     if user_pro["effective"] == "0":
    #         image_high_url = ""

    return jsonify({"status": "1", "msg": "换脸", "image_high_url": image_high_url, "image_low_url": image_low_url})



@app.route("/api/plugin/faceswap", methods=["POST"])
def swap_face_api():
    """
    换脸

    ---
    tags:
      - Plugin
    parameters:
      - name: source
        in: formData
        type: file
        required: true
        description: 源人脸图片
      - name: target
        in: formData
        type: file
        required: true
        description: 待被替换人脸图片
      - name: token
        in: formData
        type: string
        required: true
        description: token
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["换脸完成"]
              description: 提示信息. status==1 => "换脸完成"
            image_high_url:
              type: string
              description: 处理后的原始分辨率图片url. status==1 => url
            image_low_url:
              type: string
              description: 处理后的低分辨率图片url. status==1 => url
    """
    param_type = request.form.get('type')
    if not param_type:
        return jsonify({"status": "-40", "msg": "参数不完整", "image_high_url": "", "image_low_url": "", "remains": ""})

    api_token = request.form.get('token')
    if not api_token:
        return jsonify({"status": "-30", "msg": "token不存在", "image_high_url": "", "image_low_url": "", "remains": ""})

    if param_type == "url":
        try:
            source = request.form.get("source")
            target = request.form.get("target")
            filename = os.path.basename(source)
            filename_target = os.path.basename(target)
            source_pil = read_image_from_url(source)
            target_pil = read_image_from_url(target)
        except:
            return jsonify({"status": "-50", "msg": "参数错误，请检查参数", "image_high_url": "", "image_low_url": "", "remains": ""})
    elif param_type == "file":
        try:
            source = request.files["source"]
            target = request.files["target"]
            filename = source.filename
            filename_target = target.filename
            source_pil = Image.open(source)
            target_pil = Image.open(target)
        except:
            return jsonify({"status": "-50", "msg": "参数错误，请检查参数", "image_high_url": "", "image_low_url": "", "remains": ""})

    mysql_connector = MySQLConnector()
    mysql_connector.connect()

    # source_pil.save("source.jpg")
    # target_pil.save("target.jpg")
    if source_pil.mode == "RGBA":
        source_pil = source_pil.convert("RGB")
    if target_pil.mode == "RGBA":
        target_pil = target_pil.convert("RGB")
    try:
        swapped_image_pil = FaceSwap()(source_pil, filename, target_pil)
    except:
        return jsonify({"status": "-100", "msg": "源或目标图片未能检测到完整的人脸，请上传新的图片尝试，不会扣除有效次数", "image_high_url": "", "image_low_url": "", "remains": ""})
    upload_file(source_pil, f"faceswap_source_{filename}", processed=False, plugin_name="")
    upload_file(target_pil, f"faceswap_target_{filename_target}", processed=False, plugin_name="")
    _, image_high_url, image_low_url = upload_file(swapped_image_pil, filename, processed=True, plugin_name="face_swapped")

    # if email is None:
    #     image_high_url = ""
    # else:
    #     user_pro = check_user_pro(email)
    #     if user_pro["effective"] == "0":
    #         image_high_url = ""

    logging.info(f"from api")
    mysql_connector = MySQLConnector()
    mysql_connector.connect()

    query = f"SELECT counts FROM apiusage WHERE token = '{api_token}'"
    result = mysql_connector.execute_query(query)
    if len(result) == 0:
        return jsonify({"status": "-20", "msg": "token无效", "image_high_url": "", "image_low_url": "", "remains": ""})
    token_counts = result[0][0]
    logging.info(f"apicounts of {api_token}: {token_counts}")
    
    if int(token_counts) > 0:
        token_counts = int(token_counts)
        token_counts -= 1
        query = f"update apiusage set counts='{token_counts}' WHERE token = '{api_token}'"
        result = mysql_connector.execute_query(query)
        mysql_connector.disconnect()
        return jsonify({"status": "1", "msg": "换脸成功", "image_high_url": image_high_url, "image_low_url": image_low_url, "remains": f"{token_counts}"})
    else:
        return jsonify({"status": "-10", "msg": "token次数用完", "image_high_url": "", "image_low_url": "", "remains": ""})



"""
UTILS
"""
@app.route("/api/utils/upload_image", methods=["POST"])
def upload_image():
    """
    上传图片

    ---
    tags:
      - UTILS
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: 上传的图片
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1", "-1", "-2", "-3"]
              description: 1 => 成功; -1 => 失败; -2 => 验证码过期; -3 => 验证码不正确
            msg:
              type: string
              enum: ["注册成功", "该邮件已经注册", "验证码不正确", "验证码过期"]
              description: 提示信息. status==1 => "注册成功"; status==-1 => "该邮件已经注册"; status==-2 => "验证码过期"; status==-3 => "验证码不正确"
            token:
              type: string
              description: status==1 => 一个24位的字符串; status==-1/-2 => 空字符串
    """
    image = request.files["image"]

    logging.info(image.filename)

    filename = image.filename
    image_pil = Image.open(image)

    remote_origin_image_url, image_high_url, image_low_url = upload_file(image_pil, filename, processed=False, plugin_name="")

    logging.info({"status": "1", "msg": "上传成功", "image_url": remote_origin_image_url})

    return {"status": "1", "msg": "上传成功", "image_url": remote_origin_image_url}




"""
UTILS
"""
@app.route("/api/config/get_hint", methods=["POST"])
def getHint():
    """
    获取banner

    ---
    tags:
      - CONFIG
    """
    
    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = "select show_hint, hint from config"
    result = mysql_connector.execute_query(query)
    # logging.info(result)
    msg_show_hint = result[0][0]
    msg_hint = result[0][1]

    return {"status": "1", "msg": "获取成功", "show_hint": msg_show_hint, "hint": msg_hint}




"""
order
"""
@app.route("/api/order/list_orders", methods=["POST"])
def list_orders():
    """
    获取订单

    ---
    tags:
      - Order
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Access token (Bearer token)
      - name: page
        in: formData
        type: string
        required: true
        description: 页
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["图片放大完成"]
              description: 提示信息. status==1 => "图片放大完成"
            orders:
              type: array
              description: 返回的orders数组
              items:
                type: object
                properties:
                  out_trade_no:
                    type: string
                    description: 订单号
                  total_amount:
                    type: string
                    description: 交易金额
                  trade_no:
                    type: string
                    description: 交易号
                  create_time:
                    type: string
                    description: 支付时间
    """
    try:
        page = request.form["page"]
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            return jsonify({"status": "-1", "msg": "登录有效期已过，请重新登陆", "orders": [], "has_next": "no"})
        email = get_email_from_token(token)
        if email is None:
            return jsonify({"status": "-1", "msg": "登录有效期已过，请重新登陆", "orders": [], "has_next": "no"})
    except:
        return jsonify({"status": "-1", "msg": "请检查参数", "orders": [], "has_next": "no"})

    logging.info(f"{page}")

    page_size = 5
    offset = (int(page) - 1) * page_size

    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"SELECT effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    result = mysql_connector.execute_query(query)

    # get all order number
    query = f"SELECT out_trade_no, trade_no, total_amount, gmt_payment FROM orders WHERE email = '{email}' and trade_status = 'TRADE_SUCCESS'"
    result = mysql_connector.execute_query(query)
    record_num = len(result)
    # get page record
    query = f"SELECT out_trade_no, trade_no, total_amount, gmt_payment FROM orders WHERE email = '{email}' and trade_status = 'TRADE_SUCCESS' order by gmt_payment desc limit {page_size} offset {offset}"
    result = mysql_connector.execute_query(query)

    if not result:
        return  jsonify({"status": "1", "msg": "获取订单成功", "orders": [], "has_next": "no"})

    orders = []
    subscription = {
      "0.01": "试用",
      "0.02": "灵活",
      "0.03": "试用",
      "1.90": "试用",
      "4.90": "灵活",
      "9.90": "月付",
      "14.90": "套餐一",
      "24.90": "套餐二",
      "99.90": "套餐三",
      "149.90": "套餐四"
    }
    for row in result:
        order_item = {}
        out_trade_no, trade_no, total_amount, gmt_payment = row
        order_item["out_trade_no"] = out_trade_no
        order_item["trade_no"] = trade_no
        order_item["total_amount"] = total_amount
        order_item["gmt_payment"] = gmt_payment
        order_item["subscription"] = subscription[total_amount]
        orders.append(order_item)

    mysql_connector.disconnect()

    if int(page) * page_size < record_num:
        return jsonify({"status": "1", "msg": "获取订单成功", "orders": orders, "has_next": "yes"})
    
    return jsonify({"status": "1", "msg": "获取订单成功", "orders": orders, "has_next": "no"})
         


@app.route("/api/order/create_order", methods=["POST"])
def create_order():
    """
    创建订单

    ---
    tags:
      - Order
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Access token (Bearer token)
      - name: amount
        in: formData
        type: string
        required: true
        description: 金额
    responses:
      200:
        description: 响应
        schema:
          type: object
          properties:
            status:
              type: string
              enum: ["1"]
              description: 1 => 成功
            msg:
              type: string
              enum: ["图片放大完成"]
              description: 提示信息. status==1 => "图片放大完成"
            image_high_url:
              type: string
              description: 处理后的原始分辨率图片url. status==1 => url
            image_low_url:
              type: string
              description: 处理后的低分辨率图片url. status==1 => url
    """
    amount = request.form["amount"]
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})
    email = get_email_from_token(token)
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})

    logging.info(f"create order: {email}")

    order_created_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    order_random_string = generate_random_string()

    model = AlipayTradePagePayModel()
    out_trade_no = f"order{order_created_timestamp}{order_random_string}"
    model.out_trade_no = out_trade_no
    model.total_amount = float(amount)
    model.subject = "PIXGEN订阅计划"
    model.body = "PIXGEN订阅计划"
    model.product_code = "FAST_INSTANT_TRADE_PAY"
    # return_url = "https://workwithfun.site"
    orderRequest = AlipayTradePagePayRequest(biz_model=model)
    orderRequest.return_url = "https://pixgen.pro"
    orderRequest.notify_url = f"https://pixgen.pro:{CONFIG.HTTPS_PORT}/api/order/notify_order"
    response = client.page_execute(orderRequest, http_method="GET")
    logging.info("alipay.trade.page.pay response:" + response)

    mysql_connector = MySQLConnector()
    mysql_connector.connect()
    query = f"insert into orders (email, out_trade_no, total_amount, \
                    trade_status, trade_no, gmt_create, gmt_payment, create_time) values \
                    ('{email}', '{out_trade_no}', '', '', '', '', '', '{order_created_timestamp}')"
    logging.info(f"create order [query]: {query}")
    result = mysql_connector.execute_query(query)
    mysql_connector.disconnect()

    return {"status": "1", "msg": "创建成功", "url": response, "out_trade_no": out_trade_no}


@app.route("/api/order/notify_order", methods=["POST"])
def notify_order():
    mysql_connector = MySQLConnector()
    mysql_connector.connect()

    logging.info("notify_order")
    out_trade_no = request.form["out_trade_no"]
    total_amount = request.form["total_amount"]
    trade_status = request.form["trade_status"]
    trade_no = request.form["trade_no"]
    gmt_create = request.form["gmt_create"]
    gmt_payment = request.form["gmt_payment"]

    logging.info(f"out_trade_no: {out_trade_no}")

    mysql_connector = MySQLConnector()
    mysql_connector.connect()

    # get trade status
    query = f"SELECT trade_status FROM orders WHERE out_trade_no = '{out_trade_no}'"
    result = mysql_connector.execute_query(query)
    logging.info(f"get trade status: {result}")
    last_trade_status = result[0][0]
    logging.info(f"trade_status: {last_trade_status}")
    if last_trade_status == "TRADE_SUCCESS":
        return {"notify": "done"}

    # update orders
    query = f"update orders set total_amount='{total_amount}', trade_status='{trade_status}', \
              trade_no='{trade_no}', gmt_create='{gmt_create}', gmt_payment='{gmt_payment}' \
              where out_trade_no='{out_trade_no}'"
    result = mysql_connector.execute_query(query)

    # get user email
    query = f"SELECT email FROM orders WHERE out_trade_no = '{out_trade_no}'"
    logging.info(f"get user email: {query}")
    result = mysql_connector.execute_query(query)
    email = result[0][0]
    logging.info(f"email: {email}")

    # get last effective timestamp
    query = f"SELECT effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    logging.info(f"get last effective timestamp: {query}")
    result = mysql_connector.execute_query(query)
    last_effective_timestamp, last_effective_counts = result[0]
    logging.info(f"last_effective_timestamp: {last_effective_timestamp}, last_effective_counts: {last_effective_counts}")

    # api_count = 0
    # query = f"SELECT counts FROM apiusage WHERE email = '{email}'"
    # result = mysql_connector.execute_query(query)
    # if result:
    #     last_api_counts = result[0]
    #     api_count += last_api_counts
    #     # logging.info(f"last_effective_timestamp: {last_effective_timestamp}, last_effective_counts: {last_effective_counts}")

    if trade_status == "TRADE_SUCCESS":
        prices = CONFIG.PRICE_CONFIG
        subscription = prices[total_amount]
        current_time = datetime.now()
        last_effective_timestamp = datetime.strptime(last_effective_timestamp, '%Y-%m-%d %H:%M:%S')
        last_effective_timestamp = current_time if last_effective_timestamp < current_time else last_effective_timestamp
        
        if subscription == "trial":
            effective_timestamp = last_effective_timestamp + timedelta(days=1)
            effective_timestamp = effective_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            query = f"update user set effective_timestamp='{effective_timestamp}' where email='{email}'"
            result = mysql_connector.execute_query(query)
            logging.info(f"update {email} from {last_effective_timestamp} to {effective_timestamp}")
        elif subscription == "flexible":
            last_effective_counts += 100
            query = f"update user set effective_counts={last_effective_counts} where email='{email}'"
            result = mysql_connector.execute_query(query)
            logging.info(f"update {email} to {last_effective_counts}")
        elif subscription == "plus":
            effective_timestamp = last_effective_timestamp + timedelta(days=30)
            effective_timestamp = effective_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            query = f"update user set effective_timestamp='{effective_timestamp}' where email='{email}'"
            result = mysql_connector.execute_query(query)
            logging.info(f"update {email} from {last_effective_timestamp} to {effective_timestamp}")
        
        package_counts = {
          "package1": 500,
          "package2": 1000,
          "package3": 5000,
          "package4": 10000
        }
        if "package" in subscription:
            api_count = 0
            query = f"SELECT counts FROM apiusage WHERE email = '{email}'"
            result = mysql_connector.execute_query(query)
            
            if not result:
                api_token = generate_random_string(24)
                query = f"INSERT INTO apiusage (email, token, counts) VALUES \
                   ('{email}', '{api_token}', {package_counts[subscription]})"
                mysql_connector.execute_query(query)
            else:
                api_count += int(result[0][0])
                api_count += package_counts[subscription]
                query = f"update apiusage set counts={api_count} where email='{email}'"
                mysql_connector.execute_query(query)         

    mysql_connector.disconnect()
    logging.info({"notify": "done"})
    return {"notify": "done"}


@app.route('/payment/notification', methods=['POST'])
def payment_notification():
    data = request.get_json()
    print('Payment notification received:', json.dumps(data, indent=2))
    return '', 200

client_id = "AYMgaWCqhv9FPqVg8MTXvpRsAK0mPSyUa6I7nn1rTbZW-A7J-VwQJQwHJ3m0vQ8f00rYBu4kSnneZcD9"
client_secret = "EPLljnTsAt2s8-LU-1dhoX93T0mz74V6O55RpQM3cVi-hZvAuMNaZWEDIdaeg0H3nv9DABfPF7noAcv_"

@app.route('/create-paypal-order', methods=['POST'])
def create_paypal_order():
    amount = request.json.get('amount')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_access_token()}'
    }
    data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": amount
                }
            }
        ]
    }
    response = requests.post('https://api.paypal.com/v2/checkout/orders', json=data, headers=headers)
    logging.info(response)
    if response.status_code == 201:
        order_id = response.json()['id']
        return jsonify({'orderID': order_id})
    else:
        return jsonify({'error': response.json()}), 400

@app.route('/webhook', methods=['POST'])
def paypal_webhook():
    # 处理来自PayPal的Webhook通知
    # 在这里处理支付成功后的逻辑，比如更新订单状态等
    data = request.json
    event_type = data['event_type']
    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        order_id = data['resource']['id']
        # 在这里处理支付成功后的逻辑，比如更新订单状态等
        print(f"Payment successful! Order ID: {order_id}")
    return jsonify({'success': True})

def get_access_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post('https://api.paypal.com/v1/oauth2/token', data=data, headers=headers, auth=(client_id, client_secret))

    logging.info(response)

    access_token = response.json()['access_token']
    return access_token


if __name__ == "__main__":
    app.run(host=CONFIG.HOST, port=CONFIG.PORT, debug=True)
