
CUSTOM_DOMAIN = "pixgen.pro"
HOST = "0.0.0.0"
PORT = "8001"
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

PRICE_CONFIG = {
    "0.01": "trial",
    "0.02": "flexible",
    "0.03": "plus"
}