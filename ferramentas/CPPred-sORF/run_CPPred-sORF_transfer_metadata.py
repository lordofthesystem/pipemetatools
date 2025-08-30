# -*- coding: utf-8 -*-

import csv
import argparse
import ast  # mais seguro que eval()
import os

# Argumentos da linha de comando
parser = argparse.ArgumentParser(description="Corrige CSV e adiciona cabeçalho.")
parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo CSV de entrada.")
parser.add_argument(
    "-e", "--experiment_name",
    required=True,
    help="O nome do experimento a ser processado (ex: 'combined_tools_v1')."
)
args = parser.parse_args()

# Nome do arquivo atual
name_file = os.path.basename(__file__)  # ex: run_algumacoisa.py
# Remove "run_" do início e ".py" do final
name_tool = name_file.replace("run_", "").replace("_transfer_metadata.py", "")

arquivo_entrada = os.path.join('CPPred-sORF/',args.input)
arquivo_saida = os.path.join('..','..','metadata',args.experiment_name, f'{args.experiment_name}_{name_tool}.txt')


with open(arquivo_entrada, "r", encoding="utf-8") as infile, open(arquivo_saida, "w", newline="", encoding="utf-8") as outfile:
    leitor = csv.reader(infile, delimiter="\t")
    escritor = csv.writer(outfile, delimiter=",")

    escritor.writerow(["orf_name", "nt_orf_sequence", "result", "value"])

    for linha in leitor:
        nome = linha[0]
        sequencia = ""
        resultado = linha[len(linha)-2]
        if resultado == "coding":
            resultado = "Coding"
        elif resultado == "noncoding":
            resultado = "Non-coding"

        valor = linha[len(linha)-1]

        escritor.writerow([nome, sequencia, resultado, valor])
