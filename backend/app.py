# -*- coding: utf-8 -*-
import os
import io
import json
import hashlib
import logging
import random
import time
import string
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

from plugins.remove_bg import RemoveBG
from plugins.realesrgan import RealESRGANUpscaler
from plugins.remove_object import RemoveObject

import config as CONFIG
from utils import (
     upload_file, 
     generate_token, 
     get_email_from_token, 
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
        "description": "PIXGEN相关API使用说明",
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
      - name: validation_code
        in: formData
        type: string
        required: true
        description: 邮箱验证码
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
    validation_code = request.form["validation_code"]
    logging.info(f"{email} registering...")


    stored_validation_code = get_validation_code_from_email(email)
    if stored_validation_code is None:
        return jsonify({"status": "-2", "msg": "验证码过期", "token": ""})
    if stored_validation_code != validation_code:
        return jsonify({"status": "-3", "msg": "验证码不正确", "token": ""})
    conn = sqlite3.connect(CONFIG.DATABASE)
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM user WHERE email = '{email}'"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    if (count > 0):
        return jsonify({"status": "-1", "msg": "该邮件已经注册", "token": ""})
    
    created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = f"INSERT INTO user (email, username, password, created_timestamp, \
                     effective_timestamp, effective_counts) VALUES \
                   ('{email}', '{username}', '{password}', '{created_time}', '{created_time}', 0)"
    cursor.execute(query)
    conn.commit()
    conn.close()

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

    conn = sqlite3.connect(CONFIG.DATABASE)
    cursor = conn.cursor()
    query = f"SELECT username FROM user WHERE email = '{email}' and password = '{password}'"
    cursor.execute(query)
    username = cursor.fetchone()[0]
    conn.close()
    if username is None:
        return jsonify({"status": "-1", "msg": "邮箱或密码错误", "username": "", "token": ""})

    token = generate_token(email)

    return jsonify({"status": "1", "msg": "登陆成功", "username": username, "token": token})


@app.route("/api/user/user_profile", methods=["POST"])
def user_profile():
    """
    获取用户信息

    ---
    tags:
      - User
    parameters:
      - name: token
        in: formData
        type: string
        required: true
        description: 用户token
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
              type: string
              description: 提示信息. status==1 => 次数; status==-1 => 空字符串; status==-10 => 空字符串
    """
    token = request.form["token"]
    email = get_email_from_token(token)
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "username": "", "effective_timestamp": "", "effective_counts": ""})
    logging.info(f"{email} login...")

    conn = sqlite3.connect(CONFIG.DATABASE)
    cursor = conn.cursor()
    query = f"SELECT username, effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    cursor.execute(query)
    username, effective_timestamp, effective_counts = cursor.fetchone()
    conn.close()
    if username is None:
        return jsonify({"status": "-1", "msg": "获取资料失败", "username": "", "effective_timestamp": "", "effective_counts": ""})

    return jsonify({"status": "1", "msg": "获取资料成功", "username": username, \
                    "effective_timestamp": effective_timestamp, \
                    "effective_counts": effective_counts})


def check_user_pro(email):
    conn = sqlite3.connect(CONFIG.DATABASE)
    cursor = conn.cursor()
    query = f"SELECT effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    cursor.execute(query)
    result = cursor.fetchone()
    effective_timestamp, effective_counts = result
    conn.close()

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
      - name: token
        in: formData
        type: string
        required: true
        description: 用户token
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
    token = request.form["token"]
    email = get_email_from_token(token)
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
      - name: token
        in: formData
        type: string
        required: true
        description: 用户token
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
    token = request.form["token"]
    email = get_email_from_token(token)
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})
    logging.info(f"{email} updating pro...")

    conn = sqlite3.connect(CONFIG.DATABASE)
    cursor = conn.cursor()
    query = f"SELECT effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    cursor.execute(query)
    result = cursor.fetchone()
    _, effective_counts = result

    if int(effective_counts) <= 0:
        return jsonify({"status": "-1", "msg": "无剩余次数", "effective": "0"})

    effective_counts -= 1
    query = f"update user set effective_counts={effective_counts} where email = '{email}'"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

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
      - name: token
        in: formData
        type: string
        required: false
        description: 用户token
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
    if "token" in request.form:
        token = request.form["token"]
        email = get_email_from_token(token)
    else:
        email = None

    filename = image.filename
    image_pil = Image.open(image)
    image_removed_pil = RemoveBG()(image_pil)
    upload_file(image_pil, filename, processed=False, plugin_name="removebg")
    _, image_high_url, image_low_url = upload_file(image_removed_pil, filename, processed=True, plugin_name="removebg")

    if email is None:
        image_high_url = ""
    else:
        user_pro = check_user_pro(email)
        if user_pro["effective"] == "0":
            image_high_url = ""

    return jsonify({"status": "1", "msg": "消除背景完成", "image_high_url": image_high_url, "image_low_url": image_low_url})


