"""
 carregador dos arquivos das decisões
 carregamos o contrato.csv para os
"""
##############################################################################################
##############################################################################################
#
# CREATE TABLE PUBLIC.DECISOES_NLP_TC
# (
#     ID_DECISAO SERIAL PRIMARY KEY,
#     VC_PROCESSO VARCHAR(20),
#     IT_DOCUMENTO INTEGER,
#     VC_ARQUIVO VARCHAR(250),
#     IT_ARQUIVO INTEGER,
#     VC_CAMINHO VARCHAR(100),
#     DT_AUTUACAO DATE,
#     VC_STATUS VARCHAR(15),
#     IT_EXERCICIO INTEGER,
#     CD_AMBITO VARCHAR(5),
#     VC_CLASSE VARCHAR(150),
#     VC_RESULTADO VARCHAR(400),
#     VC_RELATOR VARCHAR(20),
#     VL_VALOR NUMERIC,
#     CD_DOC_CONTRATANTE VARCHAR(20),
#     CD_DOC_CONTRATADA VARCHAR(20),
#     VC_CONTRATANTE VARCHAR(250),
#     VC_CONTRATADA VARCHAR(250),
#     TX_PLAIN_TEXT TEXT,
#     VT_NORM_VET DOUBLE PRECISION ARRAY[600],
#     JS_TF JSONB,
#     TSV_PLAIN_TEXT TSVECTOR)
#
# ALTER TABLE DECISOES_NLP_TC ADD TSV_PLAIN_TEXT TSVECTOR;
#
# CREATE INDEX DECISOES_NLP_TC_IDX ON DECISOES_NLP_TC USING GIN (to_tsvector('pg_catalog.portuguese', TX_PLAIN_TEXT));
#
# CREATE TABLE PUBLIC.PARAGRAFOS_DECISOES_NLP_TC
# (
#     ID_PARAGRAFO SERIAL PRIMARY KEY,
#     ID_DECISAO INTEGER,
#     IT_ORDEM INTEGER,
#     TX_PLAIN_TEXT TEXT,
#     VT_NORM_VET DOUBLE PRECISION ARRAY[600])
#
# CREATE TABLE PUBLIC.TABELA_NILC_NLP_TC
# (
#     ID_INDEX SERIAL PRIMARY KEY,
#     VC_PALAVRA VARCHAR(100),
#     VT_NORM_VET DOUBLE PRECISION ARRAY[600],
#     DP_NORMA_VET DOUBLE PRECISION)
#
# CREATE OR REPLACE FUNCTION distanciaL2(DOUBLE PRECISION ARRAY[600], DOUBLE PRECISION ARRAY[600]) RETURNS double precision
# AS $$
# DECLARE
# NORM DOUBLE PRECISION;
# BEGIN
#     NORM := 0;
#
#     FOR i IN 1..600 LOOP
#         NORM := NORM + pow($1[i]-$2[i], 2);
#     END LOOP;
#
#     NORM := sqrt(NORM);
#
#     RETURN NORM;
# END;
# $$ LANGUAGE plpgsql;
#
# CREATE OR REPLACE FUNCTION distanciaCOS(DOUBLE PRECISION ARRAY[600], DOUBLE PRECISION ARRAY[600]) RETURNS double precision
# AS $$
# DECLARE
# DOT_PRODUCT_1_2 DOUBLE PRECISION;
# NORM_1 DOUBLE PRECISION;
# NORM_2 DOUBLE PRECISION;
# BEGIN
#     DOT_PRODUCT_1_2 := 0;
#     NORM_1 := 0;
#     NORM_2 := 0;
#
#     FOR i IN 1..600 LOOP
#         DOT_PRODUCT_1_2 := DOT_PRODUCT_1_2 + ($1[i] * $2[i]);
#     END LOOP;
#
#     FOR i IN 1..600 LOOP
#         NORM_1 := NORM_1 + pow($1[i], 2);
#     END LOOP;
#
#     NORM_1 := sqrt(NORM_1);
#
#     FOR i IN 1..600 LOOP
#         NORM_2 := NORM_2 + pow($2[i], 2);
#     END LOOP;
#
#     NORM_2 := sqrt(NORM_2);
#
#     RETURN DOT_PRODUCT_1_2 / (NORM_1 * NORM_2);
# END;
# $$ LANGUAGE plpgsql;
##############################################################################################
##############################################################################################

