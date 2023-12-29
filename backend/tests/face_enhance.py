import argparse
import cv2
import glob
import numpy as np
import os
import torch
from basicsr.utils import imwrite

from gfpgan import GFPGANer

model_path = "/home/brook/workspace/models/GFPGANv1.4.pth"

bg_upsampler = None

restorer = GFPGANer(
    model_path=model_path,
    upscale=2,
    arch="clean",
    channel_multiplier=2,
    bg_upsampler=bg_upsampler)

img_path = "/home/brook/workspace/pixgen/backend/tests/aaa.jpg"
img_name = os.path.basename(img_path)
print(f'Processing {img_name} ...')
basename, ext = os.path.splitext(img_name)
input_img = cv2.imread(img_path, cv2.IMREAD_COLOR)

suffix = "sss"

# restore faces and background if necessary
cropped_faces, restored_faces, restored_img = restorer.enhance(
    input_img,
    # has_aligned=args.aligned,
    # only_center_face=args.only_center_face,
    # arch="clean",
    paste_back=True,
    weight=0.5)

for idx, (cropped_face, restored_face) in enumerate(zip(cropped_faces, restored_faces)):
    # save cropped face
    save_crop_path = os.path.join("/home/brook/workspace/pixgen/backend/tests/", 'cropped_faces', f'{basename}_{idx:02d}.png')
    imwrite(cropped_face, save_crop_path)
    # save restored face
    if suffix is not None:
        save_face_name = f'{basename}_{idx:02d}_{suffix}.png'
    else:
        save_face_name = f'{basename}_{idx:02d}.png'
    save_restore_path = os.path.join("/home/brook/workspace/pixgen/backend/tests/", 'restored_faces', save_face_name)
    imwrite(restored_face, save_restore_path)
    # save comparison image
    cmp_img = np.concatenate((cropped_face, restored_face), axis=1)
    imwrite(cmp_img, os.path.join("/home/brook/workspace/pixgen/backend/tests/", 'cmp', f'{basename}_{idx:02d}.png'))

# save restored img
ext = "jpg"
if restored_img is not None:
    if ext == 'auto':
        extension = ext[1:]
    else:
        extension = ext

    if suffix is not None:
        save_restore_path = os.path.join("/home/brook/workspace/pixgen/backend/tests/", 'restored_imgs', f'{basename}_{suffix}.{extension}')
    else:
        save_restore_path = os.path.join("/home/brook/workspace/pixgen/backend/tests/", 'restored_imgs', f'{basename}.{extension}')
    imwrite(restored_img, save_restore_path)


# from gfpgan.utils import GFPGANer

# # 初始化GFPGAN修复器
# gfpganaa = GFPGANer(device='cpu', model_path='/home/brook/workspace/models/GFPGANv1.4.pth')

# # 读取需要修复的图片
# input_image = 'aaa.jpg'

# # 使用GFPGAN进行修复
# output_image = 'bbb.jpg'
# gfpganaa.enhance(input_image, output_image)
