import os
import logging
import numpy as np

import torch
import cv2
from PIL import Image

import config as CONFIG
from utils import norm_img


class RemoveObject():
    def __init__(self):
        super().__init__()

        REMOVE_OBJECT_MODELS = {
            "lama": {
                "url": "https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt",
                "name": "big-lama.pt"
            }
        }
        model_info = REMOVE_OBJECT_MODELS["lama"]
        self.device = "cpu"
        logging.info(os.path.join(CONFIG.MODEL_PATH, model_info["name"]))
        self.model = torch.jit.load(os.path.join(CONFIG.MODEL_PATH, model_info["name"]), map_location="cpu").to("cpu")
        self.model.eval()

    def __call__(self, image, mask):
        """Input image and output image have same size
        image: [H, W, C] RGB
        mask: [H, W, C]
        return: BGR IMAGE
        """
        mask = mask.convert("L")
        mask = np.array(mask)
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        
        image = np.array(image)
        mask = np.array(mask)
        image = norm_img(image)
        mask = norm_img(mask)

        logging.info(image.shape)
        mask = (mask > 0) * 1
        logging.info(mask.shape)
        image = torch.from_numpy(image).unsqueeze(0).to(self.device)
        mask = torch.from_numpy(mask).unsqueeze(0).to(self.device)

        image_removed = self.model(image, mask)

        cur_res = image_removed[0].permute(1, 2, 0).detach().cpu().numpy()
        cur_res = np.clip(cur_res * 255, 0, 255).astype("uint8")
        # cur_res = cv2.cvtColor(cur_res, cv2.COLOR_RGB2BGR)
        cur_res = Image.fromarray(cur_res)
        return cur_res
