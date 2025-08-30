import os
import requests
import zipfile
import pandas as pd
import os
from datetime import datetime

class Logger:
    def __init__(self, filepath: str):
        """Inicializa o logger com o caminho do arquivo de log."""
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def log(self, message: str, console: bool = True):
        """Salva a mensagem no log e, opcionalmente, imprime no console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"

        # grava no arquivo
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        # também mostra no terminal se quiser
        if console:
            print(log_line)

def read_fasta_to_dataframe(fasta_path):
    """
    Lê um arquivo FASTA e o converte para um DataFrame do pandas.
    O DataFrame terá duas colunas: 'orf_id' (do cabeçalho) e 'nt_orf_sequence'.

    Args:
        fasta_path (str): O caminho para o arquivo FASTA.

    Returns:
        pandas.DataFrame: Um DataFrame com os dados do arquivo FASTA.
    """
    records = []
    header = None
    sequence_parts = []
    with open(fasta_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                if header is not None:
                    records.append((header, ''.join(sequence_parts)))
                header = line[1:]  # Remove o '>'
                sequence_parts = []
            else:
                sequence_parts.append(line)
    if header is not None:
        records.append((header, ''.join(sequence_parts)))

    df = pd.DataFrame(records, columns=['orf_id', 'nt_orf_sequence'])
    return df

def download(path_dataset, url):
    os.makedirs(path_dataset, exist_ok=True)
    url_filename = os.path.basename(url)
    url_filepath = os.path.join(path_dataset, url_filename)

    if not os.path.exists(url_filepath):
        print(f"Baixando {url_filename} ...")
        headers = {"User-Agent": "Mozilla/5.0"}
        with requests.get(url_filename, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(url_filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Download concluído.")
    else:
        print(f"Arquivo {url_filename} já existe. Pulando download.")

def download_and_unzip(path_dataset, zip_url):
    download(path_dataset, zip_url)
    zip_filename = os.path.basename(zip_url)
    zip_filepath = os.path.join(path_dataset, zip_filename)
    print(f"Descompactando {zip_filepath} ...")
    try:
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            zip_ref.extractall(path_dataset)
        print("Descompactação concluída.")
    except zipfile.BadZipFile:
        print("Arquivo zip inválido ou corrompido.")
