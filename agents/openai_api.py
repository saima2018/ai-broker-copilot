import json
import os
from openai import OpenAI, AsyncOpenAI
import requests
import aiohttp
from commons.cfg_loader import project_cfg

# client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=project_cfg.openai_api_root)
# aclient = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=project_cfg.openai_api_root)


# call openai
def get_completion_result(question: str, temperature=0.2, stream=True):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model=project_cfg.get('openai_model'),
        stream=stream
    )

    return chat_completion


async def a_get_completion_result(question: str, temperature=0.2, stream=True):
    chat_completion = await aclient.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model=project_cfg.get('openai_model'),
        stream=stream
    )
    return chat_completion


def get_request_result_jf(question: str,
                          system_prompt: str = "",
                          url=project_cfg.gpt4_jf,
                          model=project_cfg.openai_model,
                          temperature=0.7,
                          token=project_cfg.token):
    resp = requests.post(url, data=json.dumps({
                        "model": model,
                        "messages":  [
                        {
                        "role": "system",
                        "content": system_prompt
                        },
                        { "role": "user", "content": question}
                        ],
                        "temperature": temperature,
                        "token": token
                    }))
    assert resp.status_code == 200, resp.content
    return resp.json()['data']['choices'][0]['message']['content']