import psycopg
from psycopg.types.json import Jsonb
import pandas as pd
import numpy as np
import os
import json
import re
import spacy
from PyPDF2 import PdfReader
from gensim.models import KeyedVectors


#onde estão os arquivos?
wdDir = 'd:/downloads/processos-pdf'

#usar o pipeline pt_udv25_portuguesebosque_trf do spacy para obter melhores lemmas
#para carregar o modelo, usar
# pip install https://huggingface.co/explosion/pt_udv25_portuguesebosque_trf/resolve/main/pt_udv25_portuguesebosque_trf-any-py3-none-any.whl
spacy.prefer_gpu()
nlp_transformer = spacy.load("pt_udv25_portuguesebosque_trf")

# vamos usar os vetores do NILC para o retriever
# escolhemos Word2Vec CBOW 600 dimensões
# http://143.107.183.175:22980/download.php?file=embeddings/word2vec/cbow_s600.zip
# http://www.nilc.icmc.usp.br/embeddings
modelNILC = KeyedVectors.load_word2vec_format(wdDir + '/cbow_s600.txt')

#leva o caminho relativo que consta do banco de dados no caminho definitivo, incluindo alteração da extensão
def obtemCaminhoLocal(caminhoRelativo):
    extensaoCerta = caminhoRelativo[:-4] + '.pdf'
    caminhoLocal = wdDir + extensaoCerta
    return caminhoLocal

#funcao para colocar em memoria a tabela de decisoes em um dicionário
def obtemDfDecisoes(conn):
    # este dataframe guardará os conjuntos ID_DECISAO, VC_PROCESSO, VC_CAMINHO
    dfDecisoes = pd.DataFrame(columns=['ID_DECISAO', 'VC_PROCESSO', 'VC_CAMINHO', 'TX_PLAIN_TEXT', 'JS_TF'])

    #primeiro carregamos
    dfDecisoes = pd.read_sql(
        'SELECT ID_DECISAO, VC_PROCESSO, VC_CAMINHO FROM PUBLIC.DECISOES_NLP_TC WHERE TX_PLAIN_TEXT IS NULL', conn)

    #depois concertamos o campo "caminho"
    dfDecisoes['vc_caminho'] = dfDecisoes['vc_caminho'].apply(obtemCaminhoLocal)
    return dfDecisoes


def obtemPlainText(caminho):
    reader = PdfReader(caminho)
    paginas = len(reader.pages)
    textoExtraido = ''
    for pagina in range(paginas):
        textoExtraido += reader.pages[pagina].extract_text() + ' '
    return textoExtraido

def lemmatizaTexto(plainText):
    #em primeiro lugar, precisamos obter os lemmas de todos os
    doc_transformer = nlp_transformer(plainText)
    for token in doc_transformer:
        plainTextLemmatizado += token.lemma_ + ' '
    return plainTextLemmatizado

#funcao para colocar em memoria os plain texts tabela de decisoes em um dicionário
def populaPlainText(conn, dfDecisoes):
    with conn.cursor() as cur:
        for i in range(dfDecisoes.shape[0]):
            try:
                dfDecisoes.iloc[i,3] = obtemPlainText(dfDecisoes.iloc[i,2]);

                cur.execute("UPDATE PUBLIC.DECISOES_NLP_TC SET TX_PLAIN_TEXT = %s WHERE ID_DECISAO = %s", \
                (dfDecisoes.iloc[i,3], str(dfDecisoes.iloc[i,0])))
            except BaseException as e:
                if i % 50 == 0:
                    print(str(e))
                conn.rollback()
            else:
                conn.commit()

            if i%50 == 0:
                print('.')

