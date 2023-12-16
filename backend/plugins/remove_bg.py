import os
from rembg import new_session, remove

import config as CONFIG


class RemoveBG():
    def __init__(self):
        super().__init__()

        os.environ["U2NET_HOME"] = CONFIG.MODEL_PATH
        self.session = new_session(model_name="u2net")

    def __call__(self, image):
        output = remove(image, session=self.session)
        return output
