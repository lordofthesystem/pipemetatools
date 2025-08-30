import pandas as pd
import os
import sys

# Adcionando a pasta ../../util
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from util.util import download_and_unzip, read_fasta_to_dataframe

# --- Configuration ---
# Paths
path_dataset = 'dataset'
path_result = '../../metadata/'
#autor é o nome do diretório
autor=os.path.basename(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(path_dataset, exist_ok=True)
os.makedirs(path_result, exist_ok=True)

#Download do dataset original ZIP
#zip_url = 'https://www.science.org/doi/suppl/10.1126/science.ado6670/suppl_file/science.ado6670_data_s1_to_s4.zip'
#download_and_unzip(path_dataset, zip_url,'https://www.science.org/doi/10.1126/science.ado6670')

#Nome do arquivo dataset
dataset='deepccp_human_mrnasorf.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset = read_fasta_to_dataframe(dataset_path)
pd_dataset['ferramenta'] = 'DeepCCP'
pd_dataset['coding'] = 'Coding'

dataset='deepccp_human_lncsorf.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_2 = read_fasta_to_dataframe(dataset_path)
pd_dataset_2['ferramenta'] = 'DeepCCP'
pd_dataset_2['coding'] = 'Non-coding'

# Unindo os datasets
pd_dataset = pd.concat([pd_dataset, pd_dataset_2], axis=0, ignore_index=True)

# Adicionar colunas derivadas da sequência
pd_dataset['aa_orf_length'] = pd_dataset['nt_orf_sequence'].str.len() // 3
pd_dataset['start_codon'] = pd_dataset['nt_orf_sequence'].str[:3]
# A coluna 'orf_biotype' precisaria ser extraída do cabeçalho do FASTA se a informação estiver lá.

#incluir colunas de referência
pd_dataset["DOI"] = 'https://doi.org/10.48550/arXiv.2009.02647'
pd_dataset["paper_title"] = 'Utilizing Citation Network Structure to Predict Citation Counts: A Deep Learning Approach'
pd_dataset["paper_link"] = 'https://arxiv.org/abs/2009.02647'
pd_dataset["paper_citation"] = autor

#criando nosso orf_name
#(2) autor
#(2) ano
#().....
orf_reference='deepccp20tools'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)

# Salvar o dataset no diretório do path_result
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")
