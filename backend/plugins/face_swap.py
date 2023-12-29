import os
import cv2
import glob
import torch
import numpy as np

import insightface
from PIL import Image
from insightface.app import FaceAnalysis
from basicsr.utils import imwrite
from basicsr.archs.srvgg_arch import SRVGGNetCompact
from gfpgan.utils import GFPGANer
from realesrgan.utils import RealESRGANer

import config as CONFIG


class FaceSwap():
    def __init__(self):
        super().__init__()

        self.model_info = {
            "gfpgan_model": "GFPGANv1.4.pth",
            "realesr_model": "realesr-general-x4v3.pth",
            "swapper_model": "inswapper_128.onnx",
            "swapper_size": (640, 640),
            "swapper_suffix": "swapper"
        }

        model_path_gfpgan = os.path.join(CONFIG.MODEL_PATH, self.model_info["gfpgan_model"])
        model_path_realesr = os.path.join(CONFIG.MODEL_PATH, self.model_info["realesr_model"])

        model = SRVGGNetCompact(
            num_in_ch=3, 
            num_out_ch=3, 
            num_feat=64, 
            num_conv=32, 
            upscale=4, 
            act_type="prelu"
        )
        bg_upsampler = RealESRGANer(
            scale=4, 
            model_path=model_path_realesr, 
            model=model, 
            tile=0, 
            tile_pad=10, 
            pre_pad=0, 
            half=False
        )

        self.restorer = GFPGANer(
            model_path=model_path_gfpgan,
            upscale=2,
            arch="clean",
            channel_multiplier=2,
            bg_upsampler=bg_upsampler
        )

    def swap_faces(self, faceSource, sourceFaceId, faceDestination, destFaceId):
        app = FaceAnalysis(name="buffalo_l")
        app.prepare(ctx_id=0, det_size=self.model_info["swapper_size"])
        swapper = insightface.model_zoo.get_model(self.model_info["swapper_model"], root=CONFIG.MODEL_PATH, download=True, download_zip=False)
        faces = app.get(faceSource)
        faces = sorted(faces, key = lambda x : x.bbox[0])
        if len(faces) < sourceFaceId or sourceFaceId < 1:
            # raise gr.Error(f"Source image only contains {len(faces)} faces, but you requested face {sourceFaceId}")
            return None
            
        source_face = faces[sourceFaceId-1]
        res_faces = app.get(faceDestination)
        res_faces = sorted(res_faces, key = lambda x : x.bbox[0])
        if len(res_faces) < destFaceId or destFaceId < 1:
            # raise gr.Error(f"Destination image only contains {len(res_faces)} faces, but you requested face {destFaceId}")
            return None
        res_face = res_faces[destFaceId-1]

        result = swapper.get(faceDestination, res_face, source_face, paste_back=True)
        return result

    def enhance(self, swapped_image_bgr):
        cropped_faces, restored_faces, restored_img = self.restorer.enhance(swapped_image_bgr, has_aligned=False, only_center_face=False, paste_back=True, weight=0.5)
        restored_img_pil = Image.fromarray(restored_img)
        return restored_img_pil

    def __call__(self, source, filename, target):
        src = np.array(source)
        dst = np.array(target)

        swapped_image = self.swap_faces(src, 1, dst, 1)
        swapped_image_pil = self.enhance(swapped_image)

        return swapped_image_pil



