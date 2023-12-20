import os
import random
import string
import paramiko

import redis
import numpy as np
from PIL import Image

import config as CONFIG


redis_client = redis.StrictRedis(host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, decode_responses=True)

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

def generate_random_integer(length=6):
    random_number = random.randint(100000, 999999)
    return str(random_number)


def upload_file(image, filename, processed=False, plugin_name=""):
    remote_origin_image_url = ""
    remote_processed_image_high_url = ""
    remote_processed_image_low_url = ""
    if not processed:
        local_file = os.path.join(CONFIG.LOCAL_PATH, filename)
        remote_file = os.path.join(CONFIG.REMOTE_PATH, filename)
        remote_origin_image_url = f"http://{CONFIG.REMOTE_HOST}:{CONFIG.REMOTE_PORT}/images/pixgen/{filename}"
        image.save(local_file)
    else:
        # save original-size image
        base_filename, _ = os.path.splitext(filename)
        random_tails = generate_random_string()
        processed_filename = f"{base_filename}_{plugin_name}_{random_tails}.png"
        local_high_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
        remote_high_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
        remote_processed_image_high_url = f"http://{CONFIG.REMOTE_HOST}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
        image.save(local_high_file)
        # save half-size image
        image_resized = image.resize((image.width // 2, image.height // 2))
        random_tails = generate_random_string()
        processed_filename = f"{base_filename}_{plugin_name}_{random_tails}.png"
        local_low_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
        remote_low_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
        remote_processed_image_low_url = f"http://{CONFIG.REMOTE_HOST}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
        image_resized.save(local_low_file)

    try:
        private_key = paramiko.RSAKey(filename=CONFIG.REMOTE_PRIVATE_KEY)
        transport = paramiko.Transport((CONFIG.REMOTE_HOST, 22))
        transport.connect(username=CONFIG.REMOTE_USERNAME, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        if not processed:
            sftp.put(local_file, remote_file) 
        else:
            sftp.put(local_high_file, remote_high_file)    
            sftp.put(local_low_file, remote_low_file)        
    except Exception as e:
        print(f"Error uploading file: {e}")
    finally:
        if sftp:
            sftp.close()
        if transport:
            transport.close()

    return remote_origin_image_url, remote_processed_image_high_url, remote_processed_image_low_url


def norm_img(np_img):
    if len(np_img.shape) == 2:
        np_img = np_img[:, :, np.newaxis]
    np_img = np.transpose(np_img, (2, 0, 1))
    np_img = np_img.astype("float32") / 255
    return np_img


def generate_token(email):
    token = generate_random_string(24)
    redis_client.set(token, email)
    redis_client.expire(token, 86400)
    return token


def get_email_from_token(token):
    email = redis_client.get(token)
    return email


def generate_validation_code(email):
    code = generate_random_integer()
    redis_client.set(email, code)
    redis_client.expire(email, 300)
    return code


def get_validation_code_from_email(email):
    validation_code = redis_client.get(email)
    return validation_code
