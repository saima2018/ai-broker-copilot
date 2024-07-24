import traceback
import numpy as np
from typing import List
import pandas as pd
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from commons.cfg_loader import milvus_cfg, project_cfg
from langchain_community.embeddings import HuggingFaceEmbeddings

host=milvus_cfg.get('host')
port=milvus_cfg.get('port')

connections.connect(host=host, port=port, db_name='pdf')
# embedding_model = project_cfg.get('embedding_model')


def create_collection_pdfs(collection_name):

    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    fields = [
        FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name='embeddings', dtype=DataType.FLOAT_VECTOR, description='page text embeddings', dim=1024),
        FieldSchema(name='text', dtype=DataType.VARCHAR, max_length=project_cfg.get('max_len_answer'), is_primary=False, description='The original text'),
    ]
    schema = CollectionSchema(fields, f'{collection_name} collection')
    collection = Collection(name=collection_name, schema=schema)

    index_params = {
        'metric_type': 'L2',
        'index_type': "IVF_FLAT",
        'params': {"nlist": 1536}
    }
    collection.create_index(field_name="embeddings", index_params=index_params)
    collection.load()
    return collection


def insert_collection_pdfs(pages: List[str], collection_name, batch_size=10):
    print('collection_name', collection_name)
    embedding_model = HuggingFaceEmbeddings(model_name=project_cfg.get('embedding_model'))
    num_batches = 1 + len(pages)//batch_size
    page_embeddings = embedding_model.embed_documents(pages)
    print('embedding finished')
    collection = create_collection_pdfs(collection_name)

    entities = [
        page_embeddings,
        pages
    ]
    entities = np.asarray(entities, dtype="object")

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i+1)*batch_size, len(pages))
        batch = entities[:, start_idx:end_idx].tolist()

        print(len(batch[0]), len(batch[1]),len(batch[2]))
        try:
            insert_result = collection.insert(batch)
            collection.flush()
        except:
            print(traceback.format_exc())
        print('start index: ', start_idx , 'num entities', collection.num_entities)
