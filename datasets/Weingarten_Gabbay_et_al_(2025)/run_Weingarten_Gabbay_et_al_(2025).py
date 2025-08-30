import pandas as pd
import os
import sys

# Adcionando a pasta ../../util
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from util.util import download_and_unzip

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
dataset='science.ado6670_data_s1.txt' 
dataset_path=os.path.join(path_dataset, dataset)

#ler o arquivo (excel, cvs ou txt)
#pd_dataset = pd.read_excel(dataset_path, sheet_name="Sheet1")
#pd_dataset = pd.read_csv(dataset_path, sep=",",dtype=str)
pd_dataset = pd.read_csv(dataset_path, sep="\t",dtype=str)

#Tipo de entrada
pd_dataset['coding'] = 'Coding'

#unindo datasets
pd_dataset['viral_expression'] = 'Cap-dependent translation'

dataset='science.ado6670_data_s2.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_2 = pd.read_csv(dataset_path, sep="\t",dtype=str)
pd_dataset_2['viral_expression'] = 'EMCV-IRES'

dataset='science.ado6670_data_s3.txt' 
dataset_path=os.path.join(path_dataset, dataset)
pd_dataset_3 = pd.read_csv(dataset_path, sep="\t",dtype=str)
pd_dataset_3['viral_expression'] = 'Polio-IRES'


pd_dataset = pd.concat([pd_dataset, pd_dataset_2, pd_dataset_3], axis=0, ignore_index=True)

#Rename columns for unification
pd_dataset_dict = {'orf_price_id': 'orf_id',
                            'price_start_codon': 'start_codon',
                            'ORF_type': 'orf_biotype',
                            'ORF_length_on_viral_transcript(aa)': 'aa_orf_length',
                            'ORF_seq_on_viral_transcript': 'nt_orf_sequence'}

pd_dataset = pd_dataset.rename(columns=pd_dataset_dict)


#deletar colunas que não serão usadas
del pd_dataset['oligo_index']
del pd_dataset['gb_accession_id']
del pd_dataset['oligo_type'] #Looks important but I still do not understand it
del pd_dataset['orf_start_pos_rel_cds_start_codon'] #Could maybe be useful
del pd_dataset['orf_stop_pos_rel_cds_start_codon'] #Could maybe be useful
del pd_dataset['orf_pval']
del pd_dataset['orf_fdr_pval']
del pd_dataset['reads_chx_1']
del pd_dataset['reads_ltm']
del pd_dataset['reads_ars_exp_chx_cntrl']
del pd_dataset['reads_ars_exp_chx_arsenite']
del pd_dataset['reads_chx']

#incluir colunas de referência
pd_dataset["DOI"] = '10.1126/science.ado6670'
pd_dataset["paper_title"] = 'Pan-viral ORFs discovery using massively parallel ribosome profiling'
pd_dataset["paper_link"] = 'https://www.science.org/doi/10.1126/science.ado6670'
pd_dataset["paper_citation"] = autor

#criando nosso orf_name
#(2) autor
#(2) ano
#().....
orf_reference='wg25virusriboseqorf'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)

# Salvar o dataset no diretório do path_result
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")
