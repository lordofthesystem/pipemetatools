import pandas as pd
import os
import sys
import re

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
#zip_url = ''
#download_and_unzip(path_dataset, zip_url,'https://www.biorxiv.org/content/biorxiv/early/2025/07/07/2025.07.03.662928/DC1/embed/media-1.xlsx?download=true')


# Chothani 2025

chothani_2025_complementary_table_path = "Dados Chottani 2025.xlsx"
chothani_2025_complementary_table_path=os.path.join(path_dataset, chothani_2025_complementary_table_path)


chothani_2025_s2 = pd.read_excel(chothani_2025_complementary_table_path, sheet_name="Supplementary Table 2")

"""Renaming some columns to match our style"""

chothani_2025_s2 = chothani_2025_s2.rename(
    columns={'releasev45_id': 'orf_name'})


chothani_2025_s4 = pd.read_excel(chothani_2025_complementary_table_path, sheet_name="Supplementary Table 4")

chothani_2025_s4.rename(columns={'release45_id': 'orf_name'}, inplace=True)

chothani_2025 = pd.merge(chothani_2025_s2, chothani_2025_s4, on="orf_name")


"""## Renaming columns"""

chothani25_renaming_dict = {
    'legacy_names_v35_id': 'original_orf_name',
    'legacy_names_v35_orf_type': 'original_orf_biotype',
    'genomic_coordinates (1-based)': 'orf_id',
    'starts (0-based)': 'Start',
    'ends (0-based)': 'End',
    'chrm': 'Chr',
    'strand': 'Strand',
    'transcript': 'transcript_id',
    'gene_id': 'gene_id',
    'gene_name': 'gene_name',
    'orf_type': 'orf_biotype',
    'gene_biotype': 'gene_biotype',
    'orf_length (bp)': 'nt_orf_length',
    'initiation_codon': 'start_codon',
    'number_datasets' : 'number_datasets',
    'Ji_etal_2015': 'Ji_etal_2015',
    'Calviello_etal_2016': 'Calviello_etal_2016',
    'Raj_etal_2016': 'Raj_etal_2016',
    'VanHeesch_etal_2019': 'VanHeesch_etal_2019',
    'Martinez_etal_2020': 'Martinez_etal_2020',
    'Chen_etal_2020': 'Chen_etal_2020',
    'Gaertner_etal_2020': 'Gaertner_etal_2020',
    'Chothani_etal_2022':'Chothani_etal_2022',
    'Sandmann_etal_2023':'Sandmann_etal_2023',
    'all_trans':'all_trans',
    'sequence_aa':'aa_orf_sequence',
    'sequence_nt':'nt_orf_sequence',
    'sequence_aa_MS\n_ms':'sequence_aa_MS',
    'all_trans': 'all_transcripts'

}
#rename
chothani_2025_renamed = chothani_2025.rename(columns=chothani25_renaming_dict)

del chothani_2025_renamed['included_ORF_isoforms']
del chothani_2025_renamed['included_ORF_isoforms_ov90']

"""## Adding Mudge tissue information (7 papers)

4 of them are easy to add since they have only one cell line or tissue type, and the information of where each orf comes from is easily available
"""

chothani_2025_renamed['tissue_tmp'] = [set() for _ in range(len(chothani_2025_renamed))]

"""Calviello_etal_2016"""

for i in chothani_2025_renamed.index:
    if chothani_2025_renamed.loc[i, 'Calviello_etal_2016'] == 1:
        chothani_2025_renamed.loc[i, 'tissue_tmp'].add('HEK293')

chothani_2025_renamed[["Calviello_etal_2016", "tissue_tmp"]]

"""Raj_etal_2016"""

for i in chothani_2025_renamed.index:
    if chothani_2025_renamed.loc[i, 'Raj_etal_2016'] == 1:
        chothani_2025_renamed.loc[i, 'tissue_tmp'].add('HapMap lymphoblastoid cell line')

chothani_2025_renamed.loc[chothani_2025_renamed["Raj_etal_2016"] ==1][["Raj_etal_2016", "tissue_tmp"]]

"""VanHeesch_etal_2019"""

for i in chothani_2025_renamed.index:
    if chothani_2025_renamed.loc[i, 'VanHeesch_etal_2019'] == 1:
        chothani_2025_renamed.loc[i, 'tissue_tmp'].add('Heart')

