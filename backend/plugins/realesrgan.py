import os
import logging
import numpy as np

import cv2
from PIL import Image
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

import config as CONFIG


class RealESRGANUpscaler():
    def __init__(self):
        super().__init__()

        REAL_ESRGAN_MODELS = {
            "realesr_general_x4v3": {
                "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
                "scale": 4,
                "model": lambda: SRVGGNetCompact(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_conv=32,
                    upscale=4,
                    act_type="prelu",
                ),
                "model_md5": "91a7644643c884ee00737db24e478156",
            },
            "RealESRGAN_x4plus": {
                "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                "scale": 4,
                "model": lambda: RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32,
                    scale=4,
                ),
                "model_md5": "99ec365d4afad750833258a1a24f44ca",
            },
            "RealESRGAN_x4plus_anime_6B": {
                "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
                "scale": 4,
                "model": lambda: RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=6,
                    num_grow_ch=32,
                    scale=4,
                ),
                "model_md5": "d58ce384064ec1591c2ea7b79dbf47ba",
            },
        }

        model_info = REAL_ESRGAN_MODELS["RealESRGAN_x4plus"]
        self.model = RealESRGANer(
            scale=model_info["scale"],
            model_path=os.path.join(CONFIG.MODEL_PATH, "RealESRGAN_x4plus.pth"),
            model=model_info["model"](),
            half=False,
            tile=512,
            tile_pad=10,
            pre_pad=10,
            device="cpu",
        )


    def __call__(self, image):
        image_rgb_np = np.array(image)
        upsampled = self.model.enhance(image_rgb_np, outscale=2)[0]
        upsampled_pil = Image.fromarray(upsampled)
        return upsampled_pil
