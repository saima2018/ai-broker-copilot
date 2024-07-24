# from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
# from commons.cfg_loader import project_cfg
# from llama_index.schema import NodeWithScore, QueryBundle, TextNode
# from typing import List
# from commons.logger import logger
#
#
# class RagReranker:
#     def __init__(self):
#         self.reranker = FlagEmbeddingReranker(top_n=1,
#                                               model=project_cfg.get('rerank_model'),
#                                               use_fp16=False)
#         print('reranker device: ', self.reranker._model.device)
#
#     def rerank(self, query: str, documents: List[str]):
#         nodes = [NodeWithScore(node=TextNode(text=doc)) for doc in documents]
#         query_bundle = QueryBundle(query_str=query)
#         ranked_nodes = self.reranker._postprocess_nodes(nodes, query_bundle)
#
#         for node in ranked_nodes:
#             result = node.node.get_content()
#             # print('rerank result: ', result)
#             logger.info(result + "-> Score:" + str(node.score))
#         return result
#
#
# # reranker = RagReranker()