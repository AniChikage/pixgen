
from PIL import Image
import numpy as np

mask = Image.open("mask.png")

mask_gray = mask.convert("L")
mask_np = np.array(mask_gray)
mask_binary = np.where(mask_np > 20, 255, 0).astype(np.uint8)
mask = Image.fromarray(mask_binary)

mask.save("mask_.png")