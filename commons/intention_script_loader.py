import os
import traceback
from functools import cache
from typing import List
import pandas as pd

from commons.cfg_loader import project_cfg, project_path
from commons.logger import logger


class IntentionScriptLoader:
    _instance = None
    _intentions = None
    _intention_script_dict = None

    @staticmethod
    def getInstance():
        if IntentionScriptLoader._instance == None:
            IntentionScriptLoader()
        return IntentionScriptLoader._instance

    def __init__(self):
        if IntentionScriptLoader._instance != None:
            raise Exception("IntentionScriptLoader already initialised")
        else:
            IntentionScriptLoader._instance = self
            # self._intention_script_dict, self._intentions = self.get_intention_and_script()

    @cache
    def get_intention_and_script(self, input_filename=project_cfg.get('intention_script_filename')):

        df = pd.read_excel(os.path.join(project_path, 'data', input_filename))
        intentions = df['intention'].tolist()
        intention_script_df = df.fillna('')
        return intentions, intention_script_df


isd = IntentionScriptLoader()
intentions, intention_script_df = isd.get_intention_and_script()


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)

    print(len(intentions), intentions[:2])
    # print(cst_qa_df.head())
    # for col in cst_qa_df:
    #     print(cst_qa_df[col].unique().tolist())
    a = intention_script_df[intention_script_df['business_unit'].str.lower().isin(['all',''])]
    print(a)