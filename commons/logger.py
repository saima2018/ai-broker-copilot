import os
import sys
import time
from loguru import logger

from commons.cfg_loader import project_cfg

log_path = project_cfg.log_path
os.makedirs(log_path, exist_ok=True)

log_path_all = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_log.log')
log_path_error = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_error.log')

# 日志简单配置
# 具体其他配置 可自行参考 https://github.com/Delgan/loguru
fmt = project_cfg.log_format
logger.remove()
logger.add(log_path_all, rotation=project_cfg.log_rotation, retention=project_cfg.log_retention,
           enqueue=True, format=fmt)
logger.add(log_path_error, rotation=project_cfg.log_rotation, retention=project_cfg.log_retention,
           enqueue=True, level='ERROR', format=fmt)  # 日志等级分割
logger.add(sys.stderr, level="ERROR", format=fmt)
logger.add(sys.stdout, level="INFO", format=fmt)
# format 参数： {time} {level} {message}、  {time:YYYY-MM-DD at HH:mm:ss} | {level} | {message} 记录参数
# level 日志等级
# rotation 参数：1 week 一周、00:00每天固定时间、 500 MB 固定文件大小
# retention 参数： 10 days 日志最长保存时间
# compression 参数： zip 日志文件压缩格式
# enqueue 参数 True 日志文件异步写入
# serialize 参数： True 序列化json
# encoding 参数： utf-8 字符编码、部分情况会出现中文乱码问题
# 可通过等级不同对日志文件进行分割储存