# aqui recebemos texto e um objeto gensim, e resultamos uma lista de key-value pair
def montaJsonEsparso(keyedVectors, doc, desconsideraStopWords=False):
    # vamos montar um dicionário do python onde a key é o index do keyed vector e o value é a quantidade de
    # vezes que ocorre. Se uma palavra não ocorre, não se introduz uma key para ela. Então o JSON é como
    # uma matriz esparsa. recebemos um KeyedVector do Gensim e um doc do spacy

    # contando vetores
    wordFreq = {}
    for i, token in enumerate(doc):
        if keyedVectors.has_index_for(token.text):
            if (not desconsideraStopWords) or (not token.is_stop):
                if token.text not in wordFreq:
                    wordFreq[keyedVectors.get_index(token.text)] = 0
                wordFreq[keyedVectors.get_index(token.text)] += 1

    return wordFreq

# aqui recebemos texto e um objeto gensim, e resultamos uma lista de key-value pair
def preparaTexto(text):
    # vamos devolver um texto limpo.

    # Pontuação
    punctuations = re.escape(r'!"#%\'()*+,./:;<=>?@[\\]^_`{|}~')

    #
    re_remove_brackets = re.compile(r'\{.*\}')
    re_remove_html = re.compile(r'<(\/|\\)?.+?>', re.UNICODE)
    re_transform_numbers = re.compile(r'\d', re.UNICODE)
    re_transform_emails = re.compile(r'[^\s]+@[^\s]+', re.UNICODE)
    re_transform_url = re.compile(r'(http|https)://[^\s]+', re.UNICODE)

    # outros que eu agreguei
    re_espaco_no_final = re.compile(r'[ ]+$', re.UNICODE)
    re_falso_paragrafo = re.compile(r'(?<!\.)\r\n', re.UNICODE)
    re_falso_paragrafo_2 = re.compile(r'(?<!\.)\n', re.UNICODE)
    re_duplo_espaco = re.compile(r'[ ]{2,}', re.UNICODE)

    # aspinhas.
    re_quotes_1 = re.compile(r"(?u)(^|\W)[‘’′`']", re.UNICODE)
    re_quotes_2 = re.compile(r"(?u)[‘’`′'](\W|$)", re.UNICODE)
    re_quotes_3 = re.compile(r'(?u)[‘’`′“”]', re.UNICODE)
    re_dots = re.compile(r'(?<!\.)\.\.(?!\.)', re.UNICODE)
    re_punctuation = re.compile(r'([,";:]){2},', re.UNICODE)
    re_hiphen = re.compile(r' -(?=[^\W\d_])', re.UNICODE)
    re_tree_dots = re.compile(u'…', re.UNICODE)

    # Differents punctuation patterns are used.
    re_punkts = re.compile(r'(\w+)([%s])([ %s])' %
                           (punctuations, punctuations), re.UNICODE)
    re_punkts_b = re.compile(r'([ %s])([%s])(\w+)' %
                             (punctuations, punctuations), re.UNICODE)
    re_punkts_c = re.compile(r'(\w+)([%s])$' % (punctuations), re.UNICODE)
    re_changehyphen = re.compile(u'–')
    re_doublequotes_1 = re.compile(r'(\"\")')
    re_doublequotes_2 = re.compile(r'(\'\')')
    re_trim = re.compile(r' +', re.UNICODE)

    # aplicamos tudo de uma vez
    text = text.lower()
    text = text.replace('\xa0', ' ')
    text = re_tree_dots.sub('...', text)
    text = re.sub('\.\.\.', '', text)
    text = re_remove_brackets.sub('', text)
    text = re_changehyphen.sub('-', text)
    text = re_remove_html.sub(' ', text)
    text = re_transform_numbers.sub('0', text)
    text = re_transform_url.sub('URL', text)
    text = re_transform_emails.sub('EMAIL', text)
    text = re_quotes_1.sub(r'\1"', text)
    text = re_quotes_2.sub(r'"\1', text)
    text = re_quotes_3.sub('"', text)
    text = re.sub('"', '', text)
    text = re_dots.sub('.', text)
    text = re_punctuation.sub(r'\1', text)
    text = re_hiphen.sub(' - ', text)
    text = re_punkts.sub(r'\1 \2 \3', text)
    text = re_punkts_b.sub(r'\1 \2 \3', text)
    text = re_punkts_c.sub(r'\1 \2', text)
    text = re_doublequotes_1.sub('\"', text)
    text = re_doublequotes_2.sub('\'', text)
    text = re_trim.sub(' ', text)
    text = re_espaco_no_final.sub('', text)
    text = re.sub(r'\s+$', '', text, flags=re.M)
    text = re_duplo_espaco.sub(' ', text)
    text = re_falso_paragrafo.sub(' ', text)
    text = re_falso_paragrafo_2.sub(' ', text)

    return text.strip()