chothani_2025_renamed[["VanHeesch_etal_2019", 'tissue_tmp']]

"""Gaertner_etal_2020"""

for i in chothani_2025_renamed.index:
    if chothani_2025_renamed.loc[i, 'Gaertner_etal_2020'] == 1:
        chothani_2025_renamed.loc[i, 'tissue_tmp'].add('hESC-derived pancreatic progenitors')

chothani_2025_renamed[["Gaertner_etal_2020", "tissue_tmp"]]

"""Martinez_etal_2020"""

for i in chothani_2025_renamed.index:
    if chothani_2025_renamed.loc[i, 'Martinez_etal_2020'] == 1:
        chothani_2025_renamed.loc[i, 'tissue_tmp'].update(['293T cell line', 'HeLa S3 cell line', 'K562 cell line'])

chothani_2025_renamed[["Martinez_etal_2020", "tissue_tmp"]]

"""Ji_etal_2015"""

for i in chothani_2025_renamed.index:
    if chothani_2025_renamed.loc[i, 'Ji_etal_2015'] == 1:
        chothani_2025_renamed.loc[i, 'tissue_tmp'].update(['MCF10A-ER-Src cell line', "EH cells", "EL cells", "ELR cells"])

chothani_2025_renamed[["Ji_etal_2015", "tissue_tmp"]]

"""Chen_etal_2020"""

for i in chothani_2025_renamed.index:
    if chothani_2025_renamed.loc[i, 'Chen_etal_2020'] == 1:
        chothani_2025_renamed.loc[i, 'tissue_tmp'].update(['iPSC', 'iPSC-CM cells'])

chothani_2025_renamed[["Chen_etal_2020", "tissue_tmp"]]

"""

## Adding Sandmann <16aa tissue information"""

sandmann_ls16_path = "TableS4.xlsx"
sandmann_ls16_path=os.path.join(path_dataset, sandmann_ls16_path)

sandmann_ls16_ab_cutoff = pd.read_excel(sandmann_ls16_path, sheet_name="Candidate sORFs3-15")
sandmann_ls16_below_cutoff = pd.read_excel(sandmann_ls16_path, sheet_name="sORFs3-15 below cutoff")

sandmann_ls16 = pd.concat([sandmann_ls16_ab_cutoff, sandmann_ls16_below_cutoff], axis=0, ignore_index=True)


sandmann_ls16_renamed = sandmann_ls16.rename(columns={'ORF ID\n(transcriptID_ORFstart_ORFstop)': 'orf_id',
                                                      'ORF peptide \nsequence': 'aa_orf_sequence'})


sandmann_tissue_info_path = "Sandmann_etal_2023_human_called_ncORFs3_15aa.txt"
sandmann_tissue_info_path=os.path.join(path_dataset, sandmann_tissue_info_path)

sandmann_tissue_info = pd.read_csv(sandmann_tissue_info_path, sep="\t", header=None)
sandmann_tissue_info.columns = ["orf_id", "tissue"]

sandmann_tissue_info['tissue'] = sandmann_tissue_info['tissue'].str.capitalize()


#All of them were detected on Heart tissue
# Group by 'ID' and join tissues in a list
tissue_dict = sandmann_tissue_info.groupby('orf_id')['tissue'].apply(list).to_dict()

for orf_id in tissue_dict:
  tissue_dict[orf_id].append("Heart")

sandmann_ls16_renamed['tissue'] = sandmann_ls16_renamed['orf_id'].map(tissue_dict)

sandmann_ls16_renamed['tissue_tmp_s'] = [set() for _ in range(len(sandmann_ls16_renamed))]

sandmann_ls16_renamed['evidence_tmp_s'] = [set() for _ in range(len(sandmann_ls16_renamed))]

sandmann_ls16_renamed[['Chen 2020 (CRISPR)', 'Detected in MS \n(shotgun)', 'Detected in MS \n(HLA)']]

for i in sandmann_ls16_renamed.index:
    if sandmann_ls16_renamed.loc[i, 'Chen 2020 (CRISPR)'] == 1:
        sandmann_ls16_renamed.loc[i, 'evidence_tmp_s'].add('Crispr')

for i in sandmann_ls16_renamed.index:
    if sandmann_ls16_renamed.loc[i, 'Detected in MS \n(shotgun)'] != 0:
        sandmann_ls16_renamed.loc[i, 'evidence_tmp_s'].add('MS')

