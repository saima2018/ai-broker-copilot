import argparse
import json
import traceback
import warnings
from functools import partial
from multiprocessing.pool import ThreadPool
import pandas as pd
import pytest
from tqdm import tqdm

from agents.intention_and_params import intention_agent



def get_user_intent(customer_input, current_history):
    try:
        resp = intention_agent(customer_input, current_history)
        return resp.json()["data"]["user_intent"]
    except:
        warnings.warn(traceback.format_exc())
        return "未响应"


# 定义测试函数，调用多个不同的接口获取结果
def run_test_case(test_case):
    # 在这里调用接口获取结果
    results = [get_user_intent(test_case["question"], test_case["history"])]

    ret_dict = {
        "用例": test_case["question"],
        "期望结果": test_case["expected"],
        "推理结果": str(results[0])
    }

    return ret_dict


if __name__ == '__main__':
    # 解析程序入参
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=str, help="Input CSV file path")
    parser.add_argument("output_csv", type=str, help="Output CSV file path")
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
                "desc": row[2],
                "history": row[3],
                "question": row[4],
                "expected": row[5]
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