def carregaVetoresBD(conn, keyedVectors):
    #carregamos os vetores na tabela
    for index, key in enumerate(keyedVectors.index_to_key):
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO PUBLIC.TABELA_NILC_NLP_TC (ID_INDEX, VC_PALAVRA) VALUES (%s, %s)", \
                            (str(index), key))
            except BaseException as e:
                if index % 50 == 0:
                    print(str(e))
                conn.rollback()
            else:
                conn.commit()

            if index%50 == 0:
                print('.', end='')

def carregaVetoresBD2(conn, keyedVectors, depuracao=False):
    #carregamos os vetores na tabela
    for index, key in enumerate(keyedVectors.index_to_key):

        # cada vez que eu tentava alguma coisa, tinha que carregas os keyedvectors de novo
        if index > 10 and depuracao:
            break

        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO PUBLIC.TABELA_NILC_NLP_TC (ID_INDEX, VC_PALAVRA) VALUES (%s, %s)", \
                            (str(index), key))

                vec = modelNILC.get_vector(key)
                cur.execute("UPDATE PUBLIC.TABELA_NILC_NLP_TC SET VT_NORM_VET = %s, DP_NORMA_VET = %s WHERE ID_INDEX = %s", \
                            (vec.tolist(), str(np.linalg.norm(vec)), str(index)))

            except BaseException as e:
                if index % 500 == 0:
                    print(str(e))
                conn.rollback()
            else:
                conn.commit()

            if index%500 == 0:
                print('.', end='')

            if index%5000 == 0:
                print('-')


def limpaPlainText(conn, depuracao=False):
    #vamos passar por todas as decisoes e vamos limpá-las
    dfDecisoes = pd.read_sql('SELECT ID_DECISAO, TX_PLAIN_TEXT FROM PUBLIC.DECISOES_NLP_TC ORDER BY ID_DECISAO', conn)

    linhas = dfDecisoes.shape[0]

    for i in range(linhas):
        if depuracao and i>10:
            break;

        with conn.cursor() as cur:
            try:
                idDecisao = dfDecisoes.iloc[i, 0]
                txPlainText = preparaTexto(dfDecisoes.iloc[i, 1])
                cur.execute("UPDATE PUBLIC.DECISOES_NLP_TC SET TX_PLAIN_TEXT = %s WHERE ID_DECISAO = %s", \
                            (txPlainText, str(idDecisao)))

            except BaseException as e:
                if i % 500 == 0:
                    print(str(e))
                conn.rollback()
            else:
                conn.commit()

            if i%500 == 0:
                print('.', end='')

            if i%5000 == 0:
                print('-')

import wordcloud
import matplotlib.pyplot as plt


# CONEXAO REMOTA
conn_remota = psycopg.connect("dbname=postgres user=postgres password=tceSP#22 port=5432 host=ec2-18-231-126-109.sa-east-1.compute.amazonaws.com")

# CONEXAO LOCAL
conn_local = psycopg.connect("dbname=postgres user=postgres password=postgres port=5433")

with psycopg.connect("dbname=postgres user=postgres password=postgres port=5433") as conn:
  with conn.cursor() as cur:
    cur.execute("""CREATE TABLE paragrafos (id serial PRIMARY KEY, ord integer, texto text,
                    vetor double precision ARRAY[%s] """, (dim_embedding))
    cur.execute("INSERT INTO paragrafos (ord, text, vetor) VALUES (%s, %s, %s)", \
                  (100, texto[100], embedding[100]))
    cur.execute("SELECT * FROM paragrafos")
    cur.fetchone()
    for record in cur:
      print(record)
    conn.commit()




