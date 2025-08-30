import json
import os
import sys
import pandas as pd
import subprocess
import argparse

# adiciona o caminho do util.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../util")))

from util import Logger

# inicializa o logger
logger = Logger("logs/saida.log")
logger.log("Iniciando execução run_metadado.py")

def run_dataset_script(dataset_dir, base_path,create_dataset):
    """Executa o script 'run_*.py' para um determinado diretório de dataset."""
    script_name = f"run_{os.path.basename(dataset_dir)}.py"
    script_path = os.path.join(base_path, dataset_dir, script_name)
    
    if not os.path.exists(script_path):
        logger.log(f"AVISO: Script {script_path} não encontrado. Pulando.")
        exit()
        return False

    logger.log(f"Executando script para o dataset: {dataset_dir}...")
    try:
        # Executa o script a partir do seu próprio diretório para que os caminhos relativos funcionem
        logger.log(f"Executando script {script_name}...")
        if(create_dataset=='yes'):
            working_dir = os.path.join(base_path, dataset_dir)
            result = subprocess.run(
                [sys.executable, script_path], 
                cwd=working_dir, 
                text=True, # Decodifica a saída como texto
                encoding='utf-8', # Especifica a codificação
                capture_output=True  # opcional, captura stdout/stderr
            )
            logger.log(f"Script {script_name} executado com sucesso.")
            # logger.log(result.stdout) # Descomente para ver a saída do script
        else:
            logger.log(f"Script {script_name} NÃO foi executado pois create_dataset está definido como 'no'.")
        return True
    except subprocess.CalledProcessError as e:
        logger.log(f"ERRO ao executar {script_name}:")
        logger.log(f"STDOUT: {e.stdout}")
        logger.log(f"STDERR: {e.stderr}")
        return False

def combine_metadata(dataset_names, metadata_path):
    """Combina os arquivos de metadados gerados em um único DataFrame."""
    all_dfs = []
    logger.log("\nCombinando arquivos de metadados...")
    for name in dataset_names:
        file_path = os.path.join(metadata_path, f"{name}.txt")
        if os.path.exists(file_path):
            logger.log(f"Lendo {file_path}...")
            try:
                df = pd.read_csv(file_path, sep=',',dtype=str)
                all_dfs.append(df)
            except Exception as e:
                logger.log(f"ERRO ao ler {file_path}: {e}")
        else:
            logger.log(f"AVISO: Arquivo de metadados {file_path} não encontrado.")
    
    if not all_dfs:
        logger.log("Nenhum DataFrame para combinar. Encerrando.")
        return None

    combined_df = pd.concat(all_dfs, ignore_index=True)
    logger.log(f"Total de {len(combined_df)} registros combinados.")
    return combined_df

def save_combined_files(df, metadata_path, experiment_name):
    """Salva o DataFrame combinado como TXT e FASTA."""
    if df is None or df.empty:
        logger.log("DataFrame vazio. Nenhum arquivo será salvo.")
        return

    # Salvar arquivo TXT
    output_txt_path = os.path.join(metadata_path, f"{experiment_name}.txt")
    logger.log(f"Salvando arquivo de metadados combinado em: {output_txt_path}")
    df.to_csv(output_txt_path, sep=',', index=False)

    # Salvar arquivo FASTA
    output_fasta_path = os.path.join(metadata_path, f"{experiment_name}.fasta")
    logger.log(f"Salvando arquivo FASTA combinado em: {output_fasta_path}")
    
    if 'orf_name' not in df.columns or 'nt_orf_sequence' not in df.columns:
        logger.log("ERRO: Colunas 'orf_name' e/ou 'nt_orf_sequence' não encontradas. Não é possível gerar o arquivo FASTA.")
        return

    with open(output_fasta_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            orf_name = row['orf_name']
            sequence = row['nt_orf_sequence']
            if pd.notna(orf_name) and pd.notna(sequence):
                f.write(f">{orf_name}\n")
                f.write(f"{sequence}\n")
    
    logger.log("Arquivos finais gerados com sucesso.")

def main():
    parser = argparse.ArgumentParser(description="Executa um experimento combinando múltiplos datasets.")
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo de configuração JSON.")
    parser.add_argument("-c", "--create_dataset", required=True, help="Gera datasets (yes/no)")
    args = parser.parse_args()
    args.create_dataset=args.create_dataset.lower()
    if not os.path.exists(args.input):
        logger.log(f"ERRO: Arquivo de configuração não encontrado em '{args.input}'")
        sys.exit(1)

    with open(args.input, 'r', encoding='utf-8') as f:
        config = json.load(f)

    experiment_name = config.get("experiment_name")
    dataset_names = config.get("datasets")

    if not experiment_name or not dataset_names:
        logger.log("ERRO: O arquivo JSON deve conter 'experiment_name' e uma lista 'datasets'.")
        sys.exit(1)

    base_path = os.path.dirname(os.path.abspath(__file__))
    metadata_path = os.path.abspath(os.path.join(base_path,'..', 'metadata'))
    os.makedirs(metadata_path, exist_ok=True)

    successful_datasets = [name for name in dataset_names if run_dataset_script(name, base_path,args.create_dataset)]

    if successful_datasets:
        combined_df = combine_metadata(successful_datasets, metadata_path)
        save_combined_files(combined_df, metadata_path, experiment_name)

if __name__ == "__main__":
    main()