
# from PIL import Image
# import numpy as np

# mask = Image.open("mask.png")

# mask_gray = mask.convert("L")
# mask_np = np.array(mask_gray)
# mask_binary = np.where(mask_np > 20, 255, 0).astype(np.uint8)
# mask = Image.fromarray(mask_binary)

# mask.save("mask_.png")



# image = Image.open("image.png")
# mask = Image.open("mask.png")
# image = image.convert("RGB")
# print(image.getbands())
# print(mask.getbands())

import cv2
import Final2x_core as Fin


def Myupscale(picPATH: list[str]) -> None:
    config = Fin.SRCONFIG()
    config.inputpath = picPATH  # init log percentage
    config.model = 'RealCUGAN-pro'

    SR = Fin.SRFactory.getSR()
    # RGB Mode, RGBA can refer Final2x_core.SR_queue
    for i in picPATH:
        img = cv2.imread(i, cv2.IMREAD_COLOR)
        img = SR.process(img)
        cv2.imwrite('Final2x-' + i, img)

Myupscale(["./pics/image.png"])