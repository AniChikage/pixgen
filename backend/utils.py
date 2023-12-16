import os
import random
import string
import paramiko
from PIL import Image

import config as CONFIG


def generate_random_string(length=4):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def upload_file(image, filename, processed=False):
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
        processed_filename = f"{base_filename}_removebg_{random_tails}.png"
        local_high_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
        remote_high_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
        remote_processed_image_high_url = f"http://{CONFIG.REMOTE_HOST}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
        image.save(local_high_file)
        # save half-size image
        image_resized = image.resize((image.width // 2, image.height // 2))
        random_tails = generate_random_string()
        processed_filename = f"{base_filename}_removebg_{random_tails}.png"
        local_low_file = os.path.join(CONFIG.LOCAL_PATH, processed_filename)
        remote_low_file = os.path.join(CONFIG.REMOTE_PATH, processed_filename)
        remote_processed_image_low_url = f"http://{CONFIG.REMOTE_HOST}:{CONFIG.REMOTE_PORT}/images/pixgen/{processed_filename}"
        image_resized.save(local_low_file)

    try:
        transport = paramiko.Transport((CONFIG.REMOTE_HOST, 22))
        transport.connect(username=CONFIG.REMOTE_USERNAME, password=CONFIG.REMOTE_PASSWORD)
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
