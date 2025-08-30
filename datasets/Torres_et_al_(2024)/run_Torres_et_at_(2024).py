import pandas as pd
import os

path_dataset='dataset'
path_result = '../../metadata/'
#autor é o nome do diretório
autor=os.path.basename(os.path.dirname(os.path.abspath(__file__)))

#Nome do arquivo dataset
dataset='Torres-et-al.2024_DataS1.xlsx' 
dataset_path=os.path.join(path_dataset, dataset)

#ler o arquivo (excel, cvs ou txt)
pd_dataset = pd.read_excel(dataset_path, sheet_name="Sheet1")
#pd_dataset = pd.read_csv(dataset_path, sep="\t",dtype=str)

#Tipo de entrada
pd_dataset['coding'] = 'Coding'

#Rename columns for unification
column_dict = {'Protein Length': 'aa_orf_length',
                      'DNA sequence'  : 'nt_orf_sequence',
                      'Protein Sequence': 'aa_orf_sequence',
                      'Body sites': 'Body site',
                      'Classification of representative': 'representative_organism'}
pd_dataset = pd_dataset.rename(columns=column_dict)


#deletar colunas que não serão usadas
del pd_dataset['Cluster ID']
del pd_dataset['Number of members in Family']
del pd_dataset['Ampep Score']
del pd_dataset['Is part of 4k families']
del pd_dataset['Cluster Representative']
del pd_dataset['Refseq Homologs']
del pd_dataset['Full domain']
del pd_dataset['Partial domain']

#incluir colunas de referência
pd_dataset["DOI"] = '10.1016/j.cell.2024.07.027'
pd_dataset["paper_title"] = 'Mining human microbiomes reveals an untapped source of peptide antibiotics'
pd_dataset["paper_link"] = 'https://www.cell.com/cell/fulltext/S0092-8674(24)00802-X'
pd_dataset["paper_citation"] = "Torres_et_al_(2024)"

#criando nosso orf_name
#(2) autor
#(2) ano
#().....
orf_reference='tr24microbiomeriboseqorf'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)



# Salvar o dataset no diretório do path_result
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")