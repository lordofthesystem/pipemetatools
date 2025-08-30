import pandas as pd
import os
import sys
import re
from Bio import SeqIO


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
dataset='meta-dataInformation.txt' 
dataset=os.path.join(path_dataset, dataset)
dataset_s2='PrimaryInformation.txt' 
dataset_s2=os.path.join(path_dataset, dataset_s2)
dataset_s3='interaction_HLA.txt' 
dataset_s3=os.path.join(path_dataset, dataset_s3)

#read the file (excel, csv or txt)
pd_dataset = pd.read_csv(dataset, sep='\t')
pd_dataset_s2 = pd.read_csv(dataset_s2, sep='\t')
pd_dataset_s3 = pd.read_csv(dataset_s3, sep='\t')
#pd_dataset = pd.read_csv(dataset_path, sep=",")
#pd_dataset = pd.read_csv(dataset_path, sep="\t")


#rename one of the columns in the s3 dataset
pd_dataset_s3.rename(columns={"Microprotein": "microprotein_id"}, inplace=True)

#add mass and Allele columns
pd_dataset = pd_dataset.merge(
    pd_dataset_s2[["microprotein_id", "mass"]],
    on="microprotein_id", how="left"
)
pd_dataset = pd_dataset.merge(
    pd_dataset_s3[["microprotein_id", "Allele"]],
    on="microprotein_id", how="left"
)
pd_dataset = pd_dataset.drop(columns=[col for col in pd_dataset.columns if col in ['mass', 'Allele']], errors='ignore')

#add evidence column based on mass and Allele
df_mass = pd_dataset_s2[["microprotein_id", "mass"]].copy()
df_allele = pd_dataset_s3[["microprotein_id", "Allele"]].copy()
pd_dataset = pd_dataset.drop(columns=[col for col in pd_dataset.columns if col in ['mass', 'Allele']], errors='ignore')
pd_dataset = pd_dataset.merge(df_mass, on="microprotein_id", how="left")
pd_dataset = pd_dataset.merge(df_allele, on="microprotein_id", how="left")
def get_evidence(row):
    tags = []
    if pd.notna(row["mass"]):
        tags.append("MS")
    if pd.notna(row["Allele"]):
        tags.append("HLA")
    return ";".join(tags)

pd_dataset["evidence"] = pd_dataset.apply(get_evidence, axis=1)


#add sequence fasta of the aa
def parse_fasta_from_dataframe(df_s4: pd.DataFrame) -> dict:
    lines = []
    for _, row in df_s4.iterrows():
        line = " ".join([str(x) for x in row if pd.notna(x)]).strip()
        line = re.sub(r"^\d+\s*", "", line)
        lines.append(line)
    fasta_dict = {}
    current_id = None
    current_seq = []
    for line in lines:
        if line.startswith(">"):
            if current_id is not None:
                fasta_dict[current_id] = "".join(current_seq)
            current_id = line[1:].strip()
            current_seq = []
        else:
            current_seq.append(re.sub(r'[^A-Za-z]', '', line))  
    if current_id and current_seq:
        fasta_dict[current_id] = "".join(current_seq)
    return fasta_dict
fasta_data = parse_fasta_from_dataframe(pd_dataset)
pd_dataset["aa_orf_sequence"] = pd_dataset["microprotein_id"].map(fasta_data)

#delete columns that will not be used
delete = ['mass', 'Allele']
pd_dataset = pd_dataset.drop(columns=delete)

#Rename columns for unification
pd_dataset_dict = {
    'microprotein_id': 'orf_id',
    'gene': 'gene_name',
    'length': 'aa_orf_length',
    'geneType': 'gene_biotype',
}
pd_dataset = pd_dataset.rename(columns=pd_dataset_dict)
# Converter a coluna para string
pd_dataset["aa_orf_sequence"] = pd_dataset["aa_orf_sequence"].astype(str)
pd_dataset.at[0, "aa_orf_sequence"] = "MLNSGRLCELLVSSGRAAVS"

#include reference columns
pd_dataset["original_sequence"] = "aa"
pd_dataset["Species"] = "Homo sapiens"
pd_dataset["DOI"] = "https://doi.org/10.1016/j.compbiomed.2024.108660"
pd_dataset["paper_title"] = "MicroProteinDB: A database to provide knowledge on sequences, structures and function of ncRNA-derived microproteins"
pd_dataset["paper_link"] = "https://www.sciencedirect.com/science/article/pii/S0010482524007455?via%3Dihub"
pd_dataset["paper_citation"] = autor

#creating our orf_name
#(2) author
#(2) year
#().....
orf_reference='liang24orf'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)

# Save the dataset in the path_result directory
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")
