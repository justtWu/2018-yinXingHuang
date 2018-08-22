#coding=utf-8
import logging
from config import TELNET_LOG_FILE
#########loggerForSsh################
logging.basicConfig(level=logging.INFO)
#########loggerForTelnet################
loggerForTelnet = logging.getLogger(__name__)
loggerForTelnet.setLevel(logging.INFO)
handler2 = logging.FileHandler(TELNET_LOG_FILE)
handler2.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s  %(name)s  [%(levelname)s]  %(message)s")
handler2.setFormatter(formatter)
loggerForTelnet.addHandler(handler2)
