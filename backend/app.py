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
from flask import Flask,request,send_file,cli, make_response,send_from_directory,jsonify
from PIL import Image, ImageOps, PngImagePlugin

from plugins.remove_bg import RemoveBG

import config as CONFIG
from utils import upload_file

NUM_THREADS = str(multiprocessing.cpu_count())
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
os.environ["OMP_NUM_THREADS"] = NUM_THREADS
os.environ["OPENBLAS_NUM_THREADS"] = NUM_THREADS
os.environ["MKL_NUM_THREADS"] = NUM_THREADS
os.environ["VECLIB_MAXIMUM_THREADS"] = NUM_THREADS
os.environ["NUMEXPR_NUM_THREADS"] = NUM_THREADS

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s %(levelname)s %(message)s", 
                    filemode="a",)
logger = logging.getLogger(__name__)


"""
USER
"""
@app.route("/api/register_user", methods=["POST"])
def register_user():
    email = request.form["email"]
    username = request.form["username"]
    password = request.form["password"]
    logging.info(f"{email} registering...")

    conn = sqlite3.connect(CONFIG.DATABASE)
    cursor = conn.cursor()
    query = f"SELECT COUNT(*) FROM user WHERE email = '{email}'"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    if (count > 0):
        return jsonify({"status": "-1", "msg": "该邮件已经注册！"})
    
    created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = f"INSERT INTO user (email, username, password, created_timestamp, \
                     effective_timestamp, effective_counts) VALUES \
                   ('{email}', '{username}', '{password}', '{created_time}', '{created_time}', 0)"
    cursor.execute(query)
    conn.commit()
    conn.close()

    return jsonify({"status": "0", "msg": "注册成功！正在跳转……"})


@app.route("/api/login_user", methods=["POST"])
def login_user():
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
        return jsonify({"status": "-1", "msg": "邮箱或密码错误！", "username": ""})

    return jsonify({"status": "0", "msg": "登陆成功，正在跳转……", "username": username})


@app.route("/api/user_profile", methods=["POST"])
def user_profile():
    email = request.form["email"]
    logging.info(f"{email} login...")

    conn = sqlite3.connect(CONFIG.DATABASE)
    cursor = conn.cursor()
    query = f"SELECT username, effective_timestamp, effective_counts FROM user WHERE email = '{email}'"
    cursor.execute(query)
    username, effective_timestamp, effective_counts = cursor.fetchone()
    conn.close()
    if username is None:
        return jsonify({"status": "-1", "msg": "邮箱或密码错误！", "data": ""})

    return jsonify({"status": "0", "msg": "获取资料成功", "username": username, \
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
            return {"status": "0", "msg": "有效", "effective": "1"}
        
    if int(effective_counts) > 0:
        return {"status": "0", "msg": "有效", "effective": "1"}

    return {"status": "-1", "msg": "无效", "effective": "0"}


@app.route("/api/check_pro", methods=["POST"])
def check_pro():
    email = request.form["email"]
    logging.info(f"{email} checking pro...")
    
    result = check_user_pro(email)
    return jsonify(result)


@app.route("/api/update_pro", methods=["POST"])
def update_pro():
    """
    only effective for reducing counts
    """
    email = request.form["email"]
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
@app.route("/api/remove_bg", methods=["POST"])
def remove_bg():
    email = request.form['email']
    image = request.files["image"]

    filename = image.filename
    image_pil = Image.open(image)
    image_removed_pil = RemoveBG()(image_pil)
    upload_file(image_pil, filename, processed=False)
    _, image_high_url, image_low_url = upload_file(image_removed_pil, filename, processed=True)

    user_pro = check_user_pro(email)
    if user_pro["effective"] == "0":
        image_high_url = ""

    return jsonify({"status": "1", "msg": "消除背景完成", "image_high_url": image_high_url, "image_low_url": image_low_url})


if __name__ == "__main__":
    app.run(host=CONFIG.HOST, port=CONFIG.PORT, debug=True)
