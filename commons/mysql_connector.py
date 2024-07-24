import pymysql
from commons.cfg_loader import mysql_cfg

# Establish a connection to the database using the configuration
mysql_conn = pymysql.connect(
    host=mysql_cfg.get('host'),
    port=mysql_cfg.get('port'),
    user=mysql_cfg.get('user'),
    password=mysql_cfg.get('password'),
    db=mysql_cfg.get('db'),
    charset=mysql_cfg.get('charset'),
    cursorclass=pymysql.cursors.DictCursor
)
