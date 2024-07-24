from typing import List
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

from commons.cfg_loader import milvus_cfg, project_cfg

embedding_function = HuggingFaceEmbeddings(model_name=project_cfg.get('embedding_model'))


def pdf_rag(query, vectordb):
    pdf_qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(api_key=os.environ['OPENAI_API_KEY'],
                                                          base_url=project_cfg.openai_api_root,
                                                          model_name=project_cfg.openai_model),
                                                   vectordb.as_retriever())

    chat_history = []
    result = pdf_qa({'question': query, 'chat_history': chat_history})
    print('Answer: ', result['answer'])


def docs_rag(input_file):
    loader = TextLoader(input_file, encoding="utf-8")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    # embedding_function = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
    db = Chroma.from_documents(docs, embedding_function)
    query = """why am i only getting one parcel. i ordered two."""
    matches = db.similarity_search(query)

    for i in range(len(matches[:3])):
        print(matches[i].page_content, '\n===========')


def text_list_rag(input_texts: List):
    # embedding_function = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
    db = Chroma.from_documents(input_texts, embedding_function)
    query = """why am i only getting one parcel. i ordered two."""
    matches = db.similarity_search(query)
    print('matches ', matches)


if __name__ == '__main__':
    file_path = r"D:\projects\ai_customer_email\data\展翅鹰_自由女神硬币.pdf"
    # docs_rag()
    query = 'i have a cabinet that is 30cm wide. can the coin fit in?'
    ll = ['hello', 'why so serious?', 'i ordered this?', 'good morgen']
    # ll_embedded = embedding_function.embed_documents(ll)
    db = Chroma.from_texts(ll, embedding_function)
    query = """why am i only getting one parcel. i ordered two."""
    matches = db.similarity_search(query, k=2)
    print('matches ', matches[0].page_content, matches[1].page_content)