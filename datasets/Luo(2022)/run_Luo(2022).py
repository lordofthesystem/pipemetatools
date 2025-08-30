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
#autor é o nome do diretório
autor=os.path.basename(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(path_dataset, exist_ok=True)
os.makedirs(path_result, exist_ok=True)

from util.util import Logger
logger = Logger("logs/saida.log")
logger.log(f"Iniciando execução {autor}")

#Download do dataset original ZIP
#zip_url = 'https://www.science.org/doi/suppl/10.1126/science.ado6670/suppl_file/science.ado6670_data_s1_to_s4.zip'
#download_and_unzip(path_dataset, zip_url,'https://www.science.org/doi/10.1126/science.ado6670')


logger.log(f"Abriando arquivos")

#Dataset file name
dataset='SPENCER_Validated_peptide_info.txt' 
dataset=os.path.join(path_dataset, dataset)
dataset_s2='SPENCER_Transcript_info.txt' 
dataset_s2=os.path.join(path_dataset, dataset_s2)
dataset_s3='SPENCER_Transcript_sequence.txt' 
dataset_s3=os.path.join(path_dataset, dataset_s3)

#read the file (excel, csv or txt)
pd_dataset = pd.read_csv(dataset, sep='\t',dtype=str)
pd_dataset_s2 = pd.read_csv(dataset_s2, sep='\t',dtype=str)
pd_dataset_s3 = pd.read_csv(dataset_s3, sep='\t',dtype=str)
#pd_dataset = pd.read_csv(dataset_path, sep=",")
#pd_dataset = pd.read_csv(dataset_path, sep="\t")


#join the two files by the same ord_id between them
pd_dataset_s2["associated_orf_id_list"] = pd_dataset_s2["orf_id"].str.split(",")
pd_dataset_s2_exp = pd_dataset_s2.explode("associated_orf_id_list")
pd_dataset_s2_exp["associated_orf_id_list"] = pd_dataset_s2_exp["associated_orf_id_list"].str.strip()
pd_dataset["orf_id_list"] = pd_dataset["orf_id"].str.split(",")
pd_dataset_exp = pd_dataset.explode("orf_id_list")
pd_dataset_exp["orf_id_list"] = pd_dataset_exp["orf_id_list"].str.strip()
cols_to_add = [
    "rnacentral_id",
    "description",
    "rna_type",
    "transcript_length(nt)",
    "chromosome",
    "strand",
    "start_position",
    "end_position"
]


del pd_dataset_s2

logger.log("Convertendo orf_id_list para category")
pd_dataset_exp["orf_id_list"] = pd_dataset_exp["orf_id_list"].astype("category")
pd_dataset_s2_exp["associated_orf_id_list"] = pd_dataset_s2_exp["associated_orf_id_list"].astype("category")

logger.log(f"Passo 1")
df_merged_exp = pd_dataset_exp.merge(
    pd_dataset_s2_exp[["associated_orf_id_list"] + cols_to_add],
    left_on="orf_id_list",
    right_on="associated_orf_id_list",
    how="left",
    sort=False
)


logger.log(f"Passo 2")

agg_funcs = {
    col: (lambda s: ";".join(map(str, s.dropna().unique())) if len(s.dropna()) > 0 else "")
    for col in cols_to_add
}

# Retorna um booleano se cada índice é duplicado
dupes = df_merged_exp.index.duplicated()

# Mostra apenas os índices duplicados
print(df_merged_exp.index[dupes])
logger.log(f"Passo 3")

df_merged_exp.index = pd.Categorical(df_merged_exp.index)
logger.log(f"Passo 3.1")

df_agg = (
    df_merged_exp
    .groupby(df_merged_exp.index)
    .agg(agg_funcs)
)


logger.log(f"Passo 4")


df_result = (
    pd_dataset
    .join(df_agg, how="left")
    .drop(columns=["orf_id_list"])
)


logger.log(f"Passo 5")
orig_cols = list(pd_dataset.columns)
final_cols = []
for c in orig_cols:
    final_cols.append(c)
    if c == "peptide_id":
        final_cols += cols_to_add
final_cols = [c for c in final_cols if c in df_result.columns]
pd_dataset_s2 = df_result[final_cols]


logger.log(f"Passo 6")
#add the nt sequences to the table
fasta_dict = {}
with open(pd_dataset_s3, 'r') as f:
    header = None
    seq_lines = []
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if header is not None:
                num = ''.join(re.findall(r'\d+', header))
                fasta_dict[num] = ''.join(seq_lines)
            header = line[1:]
            seq_lines = []
        else:
            seq_lines.append(line)
    if header is not None:
        num = ''.join(re.findall(r'\d+', header))
        fasta_dict[num] = ''.join(seq_lines)
def get_nt_sequence(pid):
    num = ''.join(re.findall(r'\d+', str(pid)))
    return fasta_dict.get(num, pd.NA)
pd_dataset_s2['nt_orf_sequence'] = pd_dataset_s2['peptide_id'].apply(get_nt_sequence)
pd_dataset_s2.to_csv(dataset_s2, sep='\t', index=False)

#join the columns
pd_dataset_s2['disease'] = pd_dataset_s2['cancer_type'].astype(str) + ';' + pd_dataset_s2['cancer_subtype'].astype(str)
pd_dataset_s2['dataset'] = pd_dataset_s2['study'].astype(str) + ';' + pd_dataset_s2['study_descriptione'].astype(str)  + ';' + pd_dataset_s2['study_pubmed'].astype(str)

#exchange RNA for ORF
pd_dataset_s2['rna_type'] = pd_dataset_s2['rna_type'].str.replace('RNA', 'ORF', regex=False)

#delete columns that will not be used
delete = ['cancer_type', 'cancer_subtype', 'log2_fold_change', 't_value', 'p_value', 'adjusted_p_value', 'instrument', 'quantification', 'validation', 'associated_ms_id']
pd_dataset_s2 = pd_dataset_s2.drop(columns=delete)

#Rename columns for unification
pd_dataset_s2_dict = {
    'description': 'coding_or_non_coding',
    'rna_type': 'orf_biotype',
    'transcript_length(nt)': 'nt_transcript_length',
    'chromosome': 'Chr',
    'strand': 'Strand',
    'start_position': 'Start',
    'end_position': 'End',
    'sequence': 'aa_orf_sequence',
    'tissue_type': 'tissue',
    'associated_transcript_id': 'transcript_id',
    'associated_gene_id': 'gene_id',
    'related_gene_name': 'gene_name',
    'validation_method': 'evidence'
}
pd_dataset_s2 = pd_dataset_s2.rename(columns=pd_dataset_s2_dict)


#include reference columns
pd_dataset_s2["Species"] = "Homo sapiens"
pd_dataset_s2["original_sequence"] = "aa;nt"
pd_dataset_s2["DOI"] = "https://doi.org/10.1093/nar/gkab822"
pd_dataset_s2["paper_title"] = "SPENCER: a comprehensive database for small peptides encoded by noncoding RNAs in cancer patients"
pd_dataset_s2["paper_link"] = "https://academic.oup.com/nar/article/50/D1/D1373/6376023"
pd_dataset_s2["paper_citation"] = autor

#creating our orf_name
#(2) author
#(2) year
#().....
orf_reference='luo22orf'
pd_dataset_s2["orf_name"] = orf_reference + "_" + (pd_dataset_s2.reset_index().index + 1).astype(str)

# Save the dataset in the path_result directory
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset_s2.to_csv(output_path, sep=',', index=False)
print("Done.")
