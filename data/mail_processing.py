from typing import List
import pandas as pd
from commons.cfg_loader import email_cfg
import re


def mail_cleaning(text) -> str:
    text = text.rsplit('Original Message', 1)[0]
    text = text.rsplit('（以上内容', 1)[0]
    text = text.rsplit('Sent from ', 1)[0]
    text = re.sub(r'\n{3,', '\n\n', text)
    return text


def intention_statistics(file_path):
    # df = pd.read_csv(file_path)
    df = pd.read_excel(file_path)
    print(df.head())


def preprocessing_step1(file_path):
    """从客服原始excel中提取相关信息，获取每轮邮件的首次问答"""
    df = pd.read_excel(file_path, usecols=['任务ID','业务组', '语言', '分类标签名','邮件类型', '发件箱', '发件时间', '主题', '正文（纯文本无引用）'])
    df['发件时间'] = pd.to_datetime(df['发件时间'], errors='coerce')
    df = df.dropna(subset=['发件时间'])

    # Split the DataFrame into two based on 'type' values
    df_accept = df[df['邮件类型'] == 'accept']
    df_send = df[df['邮件类型'] == 'send']

    # Group by 'id' and find the earliest 'time' for each group
    earliest_accept = df_accept.loc[df_accept.groupby('任务ID')['发件时间'].idxmin()]
    earliest_send = df_send.loc[df_send.groupby('任务ID')['发件时间'].idxmin()]

    output = pd.concat([earliest_accept, earliest_send]).sort_values(by='任务ID')
    return output


def preprocessing_step2(file_paths: List[str], output_path: str):
    df = pd.DataFrame()
    for file_path in file_paths:
        df_new = pd.read_excel(file_path)
        df_new = df_new[df_new['分类标签名'].isin(email_cfg.get('tags'))]
        df_new = df_new[df_new['业务组'].isin(email_cfg.get('business_units'))]
        df = pd.concat([df, df_new])

    ids_with_nulls = df[df['正文（纯文本无引用）'].isnull()]['任务ID'].unique()
    df = df[~df['任务ID'].isin(ids_with_nulls)]
    df = df.rename({'正文（纯文本无引用）':'正文'}, axis=1)

    # check for both accept and send types present
    df = df.groupby('任务ID').filter(check_accept_send)
    df.to_excel(output_path, index=False)


def check_accept_send(group):
    types = set(group['邮件类型'])
    return 'accept' in types and 'send' in types


if __name__ == '__main__':
    # file_path = r"D:\datasets\mail_new\august_excel.xlsx"
    # df = preprocessing_step1(file_path)
    # df.to_excel(r"D:\datasets\mail_new\august_processed.xlsx", index=False)

    file_paths = [r"D:\datasets\mail_new\july_processed.xlsx",
                  r"D:\datasets\mail_new\august_processed.xlsx",
                  r"D:\datasets\mail_new\september_processed.xlsx"]
    preprocessing_step2(file_paths, 'df_combined.xlsx')