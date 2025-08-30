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

#Download do dataset original ZIP
#zip_url = 'https://www.science.org/doi/suppl/10.1126/science.ado6670/suppl_file/science.ado6670_data_s1_to_s4.zip'
#download_and_unzip(path_dataset, zip_url,'https://www.science.org/doi/10.1126/science.ado6670')



#Dataset file name
dataset='MetamORF_Hsapiens.bed' 
dataset=os.path.join(path_dataset, dataset)
dataset_s2='MetamORF_Hsapiens_nt.fasta' 
pd_dataset_s2=os.path.join(path_dataset, dataset_s2)
dataset_s3='MetamORF_Hsapiens_aa.fasta' 
pd_dataset_s3=os.path.join(path_dataset, dataset_s3)

#read the file (excel, csv or txt)
pd_dataset = pd.read_csv(dataset, sep='\t')
#pd_dataset = pd.read_csv(dataset_path, sep=",")
#pd_dataset = pd.read_csv(dataset_path, sep="\t")

#add header to columns
pd_dataset.columns = ['chrom', 'chromStart', 'chromEnd', 'name', 'score', 'strand', 'thickStart', 'thickEnd', 'itemRgb', 'blockCount', 'blockSizes', 'blockStarts']

#add the aa and nt sequences using fasta in the bed file
nt_dict = {}
biotype_dict = {}
for rec in SeqIO.parse(pd_dataset_s2, "fasta"):
    parts = rec.id.split('|')
    if len(parts) >= 2:
        orf_id = parts[1]
        biotype_dict[orf_id] = parts[0]
        nt_dict[orf_id] = str(rec.seq)
aa_dict = {
    rec.id.split('|')[1]: str(rec.seq)
    for rec in SeqIO.parse(pd_dataset_s3, "fasta")
    if '|' in rec.id
}
pd_dataset['orf_biotype']      = pd_dataset['name'].map(biotype_dict)
pd_dataset['orf_sequence_nt']  = pd_dataset['name'].map(nt_dict)
pd_dataset['orf_sequence_aa']  = pd_dataset['name'].map(aa_dict)

#delete the chr from the chromosome lines
pd_dataset["chrom"] = pd_dataset["chrom"].str.replace("^chr", "", regex=True)

#aa and nt size counting
pd_dataset["nt_transcript_length"] = pd_dataset["orf_sequence_nt"].str.len()
pd_dataset["aa_orf_length"] = pd_dataset["orf_sequence_aa"].str.len()

#delete columns that will not be used
delete = ['score', 'thickStart', 'thickEnd', 'itemRgb', 'blockCount', 'blockStarts', 'blockSizes']
pd_dataset = pd_dataset.drop(columns=delete)

#Rename columns for unification
pd_dataset_dict = {
    'chrom': 'Chr',
    'chromStart': 'Start',
    'chromEnd': 'End',
    'name': 'orf_name',
    'strand': 'Strand',
    'orf_sequence_nt': 'nt_orf_sequence',
    'orf_sequence_aa': 'aa_orf_sequence',
}
pd_dataset = pd_dataset.rename(columns=pd_dataset_dict)


#include reference columns
pd_dataset["evidence"] = "Ribo-seq; MS; computer predictions"
pd_dataset["original_sequence"] = "aa;nt"
pd_dataset["Species"] = "Homo sapiens"
pd_dataset["DOI"] = "https://doi.org/10.1093/database/baab032"
pd_dataset["paper_title"] = "MetamORF: a repository of unique short open reading frames identified by both experimental and computational approaches for gene and metagene analyses"
pd_dataset["paper_link"] = "https://academic.oup.com/database/article/doi/10.1093/database/baab032/6307706#supplementary-data"
pd_dataset["paper_citation"] = autor

#creating our orf_name
#(2) author
#(2) year
#().....
orf_reference='choteau21orf'
pd_dataset["orf_name"] = orf_reference + "_" + (pd_dataset.reset_index().index + 1).astype(str)

# Save the dataset in the path_result directory
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")
