import warnings
from typing import Callable, Optional, Union
from fastapi.routing import APIRoute
from fastapi import Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import traceback
from commons.logger import logger
import requests
import json
import os


class BaseResponse(BaseModel):
    message: str
    inference_time: float


class HeartBeatResponse(BaseResponse):
    code: int = 200
    message: str = "ok"


class ResponseWithInfTime(BaseResponse):
    start_time: str
    end_time: str
    inference_time: float


class DataContent(BaseModel):
    content: str
    intention: str
    api_resp: Union[dict, list, str]


class JFResponse(BaseModel):
    data: Union[DataContent, None]
    no: int
    message: str


class LLMInferenceResponse(ResponseWithInfTime):
    content: str
    intention: str


class VersionResponse(ResponseWithInfTime):
    version: str


class ContextIncludedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                response: Response = await original_route_handler(request)
                return response
            except Exception as e:
                warnings.warn(traceback.format_exc())
                raise e

        return custom_route_handler


def download_file(url, save_path, timeout=30, fail_frequency:int=3, is_from_data=False):
    filename = url.split('/')[-1]
    try:
        response = requests.get(url)
        with open(save_path+filename, mode="wb") as file:
            file.write(response.content)

    except Exception as e:
        logger.error(f'请求异常:{e}')
    return filename

if __name__ == '__main__':
    download_file('https://test_masai.wav', '/home/sai/Documents/llm_text_processing/MockingBird/data/samples/sample.txt')