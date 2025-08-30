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
dataset='LncRNA_basic_information.txt' 
dataset=os.path.join(path_dataset, dataset)
dataset_s2='Peptide_basic_information.txt' 
dataset_s2=os.path.join(path_dataset, dataset_s2)

#read the file (excel, csv or txt)
pd_dataset = pd.read_csv(dataset, sep='\t')
pd_dataset_s2 = pd.read_csv(dataset_s2, sep='\t')
#pd_dataset = pd.read_csv(dataset_path, sep=",")
#pd_dataset = pd.read_csv(dataset_path, sep="\t")


#filter only the species Homo sapiens in the file - DATASET FILE
pd_dataset = pd_dataset[pd_dataset["Species"] == "Homo sapiens"]

#filter only the species Homo sapiens in the file - DATASET_s2 FILE
pd_dataset_s2 = pd_dataset_s2[pd_dataset_s2["Species"] == "Homo sapiens"]


#check ORFs smaller than 100aa - DATASET_S2 FILE
pd_dataset_s2 = pd_dataset_s2.copy()
pd_dataset_s2['ORF_length'] = pd_dataset_s2['ORF tend'] - pd_dataset_s2['ORF tstart']
pd_dataset_s2 = pd_dataset_s2[pd_dataset_s2['ORF_length'] <= 100]
pd_dataset_s2= pd_dataset_s2[pd_dataset_s2.columns]


#merge the files by adjusting the start and end
key = 'LncRNA transcript ID'
for df, name in [(pd_dataset, 'pd_dataset'), (pd_dataset_s2, 'pd_dataset_s2')]:
    if key not in df.columns:
        raise KeyError(f"Coluna '{key}' não encontrada em {name}.")
merged = pd.merge(
    pd_dataset,
    pd_dataset_s2,
    on=key,
    how='inner',
    suffixes=('_pd_dataset', '_pd_dataset_s2')
)
for col in ['Start', 'End', 'ORF tstart', 'ORF tend']:
    if col not in merged.columns:
        raise KeyError(f"Coluna '{col}' não encontrada após merge.")
    merged[col] = pd.to_numeric(merged[col], errors='coerce')
merged['ORF tstart'] = merged['Start'] + merged['ORF tstart']
merged['ORF tend'] = merged['End'] + merged['ORF tend']
pd_dataset = merged[[  # <- Aqui é salvo o dataset final
    'ORF ID_pd_dataset_s2',
    key,
    'Species_pd_dataset', 'Chr',
    'ORF tstart', 'ORF tend', 'Strand',
    'Transcript name_pd_dataset_s2', 'Transcript biotype_pd_dataset_s2',
    'Gene id_pd_dataset_s2', 'Gene name_pd_dataset_s2', 'Gene biotype_pd_dataset_s2',
    'ORF AA sequence', 'ORF NT sequence',
    'Evidences'
]].rename(columns={
    'ORF ID_pd_dataset_s2': 'ORF ID',
    'Species_pd_dataset': 'Species',
    'Transcript name_pd_dataset_s2': 'Transcript name',
    'Transcript biotype_pd_dataset_s2': 'Transcript biotype',
    'Gene id_pd_dataset_s2': 'Gene id',
    'Gene name_pd_dataset_s2': 'Gene name',
    'Gene biotype_pd_dataset_s2': 'Gene biotype'
})

#delete the chr from the chromosome lines
pd_dataset["Chr"] = pd_dataset["Chr"].str.replace("^chr", "", regex=True)

#Remove the number from the front of the evidence
pd_dataset["Evidences"] = pd_dataset["Evidences"].str.replace(r"^\d+:", "", regex=True)

#Rename columns for unification
pd_dataset_dict = {
    'ORF ID': 'orf_id',
    'LncRNA transcript ID': 'transcript_id',
    'ORF tstart': 'Start',
    'ORF tend': 'End',
    'Transcript name': 'transcript_name',
    'Transcript biotype': 'transcript_biotype',
    'Gene id': 'gene_id',
    'Gene name': 'gene_name',
    'Gene biotype': 'gene_biotype',
    'ORF AA sequence': 'aa_orf_sequence',
    'ORF NT sequence': 'nt_orf_sequence',
    'Evidences': 'evidence'
}
pd_dataset = pd_dataset.rename(columns=pd_dataset_dict)


#include reference columns
pd_dataset["original_sequence"] = "aa;nt"
pd_dataset["DOI"] = "https://doi.org/10.1093/nar/gkae905"
pd_dataset["paper_title"] = "LncPepAtlas: a comprehensive resource for exploring the translational landscape of long non-coding RNAs"
pd_dataset["paper_link"] = "https://academic.oup.com/nar/article/53/D1/D468/7831081?login=true"
pd_dataset["paper_citation"] = autor

#creating our orf_name
#(2) author
#(2) year
#().....
orf_reference='zhou24orf'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)

# Save the dataset in the path_result directory
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")
