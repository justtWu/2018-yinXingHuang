#coding=utf-8
#用于处理日志的文件
import logging
import os
#########loggerForSsh################
logging.basicConfig(level=logging.INFO)
loggerForSsh = logging.getLogger(__name__)
loggerForSsh.setLevel(logging.INFO)
handler = logging.FileHandler(os.environ["PID_FILE"])
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s  %(name)s  [%(levelname)s]  %(message)s")
handler.setFormatter(formatter)
loggerForSsh.addHandler(handler)