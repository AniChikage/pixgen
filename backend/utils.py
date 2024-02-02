import os
import sys
import random
import string
import logging
import paramiko

import cv2
import redis
import numpy as np
from PIL import Image

import torch
from torch.hub import download_url_to_file, get_dir
from urllib.parse import urlparse

import config as CONFIG


redis_client = redis.StrictRedis(host=CONFIG.REDIS_HOST, port=CONFIG.REDIS_PORT, password=CONFIG.REDIS_PASSWORD, decode_responses=True)

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

def generate_random_integer(length=6):
    random_number = random.randint(100000, 999999)
    return str(random_number)


def down_image_size(image_pil):
    original_width, original_height = image_pil.size
    resized_image = image_pil
    logging.info(f"original image size: {image_pil.size}")
    down_ratio = 8
    if original_width * original_height >= 1500 * 1500:
        new_width = original_width // 2
        new_height = original_height // 2
        resized_image = image_pil.resize((new_width, new_height))
        down_ratio = 4
    logging.info(f"resized image size: {resized_image.size}")
    return resized_image, down_ratio


def upload_file(image, filename, processed=False, plugin_name="", down_ratio=2):
    max_size = 10 * 1024 * 1024
    quality = 85
    image_data = image.tobytes()
    image_size = len(image_data)

    remote_origin_image_url = ""
    remote_processed_image_high_url = ""
    remote_processed_image_low_url = ""
    if not processed:
        local_file = os.path.join(CONFIG.LOCAL_PATH, filename)
        remote_file = os.path.join(CONFIG.REMOTE_PATH, filename)
        remote_origin_image_url = f"https://{CONFIG.CUSTOM_DOMAIN}:{CONFIG.REMOTE_PORT}/images/pixgen/{filename}"
        logging.info(f"remote_origin_image_url")
        image.save(local_file)
    else:
        # save original-size image
        logging.info(f"image_size: {image_size}")
        logging.info(f"max_size: {max_size}")
        # convert to jpg if image size > 10M, except for removebg, it needs transparency
        if image_size < max_size or plugin_name == "removebg":
            base_filename, _ = os.path.splitext(filename)
            random_tails = generate_random_string()
            processed_filename = f"{base_filename}_{plugin_name}_{random_tails}.png"
            local_high_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
            remote_high_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
            remote_processed_image_high_url = f"https://{CONFIG.CUSTOM_DOMAIN}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
            image.save(local_high_file)
            # save half-size image
            image_resized = image.resize((image.width // down_ratio, image.height // down_ratio))
            random_tails = generate_random_string()
            processed_filename = f"{base_filename}_{plugin_name}_{random_tails}.png"
            local_low_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
            remote_low_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
            remote_processed_image_low_url = f"https://{CONFIG.CUSTOM_DOMAIN}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
            image_resized.save(local_low_file)
        else:
            base_filename, _ = os.path.splitext(filename)
            random_tails = generate_random_string()
            processed_filename = f"{base_filename}_{plugin_name}_{random_tails}.jpg"
            local_high_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
            remote_high_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
            remote_processed_image_high_url = f"https://{CONFIG.CUSTOM_DOMAIN}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(local_high_file, "JPEG", quality=quality)
            # save half-size image
            image_resized = image.resize((image.width // down_ratio, image.height // down_ratio))
            random_tails = generate_random_string()
            processed_filename = f"{base_filename}_{plugin_name}_{random_tails}.jpg"
            local_low_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
            remote_low_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
            remote_processed_image_low_url = f"https://{CONFIG.CUSTOM_DOMAIN}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
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


def filter_wx_code(code):
    stored_code = redis_client.get(code)
    if stored_code:
        return None
    else:
        redis_client.set(code, code)
        redis_client.expire(token, 5)
        return code


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


# Source https://github.com/advimman/lama
def get_image(image):
    if isinstance(image, Image.Image):
        img = np.array(image)
    elif isinstance(image, np.ndarray):
        img = image.copy()
    else:
        raise Exception("Input image should be either PIL Image or numpy array!")

    if img.ndim == 3:
        img = np.transpose(img, (2, 0, 1))  # chw
    elif img.ndim == 2:
        img = img[np.newaxis, ...]

    assert img.ndim == 3

    img = img.astype(np.float32) / 255
    return img


def ceil_modulo(x, mod):
    if x % mod == 0:
        return x
    return (x // mod + 1) * mod


def scale_image(img, factor, interpolation=cv2.INTER_AREA):
    if img.shape[0] == 1:
        img = img[0]
    else:
        img = np.transpose(img, (1, 2, 0))

    img = cv2.resize(img, dsize=None, fx=factor, fy=factor, interpolation=interpolation)

    if img.ndim == 2:
        img = img[None, ...]
    else:
        img = np.transpose(img, (2, 0, 1))
    return img


def pad_img_to_modulo(img, mod):
    channels, height, width = img.shape
    out_height = ceil_modulo(height, mod)
    out_width = ceil_modulo(width, mod)
    return np.pad(
        img,
        ((0, 0), (0, out_height - height), (0, out_width - width)),
        mode="symmetric",
    )


def prepare_img_and_mask(image, mask, device, pad_out_to_modulo=8, scale_factor=None):
    out_image = get_image(image)
    out_mask = get_image(mask)

    if scale_factor is not None:
        out_image = scale_image(out_image, scale_factor)
        out_mask = scale_image(out_mask, scale_factor, interpolation=cv2.INTER_NEAREST)

    if pad_out_to_modulo is not None and pad_out_to_modulo > 1:
        out_image = pad_img_to_modulo(out_image, pad_out_to_modulo)
        out_mask = pad_img_to_modulo(out_mask, pad_out_to_modulo)

    out_image = torch.from_numpy(out_image).unsqueeze(0).to(device)
    out_mask = torch.from_numpy(out_mask).unsqueeze(0).to(device)

    out_mask = (out_mask > 0) * 1

    return out_image, out_mask


# Source: https://github.com/Sanster/lama-cleaner/blob/6cfc7c30f1d6428c02e21d153048381923498cac/lama_cleaner/helper.py # noqa
def get_cache_path_by_url(url, model_dir=None):
    parts = urlparse(url)
    hub_dir = get_dir()
    if model_dir is None:
        model_dir = os.path.join(hub_dir, "checkpoints")
    if not os.path.isdir(model_dir):
        os.makedirs(os.path.join(model_dir))
    filename = os.path.basename(parts.path)
    cached_file = os.path.join(model_dir, filename)
    return cached_file


def download_model(url):
    model_dir = CONFIG.MODEL_PATH
    cached_file = get_cache_path_by_url(url, model_dir)
    if not os.path.exists(cached_file):
        sys.stderr.write('Downloading: "{}" to {}\n'.format(url, cached_file))
        hash_prefix = None
        download_url_to_file(url, cached_file, hash_prefix, progress=True)
    return cached_file


def resize_mask(image, mask):
    image_width, image_height = image.size
    mask_width, mask_height = mask.size

    if image_width == mask_width and image_height == mask_height:
        return mask

    return mask.resize((image_width, image_height))


def enrich_mask(mask):
    mask_gray = mask.convert("L")
    mask_np = np.array(mask_gray)
    mask_binary = np.where(mask_np > 20, 255, 0).astype(np.uint8)
    mask = Image.fromarray(mask_binary)
    return mask