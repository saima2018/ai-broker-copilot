import os
import time
from functools import cache
from typing import List

import pandas
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from commons.cfg_loader import project_cfg

# embedding_function = HuggingFaceEmbeddings(model_name=os.path.join(project_cfg.get('data_mapping'), project_cfg.get('embedding_model')))
embedding_function = HuggingFaceEmbeddings(model_name=project_cfg.get('embedding_model'))


class IntentionVectorDB:
    _instance = None
    _chroma_vectordb = None

    @staticmethod
    def getInstance():
        if IntentionVectorDB._instance == None:
            IntentionVectorDB()
        return IntentionVectorDB._instance

    def __init__(self):
        if IntentionVectorDB._instance != None:
            raise Exception("IntentionVectorDB already initialised")
        else:
            IntentionVectorDB._instance = self

    def generate_chroma_vectordb(self, collection: str, intentions: List):
        print('sub intentions to chromadb:', len(intentions))
        return Chroma.from_texts(texts=intentions, collection_name=collection, embedding=embedding_function)

    @property
    def chroma_vectordb(self):
        return self._chroma_vectordb

    def similarity_search(self, query: str, k: int):
        return self._chroma_vectordb.similarity_search(query, k=k)


chromadb = IntentionVectorDB()

@cache
def create_sub_collection(sub_intentions: List, business_unit, order_asso, payment_status, logistics_status, attachment):
    collection_name = f'{business_unit}_{order_asso}_{payment_status}_{logistics_status}_{attachment}'
    print('creating collection: ', collection_name)
    return chromadb.generate_chroma_vectordb(collection_name, sub_intentions)

# pre-create high-freq at system loading
# for bu in project_cfg.get('common_business_units'):
#     create_sub_collection(bu, 'all_statuses')
create_sub_collection('question_suggestion',
                      ['Show me my overall positions',
                       'How is AAPL.US doing recently?',
                       'How much balance do I have available?',
                       'Show me my account status.',
                       'What orders have I placed today?'] )


if __name__ == '__main__':
    current_history = 'can i place an order to buy amazon?'
    chromadb.similarity_search(current_history)