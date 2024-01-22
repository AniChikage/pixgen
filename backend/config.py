
CUSTOM_DOMAIN = "pixgen.pro"
HOST = "0.0.0.0"
PORT = "8001"
HTTPS_PORT = "8002"
LOCAL_PATH="/home/brook/workspace/pixgen-images"
REMOTE_HOST = "82.157.250.59"
REMOTE_PORT = "8010"
REMOTE_PATH = "/var/www/html/images/pixgen/"
REMOTE_USERNAME = "ubuntu"
REMOTE_PRIVATE_KEY = "/home/brook/.ssh/id_rsa"

DATABASE = "./database/studio.sqlite"
MODEL_PATH = "/home/brook/workspace/models"

REDIS_HOST = "localhost"
REDIS_PORT = 6379

WX_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WX_USERINFO_URL = "https://api.weixin.qq.com/sns/userinfo"

PRICE_CONFIG = {
    "0.01": "trial",
    "1.90": "trial",
    "4.90": "flexible",
    "9.90": "plus"
}