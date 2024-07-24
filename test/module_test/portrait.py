import argparse
import traceback
import warnings
from functools import partial
from multiprocessing.pool import ThreadPool

import pandas as pd
import requests
from tqdm import tqdm

from prompt_engineering.webui_utils.general_apis import judge_with_openai

ip_add = '192.168.1.248:10240'
llm_inference_api = f'http://{ip_add}/test/llm/inference/'
single_portrait_api = f'http://{ip_add}/api/v1/portrait/get_single_portrait/'


def get_portrait(input_text: str, model_name: str = 'openai'):
    if pd.isna(input_text):
        return ""
    params = {"user_input": input_text, "soft": False, "model_name": model_name}
    try:
        resp = requests.post(single_portrait_api, json=params)
        assert resp.status_code == 200
        data = resp.json()["data"]
        return data["portrait"]
    except:
        warnings.warn(traceback.format_exc())
        return "未响应"


# 定义测试函数，调用多个不同的接口获取结果
def run_test_case(test_case, use_moss):
    # 在这里调用接口获取结果
    results = [get_portrait(test_case["question"])]
    if use_moss:
        results.append(get_portrait(test_case["question"], model_name="moss"))

    # 将结果与期望结果进行比对并计算分数
    scores = [judge_with_openai(test_case["expected"], r, llm_inference_api) for r in results]
    ret_dict = {
        "用例": test_case["question"],
        "期望结果": test_case["expected"],
        "推理结果": str(results[0]),
        "评分": scores[0]
    }
    if use_moss:
        ret_dict.update({"moss结果": str(results[1])})
        ret_dict.update({"moss评分": scores[1]})
    # 返回测试结果和分数
    return ret_dict


if __name__ == '__main__':
    # 解析程序入参
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=str, help="Input CSV file path")
    parser.add_argument("output_csv", type=str, help="Output CSV file path")
    parser.add_argument("--use_moss", action="store_true", help="use moss api", required=False)
    parser.add_argument("--workers", default=4, type=int, help="worker for concurrent", required=False)
    args = parser.parse_args()

    # 读取测试用例csv文件
    test_cases = []
    with open(args.input_csv, "r") as csv_file:
        df = pd.read_csv(csv_file).to_numpy().tolist()
        for row in df:
            test_cases.append({
                "id": row[0],
                "dim": row[1],
                "question": row[2],
                "expected": row[3]
            })

    test_func = partial(run_test_case, use_moss=args.use_moss)

    # 并发执行测试用例
    ret = []
    with ThreadPool(args.workers) as pool:
        with tqdm(total=len(test_cases)) as pbar:
            for idx, result in enumerate(pool.imap(test_func, test_cases)):
                ret.append(result)
                pbar.update()
    # write to csv
    df = pd.DataFrame(ret)
    df.to_csv(args.output_csv, index=False)


