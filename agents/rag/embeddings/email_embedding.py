import traceback
import numpy as np
from typing import List
import pandas as pd
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from commons.cfg_loader import milvus_cfg, project_cfg
from langchain_community.embeddings import HuggingFaceEmbeddings

host=milvus_cfg.get('host')
port=milvus_cfg.get('port')

connections.connect(host=host, port=port, db_name='default')
# embedding_model = project_cfg.get('embedding_model')


def insert_collection_emails(questions: List, answers: List, collection_name, batch_size=100):
    print('collection_name', collection_name)
    embedding_model = HuggingFaceEmbeddings(model_name=project_cfg.get('embedding_model'))
    num_batches = 1 + len(questions)//batch_size
    print('total entries: ', len(questions))
    question_embeddings = embedding_model.embed_documents(questions)
    print('embedding finished')
    collection = create_collection_emails(collection_name)

    entities = [
        questions,
        question_embeddings,
        answers
    ]
    entities = np.asarray(entities, dtype="object")

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i+1)*batch_size, len(questions))
        batch = entities[:, start_idx:end_idx].tolist()

        print(len(batch[0]), len(batch[1]),len(batch[2]))
        try:
            insert_result = collection.insert(batch)
            collection.flush()
        except:
            print(traceback.format_exc())
        print('start index: ', start_idx , 'num entities', collection.num_entities)


def create_collection_emails(collection_name):

    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    fields = [
        FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name='questions', dtype=DataType.VARCHAR, max_length=project_cfg.get('max_len_question'), is_primary=False, description= 'The original sentences'),
        FieldSchema(name='embeddings', dtype=DataType.FLOAT_VECTOR, description='The sentence embeddings', dim=1024),
        FieldSchema(name='answers', dtype=DataType.VARCHAR, max_length=project_cfg.get('max_len_answer'), is_primary=False, description='The original answers'),
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


def ask_question_email(collection_name, question: List):
    collection = Collection(name=collection_name)
    collection.load()

    embeddings = HuggingFaceEmbeddings(model_name=project_cfg.get('embedding_model'))
    question_embeddings = embeddings.embed_documents(question)

    search_params = {
        'metric_type': 'L2',
        'params': {"nprobe": 10}
    }

    result = collection.search(question_embeddings, 'embeddings', search_params, limit=5, output_fields=['questions', 'answers'])

    hits = result
    for hit in hits:
        for h in hit:
            print('Question: ', h.entity.get('questions'), '\nAnswer: ', h.entity.get('answers'))


def prepare_milvus_data(file_path, output_path):
    df = pd.read_excel(file_path)
    accept_df = df[df['邮件类型'] == 'accept'].copy()
    send_df = df[df['邮件类型'] == 'send'].copy()
    accept_df.columns = ['任务ID', '业务组', '分类标签名', '邮件类型', '发件人', '发件时间_accept', '主题', '正文_accept']
    send_df.columns = ['任务ID', '业务组', '分类标签名', '邮件类型', '发件人', '发件时间_send', '主题', '正文_send']
    accept_df.drop(['邮件类型'], axis=1, inplace=True)
    send_df.drop(['邮件类型', '业务组', '分类标签名', '发件人', '主题'], axis=1, inplace=True)
    merged_df = pd.merge(accept_df, send_df, on='任务ID', how='inner')
    merged_df['正文_send'] = merged_df['正文_send'].astype('str')
    merged_df['正文_accept'] = merged_df['正文_accept'].astype('str')
    merged_df['正文_send'] = merged_df['正文_send'].str.slice(0, project_cfg.get('max_len_question'))
    merged_df['正文_accept'] = merged_df['正文_accept'].str.slice(0, project_cfg.get('max_len_answer'))
    merged_df['正文_send'] = merged_df['正文_send'].apply(conditional_split) # 删除邮件开头的人名
    merged_df['正文_accept'] = merged_df['正文_accept'].apply(remove_end_pattern, args=('Original Message', )) # 删除邮件末尾的 Sent from, Original Message等格式文字
    merged_df['正文_accept'] = merged_df['正文_accept'].apply(remove_end_pattern, args=('Sent from', )) # 删除邮件末尾的 Sent from, Original Message
    merged_df['正文_accept'] = merged_df['正文_accept'].apply(remove_end_pattern, args=('（以上内容', )) # 删除邮件末尾的 Sent from, Original Message
    merged_df['正文_accept'] = merged_df['正文_accept'].apply(remove_start_pattern, args=('Refund Type:', )) # 删除邮件末尾的 Sent from, Original Message
    merged_df['正文_accept'] = merged_df['正文_accept'].replace(r'^\s*$', np.nan, regex=True) # 用主题填充空白正文收件
    merged_df['正文_accept'] = merged_df['正文_accept'].fillna(merged_df['主题']) # 用主题填充空白正文收件
    merged_df.dropna(subset=['正文_accept'], inplace=True)
    merged_df.to_excel(output_path, index=False)

def read_source_and_insert_email(file_path):
    """read source data and insert into milvus"""
    df = pd.read_excel(file_path)
    units = df['业务组'].unique().tolist()

    for unit in reversed(units):
        questions = df.loc[df['业务组']==unit, '正文_accept'].tolist()
        answers = df.loc[df['业务组']==unit, '正文_send'].tolist()
        print(unit, questions[:2], answers[:2], '\n')
        insert_collection_emails(questions, answers, unit)


def conditional_split(text):
    """删除 Hi name, Dear name """
    if text[0].lower() in ['h', 'd']:
        return text.split(',', 1)[-1]
    else:
        return text

def remove_end_pattern(text, end_pattern):
    if end_pattern in text:
        return text.split(end_pattern)[0]
    else:
        return text

def remove_start_pattern(text, start_pattern):
    if start_pattern in text:
        return text.split(start_pattern, 1)[1]
    else:
        return text


if __name__ == '__main__':


    file_path = r'/data/df_single_row.xlsx'
    # prepare_milvus_data(r'D:\projects\ai_customer_email\data\df_combined.xlsx', file_path)
    insert_units_to_collections(file_path)
    # # query collection
    # question = 'what is 401k, what does it have to do with retirement?'
    # ask_question(collection_name, [question])
