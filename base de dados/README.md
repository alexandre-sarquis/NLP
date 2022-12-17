# NLP - BD
A base de dados usada no curso tinha duas tabelas. Abaixo as suas definições. O RDBMS foi o postgres 14 (Enconding 'UTF8', LC_COLLATE 'en_US.UTF-8', LC_CTYPE 'en_US.UTF-8')

O dump da tabela 'TABELA_NILC_NLP_TC' é muito grande, mas basicamente são os keyedvectors do [NILC](http://nilc.icmc.usp.br/nilc/index.php/repositorio-de-word-embeddings-do-nilc) - [Word2Vec CBOW 600 dimensões](http://143.107.183.175:22980/download.php?file=embeddings/word2vec/cbow_s600.zip)
## DECISOES_NLP_TC
Esta tabela está anexa - exp_decisoes_nlp_tc.csv

encoding = utf8

OID - não

HEADER - não

separador - ;

Quote - "

escape - '

```
"C:\\Program Files\\PostgreSQL\\12\\bin\\psql.exe" --command " "\\copy public.decisoes_nlp_tc (id_decisao, vc_processo, it_documento, vc_arquivo, it_arquivo, vc_caminho, dt_autuacao, vc_status, it_exercicio, cd_ambito, vc_classe, vc_resultado, vc_relator, vl_valor, cd_doc_contratante, cd_doc_contratada, vc_contratante, vc_contratada, tx_plain_text, vt_norm_vet, js_tf, tsv_plain_text) TO 'D:/Users/Alexandre/Documents/exp_decisoes_nlp_tc.csv' DELIMITER ';' CSV ENCODING 'UTF8' QUOTE '\"' ESCAPE '''';""
```


## DDL
```
CREATE TABLE public.tabela_nilc_nlp_tc
(
    id_index integer NOT NULL DEFAULT nextval('tabela_nilc_nlp_tc_id_index_seq'::regclass),
    vc_palavra character varying(100) COLLATE pg_catalog."default",
    vt_norm_vet double precision[],
    dp_norma_vet double precision,
    CONSTRAINT tabela_nilc_nlp_tc_pkey PRIMARY KEY (id_index)
);

CREATE TABLE public.decisoes_nlp_tc
(
    id_decisao integer NOT NULL DEFAULT nextval('decisoes_nlp_tc_id_decisao_seq'::regclass),
    vc_processo character varying(20) COLLATE pg_catalog."default",
    it_documento integer,
    vc_arquivo character varying(250) COLLATE pg_catalog."default",
    it_arquivo integer,
    vc_caminho character varying(100) COLLATE pg_catalog."default",
    dt_autuacao date,
    vc_status character varying(15) COLLATE pg_catalog."default",
    it_exercicio integer,
    cd_ambito character varying(5) COLLATE pg_catalog."default",
    vc_classe character varying(150) COLLATE pg_catalog."default",
    vc_resultado character varying(400) COLLATE pg_catalog."default",
    vc_relator character varying(20) COLLATE pg_catalog."default",
    vl_valor numeric,
    cd_doc_contratante character varying(20) COLLATE pg_catalog."default",
    cd_doc_contratada character varying(20) COLLATE pg_catalog."default",
    vc_contratante character varying(250) COLLATE pg_catalog."default",
    vc_contratada character varying(250) COLLATE pg_catalog."default",
    tx_plain_text text COLLATE pg_catalog."default",
    vt_norm_vet double precision[],
    js_tf jsonb,
    tsv_plain_text tsvector,
    CONSTRAINT decisoes_nlp_tc_pkey PRIMARY KEY (id_decisao)
);

 CREATE INDEX DECISOES_NLP_TC_IDX ON DECISOES_NLP_TC USING GIN (to_tsvector('pg_catalog.portuguese', TX_PLAIN_TEXT));

CREATE OR REPLACE FUNCTION public.distanciacos(
	double precision[],
	double precision[])
    RETURNS double precision
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    
AS $BODY$
DECLARE 
DOT_PRODUCT_1_2 DOUBLE PRECISION;
NORM_1 DOUBLE PRECISION;
NORM_2 DOUBLE PRECISION;
BEGIN
    DOT_PRODUCT_1_2 := 0;
    NORM_1 := 0;
    NORM_2 := 0;

    FOR i IN 1..600 LOOP
        DOT_PRODUCT_1_2 := DOT_PRODUCT_1_2 + ($1[i] * $2[i]);
    END LOOP;

    FOR i IN 1..600 LOOP
        NORM_1 := NORM_1 + pow($1[i], 2);
    END LOOP;

    NORM_1 := sqrt(NORM_1);

    FOR i IN 1..600 LOOP
        NORM_2 := NORM_2 + pow($2[i], 2);
    END LOOP;

    NORM_2 := sqrt(NORM_2);

    RETURN DOT_PRODUCT_1_2 / (NORM_1 * NORM_2);
END;
$BODY$;

CREATE OR REPLACE FUNCTION public.distancial2(
	double precision[],
	double precision[])
    RETURNS double precision
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    
AS $BODY$
DECLARE 
DIF  DOUBLE PRECISION ARRAY[600];
NORM DOUBLE PRECISION;
BEGIN
    NORM := 0;

    FOR i IN 1..600 LOOP
        NORM := NORM + pow($1[i]-$2[i], 2);
    END LOOP;

    NORM := sqrt(NORM);

    RETURN NORM;
END;
$BODY$;
```