for i in sandmann_ls16_renamed.index:
    if sandmann_ls16_renamed.loc[i, 'Detected in MS \n(HLA)'] != 0:
        sandmann_ls16_renamed.loc[i, 'evidence_tmp_s'].add('HLA')

for _, row in sandmann_ls16_renamed.iterrows():
    if isinstance(row["tissue"], list):
        row["tissue_tmp_s"].update(row["tissue"])

sandmann_tissue = sandmann_ls16_renamed[['aa_orf_sequence', 'tissue_tmp_s', 'evidence_tmp_s']]

sandmann_tissue.loc[:, "aa_orf_sequence"] = sandmann_tissue["aa_orf_sequence"] + "*"

chothani_2025_renamed = pd.merge(chothani_2025_renamed, sandmann_tissue, on="aa_orf_sequence", how='left')

"""## Add Chothani tissue information

Fetch:


*   smORF list
*   nucleotide sequence from [smORF website]( https://smorfs.ddnetbio.com)
*   extra information from [smORF website]( https://smorfs.ddnetbio.com)
"""

chothani_main_smorf_list_path = "1-s2.0-S1097276522006062-mmc3.xlsx"
chothani_main_smorf_list_path=os.path.join(path_dataset, chothani_main_smorf_list_path)
nucleotide_sequence_path = "download_filtered_data.csv"
nucleotide_sequence_path=os.path.join(path_dataset, nucleotide_sequence_path)
extra_website_information_path = "download_orf_coordinates_and_nucleotides_sequence.csv"
extra_website_information_path=os.path.join(path_dataset, extra_website_information_path)

chothani_main_smorf_list = pd.read_excel(chothani_main_smorf_list_path, sheet_name="smORF list")


nucleotide_sequence = pd.read_csv(nucleotide_sequence_path)
nucleotide_sequence = nucleotide_sequence.iloc[:, 1:]

nucleotide_sequence_parsed = nucleotide_sequence["iORF_id.Genomic_coordinates"].str.split(";", n=1, expand=True)
nucleotide_sequence_parsed.columns = ["iORF_id", "Genomic_coordinates"]
nucleotide_sequence_parsed["nt_seq"] = nucleotide_sequence["Sequence"]
nucleotide_sequence_parsed["Strand"] = nucleotide_sequence["Strand"]

extra_website_information = pd.read_csv(extra_website_information_path)
extra_website_information = extra_website_information.iloc[:, 1:]
#Delete redundant information already in supplementary material
del extra_website_information["PIF"]
del extra_website_information["Uniformity"]
del extra_website_information["Dropoff"]
del extra_website_information["Gene_id"]
del extra_website_information["Peptide.seq"]
del extra_website_information["Gene_name"]
del extra_website_information["All.gene.IDs"]
del extra_website_information["Start"]


chothani_main_smorf_nt_seq = pd.merge(chothani_main_smorf_list, nucleotide_sequence_parsed, how="outer", on="iORF_id")

chothani_main_smorf_nt_seq_extra = pd.merge(chothani_main_smorf_nt_seq, extra_website_information, how="outer", on="iORF_id")


chothani_main_smorf_nt_seq_extra_renamed = chothani_main_smorf_nt_seq_extra.rename(
    columns={'ORF_id': 'orf_id', 'iORF_id': 'iorf_id', 'ORF_type': 'orf_biotype',
             'Gene ID': 'gene_id', 'Gene name': 'gene_name', 'Gene type': 'gene_biotype',
             'Start codon': 'Start_codon', 'AA_sequence': 'aa_orf_sequence',
             'All gene IDs': 'all_genes', 'All gene types': 'all_gene_biotypes',
             'MS.hits': 'MS_hits', 'ORF type': 'orf_biotype'}
)

import re

def parse_coords(coord_string):
    if pd.isna(coord_string):
        return pd.Series(["", "", ""])
    exons = coord_string.split(";")
    chr_ = ";".join(sorted(set([re.match(r"^\w+", exon).group(0) for exon in exons if re.match(r"^\w+", exon)])))
    starts = ";".join([re.search(r":(\d+)-", exon).group(1) for exon in exons if re.search(r":(\d+)-", exon)])
    ends = ";".join([re.search(r"-(\d+)", exon).group(1) for exon in exons if re.search(r"-(\d+)", exon)])
    return pd.Series([chr_, starts, ends])