@app.route("/api/plugin/upscaler", methods=["POST"])
def upscaler():
    """
    图片放大

    ---
    tags:
      - Plugin
    parameters:
      - name: token
        in: formData
        type: string
        required: false
        description: 用户token
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
    if "token" in request.form:
        token = request.form["token"]
        email = get_email_from_token(token)
    else:
        email = None

    logging.info(f"{email}")

    filename = image.filename
    image_pil = Image.open(image)
    image_removed_pil = RealESRGANUpscaler()(image_pil)
    upload_file(image_pil, filename, processed=False, plugin_name="upscaler")
    _, image_high_url, image_low_url = upload_file(image_removed_pil, filename, processed=True, plugin_name="upscaler")

    if email is None:
        image_high_url = ""
    else:
        user_pro = check_user_pro(email)
        if user_pro["effective"] == "0":
            image_high_url = ""

    return jsonify({"status": "1", "msg": "放大完成", "image_high_url": image_high_url, "image_low_url": image_low_url})


@app.route("/api/remove_object", methods=["POST"])
def remove_object():
    image = request.files["image"]
    mask = request.files["mask"]
    token = request.form["token"]
    email = get_email_from_token(token)
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆"})

    filename = image.filename
    image_pil = Image.open(image)
    mask_pil = Image.open(mask)
    image_removed_pil = RemoveObject()(image_pil, mask_pil)
    upload_file(image_pil, filename, processed=False, plugin_name="remove_object")
    _, image_high_url, image_low_url = upload_file(image_removed_pil, filename, processed=True, plugin_name="remove_object")

    user_pro = check_user_pro(email)
    if user_pro["effective"] == "0":
        image_high_url = ""

    return jsonify({"status": "1", "msg": "放大完成", "image_high_url": image_high_url, "image_low_url": image_low_url})


"""
order
"""
@app.route("/api/order/create_order", methods=["POST"])
def create_order():
    """
    创建订单

    ---
    tags:
      - Order
    parameters:
      - name: token
        in: formData
        type: string
        required: true
        description: 用户token
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
    token = request.form["token"]
    email = get_email_from_token(token)
    if email is None:
        return jsonify({"status": "-10", "msg": "登录有效期已过，请重新登陆", "effective": "0"})

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
    orderRequest.notify_url = f"http://pixgen.pro:{CONFIG.PORT}/api/order/notify_order"
    response = client.page_execute(orderRequest, http_method="GET")
    logging.info("alipay.trade.page.pay response:" + response)

    conn = sqlite3.connect('./database/studio.sqlite')
    cursor = conn.cursor()
    query = f"insert into orders (email, out_trade_no, total_amount, \
                    trade_status, trade_no, gmt_create, gmt_payment, create_time) values \
                    ('{email}', '{out_trade_no}', '', '', '', '', '', '{order_created_timestamp}')"
    logging.info(query)
    cursor.execute(query)
    conn.commit()

    return {"status": "1", "msg": "创建成功", "url": response, "out_trade_no": out_trade_no}


@app.route("/api/order/notify_order", methods=["POST"])
def notify_order():
    logging.info("notify_order")
    out_trade_no = request.form["out_trade_no"]
    total_amount = request.form["total_amount"]
    trade_status = request.form["trade_status"]
    trade_no = request.form["trade_no"]
    gmt_create = request.form["gmt_create"]
    gmt_payment = request.form["gmt_payment"]

    logging.info(f"out_trade_no: {out_trade_no}")
    conn = sqlite3.connect('./database/studio.sqlite')
    cursor = conn.cursor()

    # get trade status
    query = f"SELECT trade_status FROM orders WHERE out_trade_no = '{out_trade_no}'"
    logging.info(query)
    cursor.execute(query)
    result = cursor.fetchone()
    last_trade_status = result[0]
    logging.info(f"trade_status: {last_trade_status}")
    if last_trade_status == "TRADE_SUCCESS":
        return {"notify": "done"}

    # update orders
    query = f"update orders set total_amount='{total_amount}', trade_status='{trade_status}', \
              trade_no='{trade_no}', gmt_create='{gmt_create}', gmt_payment='{gmt_payment}' \
              where out_trade_no='{out_trade_no}'"
    logging.info(query)
    cursor.execute(query)
    conn.commit()

    # get user email
    query = f"SELECT email FROM orders WHERE out_trade_no = '{out_trade_no}'"
    logging.info(query)
    cursor.execute(query)
    result = cursor.fetchone()
    email = result[0]
    logging.info(f"email: {email}")

    # get last effective timestamp
    query = f"SELECT effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    logging.info(query)
    cursor.execute(query)
    result = cursor.fetchone()
    last_effective_timestamp, last_effective_counts = result
    logging.info(f"last_effective_timestamp: {last_effective_timestamp}, last_effective_counts: {last_effective_counts}")

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
            cursor.execute(query)
            conn.commit()
            logging.info(f"update {email} from {last_effective_timestamp} to {effective_timestamp}")
        elif subscription == "flexible":
            last_effective_counts += 100
            query = f"update user set effective_counts={last_effective_counts} where email='{email}'"
            cursor.execute(query)
            conn.commit()
            logging.info(f"update {email} to {last_effective_counts}")
        elif subscription == "plus":
            effective_timestamp = last_effective_timestamp + timedelta(days=30)
            effective_timestamp = effective_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            query = f"update user set effective_timestamp='{effective_timestamp}' where email='{email}'"
            cursor.execute(query)
            conn.commit()
            logging.info(f"update {email} from {last_effective_timestamp} to {effective_timestamp}")

    logging.info({"notify": "done"})
    return {"notify": "done"}




if __name__ == "__main__":
    app.run(host=CONFIG.HOST, port=CONFIG.PORT, debug=True)
