import argparse
import json
import traceback
import warnings
from functools import partial
from multiprocessing.pool import ThreadPool

import pandas as pd
import requests
from tqdm import tqdm

from prompt_engineering.webui_utils.general_apis import judge_with_openai

ip_add = '192.168.1.248:10242'
edu_prompt_inference_url = f'http://{ip_add}/api/v1/inference/inference_edu/'
llm_inference_api = f'http://{ip_add}/api/v1/inference/inference/'
history_add_api = f'http://{ip_add}/api/v1/history/add_history/'


def edu_process(input_text, user_id, model_name='openai',
                delete_portrait_first=False, with_portrait=True, with_kw=True):
    params = {"question": input_text, 'user_id': user_id, 'model_name': model_name,
              'delete_portrait_first': delete_portrait_first,
              'with_portrait': with_portrait,
              'with_kw': with_kw}
    resp = requests.post(edu_prompt_inference_url, data=json.dumps(params), timeout=240)
    assert resp.status_code == 200, resp.content
    prompt = resp.json()["data"]
    return prompt


# 定义测试函数，调用多个不同的接口获取结果
def run_test_case(test_case_list: list, use_moss: bool, with_portrait: bool, with_kw: bool):
    ret = []
    for idx, test_case in enumerate(test_case_list):
        user_id, question, expected = test_case["id"], test_case["question"], test_case["expected"]
        if pd.isna(question):
            result = ""
            score = ""
        else:
            try:
                prompt = edu_process(question, user_id, model_name="moss" if use_moss else "openai",
                                     delete_portrait_first=idx == 0,
                                     with_portrait=with_portrait, with_kw=with_kw)
                resp = requests.post(llm_inference_api, json.dumps({"question": prompt, "temperature": 0.7}),
                                     timeout=120)
                assert resp.status_code == 200, resp.content
                result = resp.json()["data"]["output"]
            except:
                result = "未响应"
                warnings.warn(traceback.format_exc())

            score = judge_with_openai(expected, result, llm_inference_api)
            requests.post(history_add_api, json={"user_input": question, "ai_output": expected, "user_id": user_id})
        ret.append({"编号": user_id, "用例": question, "期望结果": expected, "预测结果": result, "分数": score})
    # 返回测试结果和分数
    return ret


def split_per_id(dataframes: pd.DataFrame):
    ret = []
    last_id = None
    last_id_rows = []
    for row in dataframes:
        id_, input_, target_ = row
        if not input_:
            continue
        if id_ != last_id and last_id_rows:
            ret.append(last_id_rows)
            last_id_rows = []
        last_id_rows.append({"id": row[0], "question": row[1], "expected": row[2]})
        last_id = id_
    if last_id_rows:
        ret.append(last_id_rows)
    return ret


if __name__ == '__main__':
    # 解析程序入参
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=str, help="Input CSV file path")
    parser.add_argument("output_csv", type=str, help="Output CSV file path")
    parser.add_argument("--use_moss", action="store_true", help="use moss api", required=False)
    parser.add_argument("--without_portrait", action="store_true", help="use portrait or not", required=False)
    parser.add_argument("--without_kw", action="store_true", help="whether use knowledge", required=False)
    parser.add_argument("--workers", default=2, type=int, help="worker for concurrent", required=False)
    args = parser.parse_args()
    print(args)

    # 读取测试用例csv文件
    df = pd.read_csv(args.input_csv)
    df['编号'] = df['编号'].fillna(method='ffill')
    df = df[['编号', '用例', '结果']]
    df = df.fillna("")
    df = df.to_numpy().tolist()
    test_cases = split_per_id(df)

    test_func = partial(run_test_case, use_moss=args.use_moss,
                        with_portrait=not args.without_portrait,
                        with_kw=not args.without_kw)

    # 并发执行测试用例
    ret = []
    with ThreadPool(args.workers) as pool:
        with tqdm(total=len(test_cases)) as pbar:
            for idx, result in enumerate(pool.imap(test_func, test_cases)):
                ret.extend(result)
                pbar.update()
    # write to csv
    df = pd.DataFrame(ret)
    df.to_csv(args.output_csv, index=False)