final_merge_chothani = chothani_main_smorf_nt_seq_extra_renamed.copy()
final_merge_chothani[["Chr", "Start", "End"]] = chothani_main_smorf_nt_seq_extra_renamed["Genomic_coordinates"].apply(parse_coords)
final_merge_chothani[["Start", "End"]]



chothani_tissue_info_path = "1-s2.0-S1097276522006062-mmc4.xlsx"
chothani_tissue_info_path=os.path.join(path_dataset, chothani_tissue_info_path)
chothani_tissue_info = pd.read_excel(chothani_tissue_info_path, sheet_name="Riboseq_TPM")

chothani_tissue_info.rename(columns={'Unnamed: 0': 'iorf_id',
                                     'Brain': 'Brain',
                                     'ES': 'hESCs',
                                     'Fat': 'Adipose tissue',
                                     'Fibroblasts': 'Primary atrial fibroblasts',
                                     'HCAEC': 'Human coronary artery endothelial cells',
                                     'HAEC': 'Human aortic endothelial cells',
                                     'Hepatocytes': 'Primary human hepatocytes',
                                     'HUVEC': "Human umbilical vein endothelial cells",
                                     'Kidney': 'Kidney',
                                     'SM': 'Skeletal Muscle', #?
                                     'VSMC': 'Vascular smooth muscle cells'}, inplace=True)

"""Transformar tpm em 0 ou 1, se maior que 1, 1"""

#Choose the column to exclude
column_to_exclude = 'iorf_id'

# Get the list of columns to modify
cols_to_modify = chothani_tissue_info.columns.difference([column_to_exclude])

# Apply changes
chothani_tissue_info[cols_to_modify] = (chothani_tissue_info[cols_to_modify] > 1).astype(int)

"""Add tissue columns to a set"""

chothani_tissue_info['tissue_tmp_c'] = [set() for _ in range(len(chothani_tissue_info))]

for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Brain'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Brain')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'hESCs'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('hESCs')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Adipose tissue'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Adipose tissue')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Primary atrial fibroblasts'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Primary atrial fibroblasts')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Human coronary artery endothelial cells'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Primary atrial fibroblasts')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Heart'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Heart')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Primary human hepatocytes'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Primary human hepatocytes')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Human umbilical vein endothelial cells'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Human umbilical vein endothelial cells')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Kidney'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Kidney')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Skeletal Muscle'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Skeletal Muscle')
for i in chothani_tissue_info.index:
    if chothani_tissue_info.loc[i, 'Vascular smooth muscle cells'] == 1:
        chothani_tissue_info.loc[i, 'tissue_tmp_c'].add('Vascular smooth muscle cells')

chothani_2022_tissue = pd.merge(final_merge_chothani, chothani_tissue_info, on="iorf_id")

chothani_2022_tissue['evidence_tmp_c'] = [set() for _ in range(len(chothani_2022_tissue))]

for i in chothani_2022_tissue.index:
    chothani_2022_tissue.loc[i, 'evidence_tmp_c'].add('Ribo-seq')

for i in chothani_2022_tissue.index:
    if chothani_2022_tissue.loc[i, 'MS_hits'] >= 1:
        chothani_2022_tissue.loc[i, 'evidence_tmp_c'].add('MS')

chothani_2022_tissue["aa_orf_sequence"] = chothani_2022_tissue["aa_orf_sequence"].str.replace(r"_$", "*", regex=True)

chothani_2022_tissue_to_be_merged = chothani_2022_tissue[['aa_orf_sequence', 'tissue_tmp_c', 'evidence_tmp_c']]

chothani_2025_renamed = pd.merge(chothani_2025_renamed, chothani_2022_tissue_to_be_merged, on="aa_orf_sequence", how='left')

"""# Deutsch High-quality MS-validated ORFs

Main information about Ribo-seq ORFs:



*   S2
*   S3
*   S4
*   S5
*   S7
*   S8
"""

