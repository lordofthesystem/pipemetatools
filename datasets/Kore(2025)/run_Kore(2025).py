import pandas as pd
import os
import sys
import re

# Adicionando a pasta ../../util
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from util.util import download_and_unzip

# --- Configuration ---
# Paths
path_dataset = 'dataset'
path_result = '../../metadata/'
# Kore é o nome do diretório
kore = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(path_dataset, exist_ok=True)
os.makedirs(path_result, exist_ok=True)

# Nome do arquivo dataset
dataset = 'Table S6.xlsx'
dataset_path = os.path.join(path_dataset, dataset)

# Ler o arquivo (Excel)
pd_dataset = pd.read_excel(dataset_path, header=3)

# Adicionar informações de tissue
pd_dataset["tissue"] = "Heart"

# Renomear colunas para unificação
pd_dataset_dict = {
    'Gene': 'gene_name',
    'Transcripts': 'transcript_id',
    'Protein sequence': 'aa_orf_sequence',
    'Protein length': 'aa_orf_length',
    'ORF biotype': 'orf_biotype',
    'Genomic coordinate': 'genomic_coordinates',
    'Evidence': 'evidence'
}
pd_dataset = pd_dataset.rename(columns=pd_dataset_dict)

# Deletar colunas desnecessárias
columns_to_drop = ['P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10', 'P11', 'P12', 'P13', 'P14', 'P15', 'P16', 'P17']
pd_dataset = pd_dataset.drop(columns=[col for col in columns_to_drop if col in pd_dataset.columns])

# Mapear os tipos de ORF
orf_biotype_mapping_kore = {
    "3'UTR-CDS_overlap": "doORF",
    "3'UTR": "dORF",
    "intORF": "intORF",
    "lncRNA": "lncORF",
    "lncRNA-ORF": "lncRNA",
    "Pseudogene": "pseudogene",
    "5'UTR-CDS_overlap": "uoORF",
    "5'UTR": "uORF",
    "TEC": "TEC",
    "Antisense-lncRNA": "antisense",
    "Intergenic-lncRNA": "lincRNA"
}
pd_dataset["orf_biotype_unified"] = pd_dataset["orf_biotype"].map(orf_biotype_mapping_kore)

# Adicionar coluna de evidência
pd_dataset['evidence'] = pd_dataset['evidence'].str.replace('|', ';')

# Detectar tipo de sequência
def detect_sequence_type(sequence):
    nucleotide_pattern = re.compile(r'^[ACGTUacgtu]+$')
    aa_one_letter = re.compile(r'^[ACDEFGHIKLMNPQRSTVWY]+$', re.IGNORECASE)
    aa_three_letters = re.compile(r'^([A-Za-z]{3})+$')

    if pd.isna(sequence):
        return 'unknown'
    elif nucleotide_pattern.match(sequence):
        return 'nt'
    elif aa_one_letter.match(sequence):
        return 'aa'
    elif aa_three_letters.match(sequence):
        return 'aa'
    else:
        return 'unknown'

pd_dataset['data_type'] = pd_dataset['aa_orf_sequence'].apply(
    lambda x: 'aa' if pd.notna(x) else 'unknown'
)

# Adicionar colunas de referência
pd_dataset["DOI"] = "https://doi.org/10.1093/gpbjnl/qzaf004"
pd_dataset["paper_title"] = "Identification of Small Open Reading Frame-encoded Proteins in the Human Genome"
pd_dataset["paper_link"] = "https://academic.oup.com/gpb/article/23/1/qzaf004/8005233"
pd_dataset["paper_citation"] = kore

#criando nosso orf_name
#(2) autor
#(2) ano
#().....
orf_reference = 'kore25orf'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)

# Salvar o dataset no diretório do path_result
output_filename = f"{kore}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")