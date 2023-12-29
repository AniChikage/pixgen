
import cv2
import glob
import numpy as np
import os
import torch
from basicsr.utils import imwrite

import insightface
from insightface.app import FaceAnalysis

import numpy as np
from PIL import Image

from basicsr.archs.srvgg_arch import SRVGGNetCompact
from gfpgan.utils import GFPGANer
from realesrgan.utils import RealESRGANer

import warnings

warnings.filterwarnings("ignore")


model_path = "/home/brook/workspace/models/GFPGANv1.4.pth"

model = SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type='prelu')
model_path_realesr = '/home/brook/workspace/models/realesr-general-x4v3.pth'
half = True if torch.cuda.is_available() else False
bg_upsampler = RealESRGANer(scale=4, model_path=model_path_realesr, model=model, tile=0, tile_pad=10, pre_pad=0, half=half)

restorer = GFPGANer(
    model_path=model_path,
    upscale=2,
    arch="clean",
    channel_multiplier=2,
    bg_upsampler=bg_upsampler)

def swap_faces(faceSource, sourceFaceId, faceDestination, destFaceId):
    app = FaceAnalysis(name='buffalo_l')
    print(faceDestination.shape)
    app.prepare(ctx_id=0, det_size=(640, 640))
    swapper = insightface.model_zoo.get_model('inswapper_128.onnx', root="/home/brook/workspace/models", download=True, download_zip=False)
    faces = app.get(faceSource)
    faces = sorted(faces, key = lambda x : x.bbox[0])
    if len(faces) < sourceFaceId or sourceFaceId < 1:
        raise gr.Error(f"Source image only contains {len(faces)} faces, but you requested face {sourceFaceId}")
        
    source_face = faces[sourceFaceId-1]

    res_faces = app.get(faceDestination)
    res_faces = sorted(res_faces, key = lambda x : x.bbox[0])
    if len(res_faces) < destFaceId or destFaceId < 1:
        raise gr.Error(f"Destination image only contains {len(res_faces)} faces, but you requested face {destFaceId}")
    res_face = res_faces[destFaceId-1]

    result = swapper.get(faceDestination, res_face, source_face, paste_back=True)
    return result

def enhance(input_img, basename, ext):
    cropped_faces, restored_faces, restored_img = restorer.enhance(
    input_img,
    has_aligned=False,
    only_center_face=False,
    # arch="clean",
    paste_back=True,
    weight=0.5)


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


img_name = "source.jpg"
basename, ext = os.path.splitext(img_name)

src = Image.open(img_name)
dst = Image.open("target2.jpg")

src = np.array(src)
dst = np.array(dst)

ret = swap_faces(src, 1, dst, 1)
# rett = Image.fromarray(ret)
# rett.save("aaa.jpg")

# img_path = "/home/brook/workspace/pixgen/backend/tests/aaa.jpg"
# img_name = os.path.basename(img_path)
# print(f'Processing {img_name} ...')
# basename, ext = os.path.splitext(img_name)
# input_img = cv2.imread(img_path, cv2.IMREAD_COLOR)

input_img = cv2.cvtColor(ret, cv2.COLOR_RGB2BGR)
enhance(input_img, basename, ext)