deutsch_xlsm_s2_path = "media-2.xlsx"
deutsch_xlsm_s2_path=os.path.join(path_dataset, deutsch_xlsm_s2_path)
deutsch_xlsm_s3_path = "media-3.xlsx"
deutsch_xlsm_s3_path=os.path.join(path_dataset, deutsch_xlsm_s3_path)
deutsch_xlsm_s4_path = "media-4.xlsx"
deutsch_xlsm_s4_path=os.path.join(path_dataset, deutsch_xlsm_s4_path)
deutsch_xlsm_s5_path = "media-5.xlsx"
deutsch_xlsm_s5_path=os.path.join(path_dataset, deutsch_xlsm_s5_path)
deutsch_xlsm_s7_path = "media-7.xlsx"
deutsch_xlsm_s7_path=os.path.join(path_dataset, deutsch_xlsm_s7_path)
deutsch_xlsm_s8_path = "media-8.xlsx"
deutsch_xlsm_s8_path=os.path.join(path_dataset, deutsch_xlsm_s8_path)

"""Remove unnecessary columns"""

deutsch_s2 = pd.read_excel(deutsch_xlsm_s2_path, sheet_name="Table S2")


deutsch_s2.rename(columns={'Ribo-Seq_ORF': 'orf_name'}, inplace=True)
deutsch_s2["orf_name"] = deutsch_s2["orf_name"].str.extract(r"(c[A-Za-z0-9]+.*?\d+)")
deutsch_s2.drop(columns=["PeptideAtlas identifier", "chrm", "starts", "orf_biotype",
                         "ends", "strand", "transcript", "gene_id", "gene_name",
                         "gene_biotype", "sequence"], inplace=True) #Sequence is just MS fragments


deutsch_s3 = pd.read_excel(deutsch_xlsm_s3_path, sheet_name="Table S3")


deutsch_s3.rename(columns={'Ribo-Seq_ORF': 'orf_name'}, inplace=True)
deutsch_s3["orf_name"] = deutsch_s3["orf_name"].str.extract(r"(c[A-Za-z0-9]+.*?\d+)")
deutsch_s3.drop(columns=["PeptideAtlas.identifier", "chrm", "starts", "orf_biotype",
                         "ends", "strand", "transcript", "gene_id", "gene_name",
                         "gene_biotype"], inplace=True) #Sequence is just MS fragments


deutsch_s4 = pd.read_excel(deutsch_xlsm_s4_path, sheet_name="Table S4")


deutsch_s4.rename(columns={'Ribo-Seq_ORF': 'orf_name'}, inplace=True)
deutsch_s4["orf_name"] = deutsch_s4["orf_name"].str.extract(r"(c[A-Za-z0-9]+.*?\d+)")
deutsch_s4.drop(columns=["PeptideAtlas.identifier", "chrm", "starts", "orf_biotype",
                         "ends", "strand", "transcript", "gene_id", "gene_name",
                         "gene_biotype", "sequence"], inplace=True) #Sequence is just MS fragments


deutsch_s5 = pd.read_excel(deutsch_xlsm_s5_path, sheet_name="Table S5")


deutsch_s5.rename(columns={'Ribo-Seq_ORF': 'orf_name'}, inplace=True)
deutsch_s5["orf_name"] = deutsch_s5["orf_name"].str.extract(r"(c[A-Za-z0-9]+.*?\d+)")
deutsch_s5.drop(columns=["PeptideAtlas.identifier", "orf_biotype", "chrm", "starts",
                         "ends", "strand", "transcript", "gene_id", "gene_name",
                         "gene_biotype", "orf_length"], inplace=True) #Sequence is just MS fragments


deutsch_s7 = pd.read_excel(deutsch_xlsm_s7_path, sheet_name="Sheet1")


deutsch_s7["orf_name"] = deutsch_s7["orf_name"].str.extract(r"(c[A-Za-z0-9]+.*?\d+)")
deutsch_s7.drop(columns=["sequence"], inplace=True) #Sequence is just MS fragments


deutsch_s8 = pd.read_excel(deutsch_xlsm_s8_path, sheet_name="Sheet1")


deutsch_s8["orf_name"] = deutsch_s8["orf_name"].str.extract(r"(c[A-Za-z0-9]+.*?\d+)")
deutsch_s8.drop(columns=["group(d=1, u=0)", "sequence"], inplace=True) #Sequence is just MS fragments


"""Aqui só empilha"""

