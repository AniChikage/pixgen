import os
from rembg import new_session, remove
from PIL import Image, ImageFilter

import config as CONFIG


class BlurBackground():
    def __init__(self):
        super().__init__()

        os.environ["U2NET_HOME"] = CONFIG.MODEL_PATH
        self.session = new_session(model_name="u2net")

    def __call__(self, image, degree):
        output = remove(image, session=self.session)
        if image.size != output.size:
            image = image.transpose(Image.Transpose.ROTATE_270)
        image = image.filter(ImageFilter.GaussianBlur(radius=int(degree)))
        output = Image.alpha_composite(image.convert("RGBA"), output)
        return output
