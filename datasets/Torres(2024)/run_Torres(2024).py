import pandas as pd
import os
import sys
import re
from Bio import SeqIO

# Adding the folder ../../util
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from util.util import download_and_unzip

# --- Configuration ---
#Paths
path_dataset = 'dataset'
path_result = '../../metadata/'
#author is the name of directory
autor=os.path.basename(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(path_dataset, exist_ok=True)
os.makedirs(path_result, exist_ok=True)

#Download do dataset original ZIP
#zip_url = 'https://www.science.org/doi/suppl/10.1126/science.ado6670/suppl_file/science.ado6670_data_s1_to_s4.zip'
#download_and_unzip(path_dataset, zip_url,'https://www.science.org/doi/10.1126/science.ado6670')

# Dataset file name
torres_s1 = "Torres-et-al.2024_DataS1.xlsx"
torres_s1=os.path.join(path_dataset, torres_s1)

# Reading the file (excel, csv, txt)
pd_torres_s1 = pd.read_excel(torres_s1, sheet_name="Sheet1")

# Renaming columns for unification
torres_column_dict = {'Protein Length': 'aa_orf_length',
                      'DNA sequence'  : 'nt_orf_sequence',
                      'Protein Sequence': 'aa_orf_sequence',
                      'Body sites': 'Body site',
                      'Classification of representative': 'representative_organism'}
torres_s1_renamed = pd_torres_s1.rename(columns=torres_column_dict)
torres_s1_renamed

# Deleting columns that will not be used
del torres_s1_renamed['Cluster ID']
del torres_s1_renamed['Number of members in Family']
del torres_s1_renamed['Ampep Score']
del torres_s1_renamed['Is part of 4k families']
del torres_s1_renamed['Cluster Representative']
del torres_s1_renamed['Refseq Homologs']
del torres_s1_renamed['Full domain']
del torres_s1_renamed['Partial domain']
torres_s1_renamed

# Including reference columns
torres_s1_renamed["DOI"] = '10.1016/j.cell.2024.07.027'
torres_s1_renamed["paper_title"] = 'Mining human microbiomes reveals an untapped source of peptide antibiotics'
torres_s1_renamed["paper_link"] = 'https://www.cell.com/cell/fulltext/S0092-8674(24)00802-X'
torres_s1_renamed["paper_citation"] = "Torres_et_al_(2024)"

# Creating orf_name
torres_s1_renamed["orf_name"] = "tr24microbiomeriboseqorf" + (torres_s1_renamed.reset_index().index + 1).astype(str)

# Saving the dataset to the path_result directory
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
torres_s1_renamed.to_csv(output_path, sep=',', index=False)
print("Done.")