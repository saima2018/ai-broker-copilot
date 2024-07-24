import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings

from commons.exceptions import BaseError
from commons.logger import logger
from routers import MainRoute
from commons.redis_conn import redis_conn
parameters_already_extracted = redis_conn.set('parameters_already_extracted', '{}') # clear previous states


all_routes = [
    # route   prefix    tags
    (MainRoute, "/api/v1", None),
]


class Settings(BaseSettings):
    openapi_url: str = "/openapi.json"


settings = Settings()
app = FastAPI(openapi_url=settings.openapi_url)

for route in all_routes:
    app.include_router(route[0], prefix=route[1], tags=route[2])


@app.exception_handler(BaseError)
async def bad_request_handler(request: Request, exc: BaseError):
    logger.error(f"{request.url}, 请求内容:{request.body},错误信息{exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        # exc为异常
        content={"code": exc.code, "message": exc.message},
    )


@app.get('/ping')
def health_check():
    return 200


def internet_conn_check():
    import socket
    try:
        print('net conn: ', socket.create_connection(('1.1.1.1', 53)))
    except:
        logger.error('server network error')
        print(traceback.format_exc())

if __name__ == '__main__':
    internet_conn_check()

    import uvicorn
    # 运行前添加OPENAPI_URL= 来disable docs 和 openapi.json
    # "python -m uvicorn app:app --host 0.0.0.0 --port 10240 --workers=2 --access-log --use-colors"
    uvicorn.run(app, host='0.0.0.0', port=8868, access_log=True, use_colors=True,
                ssl_certfile='./cert.pem',
                ssl_keyfile='./key.pem')
