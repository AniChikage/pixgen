import os
import logging
import numpy as np

import torch
import cv2
from PIL import Image
from models.lama import LaMa

import config as CONFIG
from utils import norm_img


class RemoveObject():
    def __init__(self):
        super().__init__()
        self.lama = LaMa()

    def __call__(self, image, mask):
        """Input image and output image have same size
        image: [H, W, C] RGB
        mask: [H, W, C]
        return: BGR IMAGE
        """
        mask = mask.convert("L")
        mask = np.array(mask)
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

        result = self.lama(image, mask)
        return result

