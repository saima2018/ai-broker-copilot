import json
import requests

from commons.cfg_loader import project_cfg
from commons.logger import logger
from agents.openai_api import get_completion_result
# from agents.openai_api import get_request_result, a_get_completion_result


# def llm_inference(question: str, *,
#                   model_name: str = 'openai',
#                   temperature: float = 0.7,
#                   top_p: float = 0.9,
#                   stream=False):
#
#     if model_name == 'local_model':
#         output = get_request_result(url=project_cfg.moss_api_root,
#                                     question=question,
#                                     temperature=temperature,
#                                     top_p=top_p)
#     else:  # openai
#         output = get_completion_result(
#             question=question,
#             temperature=temperature,
#             stream=stream
#         )
#
#     return output
#
#
# async def a_llm_inference(question: str, *,
#                   model_name: str = 'openai',
#                   temperature: float = 0.7,
#                   top_p: float = 0.5,
#                   stream=False):
#     output = await a_get_completion_result(
#             question=question,
#             temperature=temperature,
#             stream=stream
#         )
#     return output


def get_request_result_jf(question: str,
                          system_prompt: str = '',
                          url=project_cfg.gpt4_jf,
                          model=project_cfg.get('openai_model'),
                          temperature=0.5,
                          token=project_cfg.token):
    resp = requests.post(url, data=json.dumps({
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {"role": "user", "content": question}
        ],
        "temperature": temperature,
        "token": token
    }))
    assert resp.status_code == 200, resp.content
    return resp.json()['data']['choices'][0]['message']['content']