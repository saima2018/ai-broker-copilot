import pandas as pd
from docx.opc.pkgreader import _SerializedRelationships, _SerializedRelationship
from docx.opc.oxml import parse_xml
from docx import Document
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import Docx2txtLoader
from pdf2image import convert_from_bytes
import pytesseract
import httpcore
setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')
from googletrans import Translator
translator = Translator()

from commons.cfg_loader import milvus_cfg, project_cfg

embedding_function = HuggingFaceEmbeddings(model_name=project_cfg.get('embedding_model'))

def embed_pdfs(file_path):
    loader = PyPDFLoader(file_path, extract_images=True)
    pages = loader.load_and_split()
    for page in pages:
        print('pppp', page.page_content)
        # print('ppppp', translator.translate(page.page_content, src='zh-CN').text)


    # vectordb = Chroma.from_documents(pages, embedding=embedding_function)

def docs_processing(file_path):

    def load_from_xml_v2(baseURI, rels_item_xml):
        """
        Return |_SerializedRelationships| instance loaded with the
        relationships contained in *rels_item_xml*. Returns an empty
        collection if *rels_item_xml* is |None|.
        """
        srels = _SerializedRelationships()
        if rels_item_xml is not None:
            rels_elm = parse_xml(rels_item_xml)
            for rel_elm in rels_elm.Relationship_lst:
                if rel_elm.target_ref in ('../NULL', 'NULL'):
                    continue
                srels._srels.append(_SerializedRelationship(baseURI, rel_elm))
        return srels

    _SerializedRelationships.load_from_xml = load_from_xml_v2

    document = Document(file_path)
    headings = []
    texts = []
    para = []
    for paragraph in document.paragraphs:
        if paragraph.style.name.startswith("Heading"):
            if headings:
                texts.append(para) # heading with empty para
            headings.append(paragraph.text)
            para = []
        elif 'normal' in paragraph.style.name:
            para.append(paragraph.text)
    if para or len(headings) > len(texts):
        texts.append(texts.append(para))

    for h, t in zip(headings, texts):
        if h and t:
            for s in ['）', '、', ')', '.', '①', '②', '③' ]:
                if s in h:
                    h = h.split(s)[1]
            yield h.strip(), ' '.join(s for s in t)


def create_excel(file_path, output_path):
    df = pd.DataFrame(docs_processing(file_path), columns=['intention_and_params', 'script'])
    df.to_excel(output_path, index=False)


def process_cst_qa_file(file_path, output_path):
    df = pd.read_excel(file_path)
    print(len(df))
    df = df.drop_duplicates(subset='intention_and_params', keep='last')
    print(len(df))
    df.to_excel(output_path, index=False)



if __name__ == '__main__':
    # file_path = r"D:\projects\ai_customer_email\data\展翅鹰_自由女神硬币.pdf"
    # embed_pdfs(file_path)

    file_path = r"D:\projects\ai_customer_email\data\功能爆款话术模板v2_3.docx"
    temp_path = r"D:\projects\ai_customer_email\data\功能爆款话术模板v2_3.xlsx"
    filter_path = r"D:\datasets\mail_new\data\Filter_Case_script.docx"
    filter_path_processed = r"D:\datasets\mail_new\data\Filter_Case_script_processed.xlsx"
    product_pdf = r"D:\datasets\mail_new\data\denture.pdf"

    # docs_processing(filter_path)
    # create_excel(filter_path, filter_path_processed)
    # embed_pdfs(product_pdf)
    process_cst_qa_file(r"D:\projects\ai_customer_email\data\cst_qa_scripts_.xlsx", r"D:\projects\ai_customer_email\data\cst_qa_scripts_1.xlsx")