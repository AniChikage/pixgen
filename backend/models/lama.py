import os
import torch
import numpy as np
from PIL import Image
from utils import prepare_img_and_mask, download_model

import config as CONFIG

LAMA_MODEL_URL = os.environ.get(
    "LAMA_MODEL_URL",
    "https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt",
)


class LaMa:
    def __init__(self):
        self.device = torch.device("cpu")
        if os.environ.get("LAMA_MODEL"):
            model_path = os.environ.get("LAMA_MODEL")
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"lama torchscript model not found: {model_path}"
                )
        else:
            model_path = download_model(LAMA_MODEL_URL, CONFIG.MODEL_PATH)

        self.model = torch.jit.load(model_path, map_location=self.device)
        self.model.eval()
        self.model.to(self.device)

    def __call__(self, image: Image.Image | np.ndarray, mask: Image.Image | np.ndarray):
        image, mask = prepare_img_and_mask(image, mask, self.device)

        with torch.inference_mode():
            inpainted = self.model(image, mask)

            cur_res = inpainted[0].permute(1, 2, 0).detach().cpu().numpy()
            cur_res = np.clip(cur_res * 255, 0, 255).astype(np.uint8)

            cur_res = Image.fromarray(cur_res)
            return cur_res