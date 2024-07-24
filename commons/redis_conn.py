import json

import redis
from commons.cfg_loader import redis_cfg


# Establish a connection to the database using the configuration
redis_conn = redis.Redis(
    host=redis_cfg.get('host'),
    port=redis_cfg.get('port'),
    password=redis_cfg.get('password'),
    decode_responses=True
)


if __name__ == '__main__':
    redis_conn.hset('p', str({'a':{'b':[1,2,3]}}))
    res = redis_conn.get('pp')
    print( res)