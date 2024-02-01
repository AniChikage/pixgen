import os
import logging
import numpy as np

import cv2
import torch
from PIL import Image
from basicsr.utils import imwrite
# from realesrgan import RealESRGANer
from gfpgan.utils import GFPGANer
from realesrgan.utils import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

import config as CONFIG


class RealESRGANUpscaler():
    def __init__(self):
        super().__init__()

        self.DEVICE = "cuda:1" if torch.cuda.is_available() else "cpu"

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
            half=False if self.DEVICE == "cpu" else True,
            tile=512,
            tile_pad=10,
            pre_pad=10,
            device=self.DEVICE,
        )

        
        model_path_gfpgan = os.path.join(CONFIG.MODEL_PATH, "GFPGANv1.4.pth")
        model_path_realesr = os.path.join(CONFIG.MODEL_PATH, "realesr-general-x4v3.pth")
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
            tile=512, 
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

    def enhance(self, upsampled):
        cropped_faces, restored_faces, restored_img = self.restorer.enhance(upsampled, paste_back=True, weight=0.5)

        imwrite(restored_img, "restored_img.jpg")

        img_rgb = cv2.cvtColor(restored_img, cv2.COLOR_BGR2RGB)
        restored_img_pil = Image.fromarray(img_rgb)
        return restored_img_pil


    def upscale(self, image):
        image_rgb_np = np.array(image)
        upsampled = self.model.enhance(image_rgb_np, outscale=2)[0]
        upsampled = cv2.cvtColor(upsampled, cv2.COLOR_RGB2BGR)
        upsampled_pil = self.enhance(upsampled)
        # upsampled_pil = Image.fromarray(upsampled)
        torch.cuda.empty_cache()
        if torch.cuda.is_available():
            torch.cuda.reset_max_memory_allocated(device=self.DEVICE)
            torch.cuda.reset_max_memory_cached(device=self.DEVICE)
        return upsampled_pil
