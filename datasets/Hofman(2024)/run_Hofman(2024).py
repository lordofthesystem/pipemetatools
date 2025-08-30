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
# Paths
path_dataset = 'dataset'
path_result = '../../metadata/'
#author is the name of directory
autor=os.path.basename(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(path_dataset, exist_ok=True)
os.makedirs(path_result, exist_ok=True)

# Download of the original dataset ZIP
#zip_url = 'https://www.science.org/doi/suppl/10.1126/science.ado6670/suppl_file/science.ado6670_data_s1_to_s4.zip'
#download_and_unzip(path_dataset, zip_url,'https://www.science.org/doi/10.1126/science.ado6670')

# Mapping column names to sample types
tissue_cell_name_mapping_hofman = {'Unnamed: 0': 'orf_id',
                                   'Autopsy_1': 'Medulloblastoma tissue',
                                   'Autopsy_2': 'Medulloblastoma tissue',
                                   'Autopsy_3': 'Medulloblastoma tissue',
                                   'Autopsy_4': 'Medulloblastoma tissue',
                                   'Autopsy_5': 'Medulloblastoma tissue',
                                   'CHLA-01-MED': 'CHLA-01-MED medulloblastoma cell line',
                                   'CHLA-01-MEDR': 'CHLA-01-MEDR medulloblastoma cell line',
                                   'CHLA-259': 'CHLA-259 medulloblastoma cell line',
                                   'D283MED': 'D283MED medulloblastoma cell line',
                                   'D341': 'D341 medulloblastoma cell line',
                                   'D384': 'D384 medulloblastoma cell line',
                                   'D425': 'D425 medulloblastoma cell line',
                                   'D458': 'D458 medulloblastoma cell line',
                                   'DAOY': 'D458 medulloblastoma cell line',
                                   'Med2112': 'Med2112 medulloblastoma cell line',
                                   'Med411': 'Med411 medulloblastoma cell line',
                                   'ONS76': 'ONS76 medulloblastoma cell line',
                                   'Tissue_1': 'Medulloblastoma tissue',
                                   'Tissue_2': 'Medulloblastoma tissue',
                                   'Tissue_3': 'Medulloblastoma tissue',
                                   'Tissue_4': 'Medulloblastoma tissue',
                                   'R256': 'R256 medulloblastoma cell line',
                                   'R262': 'R262 medulloblastoma cell line',
                                   'Tissue_5': 'PNET tissue',
                                   'Tissue_6': 'PNET tissue',
                                   'Tissue_7': 'Medulloblastoma tissue',
                                   'Tissue_8': 'Medulloblastoma tissue',
                                   'Tissue_9': 'Medulloblastoma tissue',
                                   'Tissue_10': 'Medulloblastoma tissue',
                                   'Tissue_11': 'Medulloblastoma tissue',
                                   'Tissue_12': 'Medulloblastoma tissue',
                                   'Tissue_13': 'Medulloblastoma tissue',
                                   'Tissue_14': 'Medulloblastoma tissue',
                                   'Tissue_15': 'Medulloblastoma tissue',
                                   'Tissue_16': 'Medulloblastoma tissue',
                                   'Tissue_17': 'Medulloblastoma tissue',
                                   'Tissue_18': 'Medulloblastoma tissue',
                                   'Tissue_19': 'Medulloblastoma tissue',
                                   'Tissue_20': 'Medulloblastoma tissue',
                                   'SUMB002': 'SUMB002 medulloblastoma cell line',
                                   'UW228': 'UW228 medulloblastoma cell line'}

# Dataset file name
hofman_tissue_ppm = 'S1_Riboseq_PPM_ORFlvl_all.csv'
hofman_tissue_ppm=os.path.join(path_dataset, hofman_tissue_ppm)

# Reading the file (excel, csv, txt)
hofman_tissue_ppm = pd.read_csv(hofman_tissue_ppm, sep=",",dtype=str)

# Applying threshold to PPM data
ppm_threshold = 1 #According to the paper (See Star Methods)
# Get only the numeric columns
cols_to_threshold = hofman_tissue_ppm.columns.difference(['Unnamed: 0'])
# Apply threshold

# Converter colunas para numéricas, transformando valores não numéricos em NaN
hofman_tissue_ppm[cols_to_threshold] = hofman_tissue_ppm[cols_to_threshold].apply(pd.to_numeric, errors='coerce')

# Substituir NaN por 0 (ou outro valor adequado)
hofman_tissue_ppm[cols_to_threshold] = hofman_tissue_ppm[cols_to_threshold].fillna(0)

hofman_tissue_ppm[cols_to_threshold] = (hofman_tissue_ppm[cols_to_threshold] >= ppm_threshold).astype(int)


# Renaming columns
hofman_sample_source_renamed = hofman_tissue_ppm.rename(columns=tissue_cell_name_mapping_hofman)
hofman_sample_source_renamed

#Group columns by new name and aggregate using logical OR (max works for 0/1)
# Exclude identifier column if present
id_col = 'orf_id'

# Separate the identifier column
if id_col in hofman_sample_source_renamed.columns:
    id_series = hofman_sample_source_renamed[[id_col]]
    data_only = hofman_sample_source_renamed.drop(columns=[id_col])
else:
    id_series = None
    data_only = hofman_sample_source_renamed

# Group by column names and take max (OR logic for binary 0/1)
hofman_sample_source_renamed_grouped = data_only.T.groupby(level=0).max().T


# Reattach ID column if it was present
if id_series is not None:
    hofman_sample_source_final = pd.concat([id_series, hofman_sample_source_renamed_grouped], axis=1)
else:
    df_final = hofman_sample_source_renamed_grouped
hofman_sample_source_final

# Condensing the information into two columns: tissue and cell_line
tissue_columns_hofman = ['Medulloblastoma tissue', 'PNET tissue']

cell_line_columns_hofman = ['CHLA-01-MEDR medulloblastoma cell line',
                            'CHLA-259 medulloblastoma cell line',
                            'D283MED medulloblastoma cell line',
                            'D341 medulloblastoma cell line',
                            'D384 medulloblastoma cell line',
                            'D458 medulloblastoma cell line',
                            'Med2112 medulloblastoma cell line',
                            'Med411 medulloblastoma cell line',
                            'ONS76 medulloblastoma cell line',
                            'R256 medulloblastoma cell line',
                            'R262 medulloblastoma cell line',
                            'SUMB002 medulloblastoma cell line',
                            'UW228 medulloblastoma cell line']

# Creates the 'tissue' column by concatenating the names of tissue columns where the value is 1
hofman_sample_source_final['tissue'] = hofman_sample_source_final.apply(lambda row: ';'.join([col for col in tissue_columns_hofman if row[col] == 1]), axis=1)
# Drop the original columns if you want
hofman_sample_source_final = hofman_sample_source_final.drop(tissue_columns_hofman, axis=1)
hofman_sample_source_final

# Creates the 'cell_line' column by concatenating the names of tissue columns where the value is 1
hofman_sample_source_final['cell_line'] = hofman_sample_source_final.apply(lambda row: ';'.join([col for col in cell_line_columns_hofman if row[col] == 1]), axis=1)
# Drop the original columns if you want
hofman_sample_source_final = hofman_sample_source_final.drop(cell_line_columns_hofman, axis=1)
hofman_sample_source_final

# Dataset file name
hofman_s1p = 'mmc2.xlsx'
hofman_s1p=os.path.join(path_dataset, hofman_s1p)

# Reading the file (excel, csv, txt)
hofman_s1p = pd.read_excel(hofman_s1p, sheet_name="Table S1P", header=2)


# Renaming columns for unification
hofman_s1p_renamed = hofman_s1p.rename(columns={'chrm': 'Chr', 'starts': 'Start', 'ends': 'End',
                                        'strand': 'Strand', 'trans': 'transcript_id',
                                        'gene': 'gene_id', 'pep': 'aa_orf_sequence'})

# Including reference columns
hofman_s1p_renamed["DOI"] = 'https://doi.org/10.1016/j.molcel.2023.12.003'
hofman_s1p_renamed["paper_title"] = 'Translation of non-canonical open reading frames as a cancer cell survival mechanism in childhood medulloblastoma'
hofman_s1p_renamed["paper_link"] = 'https://www.sciencedirect.com/science/article/pii/S1097276523010225'
hofman_s1p_renamed["paper_citation"] = "Hofman_et_al_(2024)"

# Creating orf_name
hofman_s1p_renamed["orf_name"] = "hf24riboseqorf" + (hofman_s1p_renamed.reset_index().index + 1).astype(str)

# Unifying orf_biotype
orf_biotype_mapping_hofman = {
   #old_value: new_value
    "doORF" : "doORF",
    "dORF"  : "dORF",
    "intORF": "intORF",
    "lncRNA": "lncRNA/Processed_transcript",#changed
    "uoORF" : "uoORF",
    "uORF"  : "uORF"
}

hofman_s1p_renamed["orf_biotype_unified"] = hofman_s1p_renamed["orf_biotype"].map(orf_biotype_mapping_hofman)

# Performing a left merge and filters ORFs that did not match any tissue/cell line
pd_dataset = pd.merge(hofman_s1p_renamed, hofman_sample_source_final, how='left', on='orf_id')

pd_dataset[pd_dataset['tissue'].isna()]

# Adding evidence column
pd_dataset['evidence'] = 'MS;CRISPR'

# Saving the dataset to the path_result directory
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
pd_dataset.to_csv(output_path, sep=',', index=False)
print("Done.")

