# -*- coding: utf-8 -*-

import pandas as pd
import os
import sys
import re

# Adding the ../../util folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from util.util import download_and_unzip


# --- Configuration ---
# Paths
path_dataset = 'dataset'
path_result = '../../metadata/'
#author is the name of the directory
autor=os.path.basename(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(path_dataset, exist_ok=True)
os.makedirs(path_result, exist_ok=True)

#Download do dataset original ZIP
#zip_url = 'https://www.science.org/doi/suppl/10.1126/science.ado6670/suppl_file/science.ado6670_data_s1_to_s4.zip'
#download_and_unzip(path_dataset, zip_url,'https://www.science.org/doi/10.1126/science.ado6670')

#Dataset file name
dataset='SmProt2_LiteratureMining.txt' 
dataset=os.path.join(path_dataset, dataset)
dataset_s2='SmProt2_LiteratureMining.annotation.txt' 
dataset_s2=os.path.join(path_dataset, dataset_s2)
dataset_s3='SmProt2_MS.txt' 
dataset_s3=os.path.join(path_dataset, dataset_s3)
dataset_s4='SmProt2_human_Ribo.txt' 
dataset_s4=os.path.join(path_dataset, dataset_s4)

#read the file (excel, csv or txt)
pd_dataset = pd.read_csv(dataset, sep='\t', dtype=str)
pd_dataset_s2 = pd.read_csv(dataset_s2, sep='\t', dtype=str)
pd_dataset_s3 = pd.read_csv(dataset_s3, sep='\t')
pd_dataset_s4 = pd.read_csv(dataset_s4, sep='\t')
#pd_dataset = pd.read_csv(dataset_path, sep=",")
#pd_dataset = pd.read_csv(dataset_path, sep="\t")

#fix columns with string, int and float errors
pd_dataset.iloc[:, 4] = pd.to_numeric(pd_dataset.iloc[:, 4], errors='coerce').astype('Int64')

pd_dataset_s2['PMID'] = pd_dataset_s2['PMID'].astype(str)

col = pd_dataset_s2.iloc[:, 9].astype(str)       
col = col.replace('nan', '')                   
pd_dataset_s2.iloc[:, 9] = col

col = pd_dataset_s2.iloc[:, 11].astype(str)       
col = col.replace('nan', '')                   
pd_dataset_s2.iloc[:, 11] = col


#filter only the species Homo sapiens in the file - DATASET FILE
pd_dataset = pd_dataset[pd_dataset["Species"] == "human"]

#merge the two files by SmProtID and smPEPID
pd_dataset_s2['key'] = pd_dataset_s2.iloc[:, 1].astype(str)
pd_dataset['key'] = pd_dataset.iloc[:, 1].str.extract(r'(\d+)', expand=False)
missing = pd_dataset['key'].isna().sum()
print(f'Linhas no segundo arquivo sem valor numérico extraído: {missing}')
pd_dataset_s2 = pd.merge(
    pd_dataset_s2,
    pd_dataset,
    on='key',
    how='inner',
    suffixes=('_pd_dataset_s2', '_smprot')
)
pd_dataset_s2 = pd_dataset_s2.drop(columns=['key'])


#add evidence through the chr, start and end columns
coordenadas_ms = set(
    tuple(map(str, row)) for row in pd_dataset_s3.iloc[:, [4, 5, 6, 7]].values
)
if 'evidence' not in pd_dataset_s2.columns:
    pd_dataset_s2['evidence'] = ''
def verificar_evidence_ms(row):
    coord = tuple(map(str, row.iloc[25:29]))
    if coord in coordenadas_ms:
        if row['evidence'] == '':
            return 'MS'
        elif 'MS' not in row['evidence']:
            return row['evidence'] + ';MS'
    return row['evidence']
pd_dataset_s2['evidence'] = pd_dataset_s2.apply(verificar_evidence_ms, axis=1)
pd_dataset_s2.to_csv("arquivo_principal.txt", sep='\t', index=False, header=False)
coordenadas_ms = set(
    tuple(map(str, row)) for row in pd_dataset_s3.iloc[:, [4, 5, 6, 7]].values
)
coordenadas_ribo = set(
    tuple(map(str, row)) for row in pd_dataset_s4.iloc[:, [4, 5, 6, 7]].values
)
if 'evidence' not in pd_dataset_s2.columns:
    pd_dataset_s2['evidence'] = ''
def atualizar_evidence(row):
    coord = tuple(map(str, row.iloc[25:29]))
    evidencias = row['evidence'].split(';') if row['evidence'] else []

    if coord in coordenadas_ms and 'MS' not in evidencias:
        evidencias.append('MS')
    if coord in coordenadas_ribo and 'ribo-seq' not in evidencias:
        evidencias.append('ribo-seq')

    return ';'.join(evidencias)
pd_dataset_s2['evidence'] = pd_dataset_s2.apply(atualizar_evidence, axis=1)
pd_dataset_s2.to_csv("arquivo_principal.txt", sep='\t', index=False, header=False)

#delete the chr from the chromosome lines
pd_dataset["Chr"] = pd_dataset["Chr"].str.replace("^chr", "", regex=True)

#aa and nt size counting
pd_dataset["nt_transcript_length"] = pd_dataset["RNAseq"].str.len()
pd_dataset["aa_orf_length"] = pd_dataset["AAseq"].str.len()

#join the columns
pd_dataset_s2['evidence'] = pd_dataset_s2['experiment'].astype(str) + ';' + pd_dataset_s2['evidence'].astype(str)

#change human to Homo sapiens
pd_dataset_s2['Species'] = pd_dataset_s2['Species'].str.replace('human', 'Homo sapiens', regex=False)

#delete columns that will not be used
delete = ['Symbol', 'smPEPID', 'Throughput', 'Phenotype', 'Interaction', 'originalID', 'EnsemblGene', 'EnsemblTrans', 'refseqID', 'NONCODEGene', 'NONCODETrans', 'Synonyms', 'Blocks'   ]
pd_dataset_s2 = pd_dataset_s2.drop(columns=delete)

#Rename columns for unification
pd_dataset_s2_dict = {
    'PMID': 'dataset',
    'SmProtID': 'orf_id',
    'GeneID': 'gene_id',
    'TransID': 'transcript_id',
    'ORFType': 'orf_biotype',
    'GeneType': 'gene_biotype',
    'CellORTissue': 'tissue',
    'FuncDiscription': 'expression_group',
    'RNAseq': 'nt_orf_sequence',
    'AAseq': 'aa_orf_sequence',
    'Length': 'aa_orf_length',
    'Stop': 'End',
    'StartCodon': 'start_codon',
    'PhyloCSF_Mean': 'conservation'
}
pd_dataset_s2 = pd_dataset_s2.rename(columns=pd_dataset_s2_dict)


#include reference columns
pd_dataset_s2["original_sequence"] = "aa;nt"
pd_dataset_s2["DOI"] = "https://doi.org/10.1016/j.gpb.2021.09.002"
pd_dataset_s2["paper_title"] = "SmProt: A Reliable Repository with Comprehensive Annotation of Small Proteins Identified from Ribosome Profiling"
pd_dataset_s2["paper_link"] = "https://academic.oup.com/gpb/article/19/4/602/7230393?login=false"
pd_dataset_s2["paper_citation"] = autor

#creating our orf_name
#(2) author
#(2) year
#().....
orf_reference='li21orf'
pd_dataset_s2["orf_name"] = orf_reference + "_" + (pd_dataset_s2.reset_index().index + 1).astype(str)

# Save the dataset in the path_result directory
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset_s2.to_csv(output_path, sep=',', index=False)
print("Done.")
