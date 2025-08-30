import pandas as pd
import os
import sys
import re

# Adicionando a pasta ../../util
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from util.util import download_and_unzip

# --- Configuração ---
# Paths
path_dataset = 'dataset'
path_result = '../../metadata/'
#autor é o nome do diretório
autor = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(path_dataset, exist_ok=True)
os.makedirs(path_result, exist_ok=True)

# Nome do arquivo do dataset
dataset = '44161_2024_544_MOESM3_ESM.xlsx'
dataset_path = os.path.join(path_dataset, dataset)

# Ler o arquivo (Excel, CSV ou TXT)
ruiz_orera = pd.read_excel(dataset_path, sheet_name="Supplementary Table 6", header=1)

# Adicionar informações de tecido
ruiz_orera["tissue"] = "Heart"

# Adicionar informações do artigo
ruiz_orera["DOI"] = "https://doi.org/10.1038/s44161-024-00544-7"
ruiz_orera["paper_link"] = "https://www.nature.com/articles/s44161-024-00544-7"
ruiz_orera["paper_title"] = "Evolução do controle translacional e o surgimento de genes e quadros de leitura aberta no coração humano e de primatas não humanos"
ruiz_orera["paper_citation"] = "Ruiz-Orera_et_al_(2024)"

#Rename columns for unification
ruiz_orera = ruiz_orera.rename(columns={'orf': 'orf_id', 'length': 'aa_orf_length', 'sequence': 'aa_orf_sequence'})

# Filtrar para espécies humanas
ruiz_orera = ruiz_orera[ruiz_orera["species"] == "human"]
del ruiz_orera["species"]

# Extrair coordenadas
coordinates = ruiz_orera["orf_id"].str.extract(
    r"(?P<prefix>P\d+)_(?P<Chr>[^:]+):(?P<Start>\d+)_(?P<End>\d+):(?P<Strand>[+-]):(?P<frame>\d+):(?P<length>\d+)"
)
del coordinates["prefix"]
del coordinates["frame"]
del coordinates["length"]

# Combinar coordenadas com o dataset
ruiz_orera = pd.concat([coordinates, ruiz_orera], axis=1)

#Unificação de orf_biotype
orf_biotype_mapping_ruiz = {
    "doORF": "doORF",
    "dORF": "dORF",
    "intORF": "intORF",
    "ncRNA-ORF": "transcrito_processado",
    "lncRNA-ORF": "lncRNA",
    "pseudogene": "pseudogene",
    "uoORF": "uoORF",
    "uORF": "uORF"
}
ruiz_orera["orf_biotype_unificado"] = ruiz_orera["orf_biotype"].map(orf_biotype_mapping_ruiz)

# Adicionar coluna de evidência
ruiz_orera["evidence"] = 'Ribo-seq'

# Detectar tipo de sequência
def detectar_tipo_sequencia(sequence):
    nucleotide_pattern = re.compile(r'^[ACGTUacgtu]+$')
    aa_one_letter = re.compile(r'^[ACDEFGHIKLMNPQRSTVWY]+$', re.IGNORECASE)
    aa_three_letters = re.compile(r'^([A-Za-z]{3})+$')

    if pd.isna(sequence):
        return 'desconhecido'
    elif nucleotide_pattern.match(sequence):
        return 'nt'
    elif aa_one_letter.match(sequence):
        return 'aa'
    elif aa_three_letters.match(sequence):
        return 'aa'
    else:
        return 'unknown'

ruiz_orera['data_type'] = ruiz_orera['aa_orf_sequence'].apply(
    lambda x: 'aa' if pd.notna(x) else 'unknown'
)

#criando nosso orf_name
#(2) autor
#(2) ano
#().....
orf_reference = 'ro24riboseqorf'
ruiz_orera["orf_name"] = orf_reference + "_" + (ruiz_orera.reset_index().index + 1).astype(str)

# Salvar o dataset processado no diretório do path_result
output_filename = f"{autor}.txt"
output_path = os.path.join(path_result, output_filename)
print(f"Saving processed data to {output_path}...")
ruiz_orera.to_csv(output_path, sep=',', index=False)
print("Done.")