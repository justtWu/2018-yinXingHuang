#coding=utf-8
import logging
from config import SSH_LOG_FILE
#########loggerForSsh################
logging.basicConfig(level=logging.INFO)
loggerForSsh = logging.getLogger(__name__)
loggerForSsh.setLevel(logging.INFO)
handler = logging.FileHandler(SSH_LOG_FILE)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s  %(name)s  [%(levelname)s]  %(message)s")
handler.setFormatter(formatter)
loggerForSsh.addHandler(handler)