all_deutsch_list = [deutsch_s2, deutsch_s3, deutsch_s4, deutsch_s5, deutsch_s7, deutsch_s8]
all_deutsch = pd.concat(all_deutsch_list, ignore_index=True)


import pandas as pd
import numpy as np

def fill_missing(series):
    # Drop missing and empty strings
    valid_vals = series.dropna()
    valid_vals = valid_vals[valid_vals != ""]

    if not valid_vals.empty:
        return valid_vals.iloc[0]  # Return the first non-empty value
    else:
        return np.nan

# Apply this function across all columns, grouped by 'orf_name'
all_deutsch_collapsed = all_deutsch.groupby("orf_name", dropna=False).agg(fill_missing).reset_index()


all_deutsch_collapsed_renamed = all_deutsch_collapsed.rename(columns={'length': 'orf_length'})

all_deutsch_collapsed_renamed['evidence_tmp_d'] = [set() for _ in range(len(all_deutsch_collapsed_renamed))]

for i in all_deutsch_collapsed_renamed.index:
    if all_deutsch_collapsed_renamed.loc[i, 'n_peptides_in_entry'] >= 1:
        all_deutsch_collapsed_renamed.loc[i, 'evidence_tmp_d'].add('MS')

for i in all_deutsch_collapsed_renamed.index:
    if all_deutsch_collapsed_renamed.loc[i, 'n_hla_peptides'] >= 1:
        all_deutsch_collapsed_renamed.loc[i, 'evidence_tmp_d'].add('HLA')


all_deutsch_collapsed_renamed_to_be_merged = all_deutsch_collapsed_renamed[["orf_name", "evidence_tmp_d"]]

chothani_2025_renamed = pd.merge(chothani_2025_renamed, all_deutsch_collapsed_renamed_to_be_merged, left_on="original_orf_name", right_on="orf_name", how='left', suffixes=("", "_drop")).filter(regex="^(?!.*_drop)")


chothani_2025_renamed['evidence_tmp_main'] = [set() for _ in range(len(chothani_2025_renamed))]

for i in chothani_2025_renamed.index:
    chothani_2025_renamed.loc[i, 'evidence_tmp_main'].add('Ribo-seq')

"""Join evidence and tissues"""

chothani_2025_renamed["evidence"] = chothani_2025_renamed[["evidence_tmp_s", "evidence_tmp_c", "evidence_tmp_d", "evidence_tmp_main"]].apply(
    lambda row: ";".join(sorted(set().union(*(s for s in row if isinstance(s, set))))),
    axis=1
)
chothani_2025_renamed["tissue"] = chothani_2025_renamed[["tissue_tmp", "tissue_tmp_s", "tissue_tmp_c"]].apply(
    lambda row: ";".join(sorted(set().union(*(s for s in row if isinstance(s, set))))),
    axis=1
)

#Adjust coordinates from BED to GTF

def transform_value(v):
    if isinstance(v, int):
        return v + 1
    elif isinstance(v, str):
        # split into numbers, increment, join with ;
        return ";".join(str(int(x) + 1) for x in v.split(","))
    else:
        return v  # fallback for NaN or other types

chothani_2025_renamed["Start"] = chothani_2025_renamed["Start"].apply(transform_value)


chothani_2025_renamed = chothani_2025_renamed.drop(columns=["evidence_tmp_s", "evidence_tmp_c", "evidence_tmp_d", "evidence_tmp_main", "tissue_tmp", "tissue_tmp_s", "tissue_tmp_c", "sequence_aa_MS"])

#drop dataset columns
chothani_2025_renamed = chothani_2025_renamed.drop(columns=["Ji_etal_2015", "Calviello_etal_2016", "Raj_etal_2016", "VanHeesch_etal_2019", "Chen_etal_2020", "Gaertner_etal_2020", "Chothani_etal_2022", "Sandmann_etal_2023"])


chothani_2025_renamed["paper_title"] = "An expanded reference catalog of translated open reading frames for biomedical research"
chothani_2025_renamed["paper_link"] = "https://www.biorxiv.org/content/10.1101/2025.07.03.662928v1"
chothani_2025_renamed["DOI"] = "10.1101/2025.07.03.662928"
chothani_2025_renamed["paper_citation"]= "Chothani_et_al_(2025)"

# Salvar o dataset no diretório do path_result
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
chothani_2025_renamed.to_csv(output_path, sep=',', index=False)
print("Done.")
