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
dataset='H.sapiens_CDS-csORFs_testp.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset = read_fasta_to_dataframe(dataset_path)
pd_dataset['ferramenta'] = 'csORF-finder_CDS'
pd_dataset['coding'] = 'Coding'

dataset='H.sapiens_CDS-ncsORFs_testn.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_2 = read_fasta_to_dataframe(dataset_path)
pd_dataset_2['ferramenta'] = 'csORF-finder_CDS'
pd_dataset_2['coding'] = 'Non-coding'

dataset='H.sapiens_ncRNA-csORFs_testp.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_3 = read_fasta_to_dataframe(dataset_path)
pd_dataset_3['ferramenta'] = 'csORF-finder_ncRNA'
pd_dataset_3['coding'] = 'coding'


dataset='H.sapiens_ncRNA-ncsORFs_testn.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_4 = read_fasta_to_dataframe(dataset_path)
pd_dataset_4['ferramenta'] = 'csORF-finder_ncRNA'
pd_dataset_4['coding'] = 'noncoding'

dataset='H.sapiens_nonCDS-csORFs_testp.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_5 = read_fasta_to_dataframe(dataset_path)
pd_dataset_5['ferramenta'] = 'csORF-finder_nonCDS'
pd_dataset_5['coding'] = 'coding'

dataset='H.sapiens_nonCDS-ncsORFs_testn.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_6 = read_fasta_to_dataframe(dataset_path)
pd_dataset_6['ferramenta'] = 'csORF-finder_nonCDS'
pd_dataset_6['coding'] = 'noncoding'

# Unindo os datasets
pd_dataset = pd.concat([pd_dataset, pd_dataset_2, pd_dataset_3,pd_dataset_4,pd_dataset_5,pd_dataset_6], axis=0, ignore_index=True)

# Adicionar colunas derivadas da sequência
pd_dataset['aa_orf_length'] = pd_dataset['nt_orf_sequence'].str.len() // 3
pd_dataset['start_codon'] = pd_dataset['nt_orf_sequence'].str[:3]
# A coluna 'orf_biotype' precisaria ser extraída do cabeçalho do FASTA se a informação estiver lá.

#incluir colunas de referência
pd_dataset["DOI"] = 'https://doi.org/10.1093/bib/bbac392'
pd_dataset["paper_title"] = 'csORF-finder: an effective ensemble learning framework for accurate identification of multi-species coding short open reading frames'
pd_dataset["paper_link"] = 'https://academic.oup.com/bib/article/23/6/bbac392/6696144'
pd_dataset["paper_citation"] = autor

#criando nosso orf_name
#(2) autor
#(2) ano
#().....
orf_reference='csorf_finder22tools'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)

# Salvar o dataset no diretório do path_result
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")
