import os
from typing import List
from commons.logger import logger
# from agents.rag.rerank import reranker
# from pymilvus import Collection, db, connections
from commons.cfg_loader import project_cfg
# from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer, util
# from commons.milvus_connector import connections
# host = milvus_cfg.get('host')
# port = milvus_cfg.get('port')
# connections.connect(host=host, port=port, db_name='default')

# embeddings = HuggingFaceEmbeddings(model_name=project_cfg.get('embedding_model'))
embeddings = SentenceTransformer(model_name_or_path=project_cfg.get('embedding_model'))
# embeddings = SentenceTransformer(model_name_or_path=os.path.join(project_cfg.get('data_mapping'), project_cfg.get('embedding_model')))

print('embedding device: ', embeddings._target_device)


# def embedding_query_emails(collection_name, question: str):
#     collection = Collection(name=collection_name)
#
#     question_embeddings = embeddings.embed_documents([question])
#
#     search_params = {
#         'metric_type': 'L2',
#         'params': {"nprobe": 10}
#     }
#
#     result = collection.search(question_embeddings, 'embeddings', search_params,
#                                limit=project_cfg.get('embedding_query_limit'),
#                                output_fields=['questions', 'answers'])
#
#     hits = result
#     rerank_candidates_q = [] # [q1, q2, ...]
#     rerank_candidates_qa = {} # {question: answer}
#     for hit in hits:
#         for h in hit:
#             question = h.entity.get('questions')
#             answer = h.entity.get('answers')
#             rerank_candidates_q.append(question)
#             rerank_candidates_qa[question] = answer
#
#     most_similar_question = reranker.rerank(question, rerank_candidates_q)
#     return most_similar_question, rerank_candidates_qa[most_similar_question]


# def embedding_query_scripts(collection_name, question: str):
#     db.using_database('script')
#     collection = Collection(name=collection_name)
#
#     question_embeddings = embeddings.embed_documents([question])
#
#     search_params = {
#         'metric_type': 'L2',
#         'params': {"nprobe": 10}
#     }
#
#     result = collection.search(question_embeddings, 'embeddings', search_params,
#                                limit=project_cfg.get('embedding_query_limit'),
#                                output_fields=['questions', 'answers'])
#
#     hits = result
#     rerank_candidates_q = [] # [q1, q2, ...]
#     rerank_candidates_qa = {} # {question: answer}
#     for hit in hits:
#         for h in hit:
#             question = h.entity.get('questions')
#             answer = h.entity.get('answers')
#             rerank_candidates_q.append(question)
#             rerank_candidates_qa[question] = answer
#
#     most_similar_question = reranker.rerank(question, rerank_candidates_q)
#     return most_similar_question, rerank_candidates_qa[most_similar_question]


def email_product_embeddings(email: str, *product_names):
    max_score = -1
    result = ''
    for product_name in product_names:
        similarity = calculate_similarity(email, product_name)
        if similarity > max_score:
            result = product_name
    # print('result: ', result)
    return result


def calculate_similarity(email: str, product_name: str) -> float:
    email_embedding = embeddings.encode(email, convert_to_tensor=True)
    product_name_embedding = embeddings.encode(product_name, convert_to_tensor=True)
    if email_embedding.get_device() != product_name_embedding.get_device():
        email_embedding.to(device='cpu')
        product_name_embedding.to(device='cpu')
        print('embeddings devices: ', email_embedding.get_device(), product_name_embedding.get_device())
    score = util.pytorch_cos_sim(email_embedding, product_name_embedding)
    return score


if __name__ == '__main__':
    # a, b = embedding_query_scripts('MH', 'can you ship to my place? ')
    # print(a, '\n==========', b)
    # calculate_similarity('das ist guagua', 'alles gute lala')
    email_collection = email_product_embeddings('i feel dizzy after wearing this for over an hour.', 'reading glasses', 'mosqito dispeller')