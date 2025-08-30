
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import pandas as pd
import os
import argparse


def filtrar_fasta_csORF_finder(input_fasta_path, output_fasta_path):

    fasta_sequences = SeqIO.parse(open(input_fasta_path), 'fasta')
    all_sequences = list(fasta_sequences)
    print(f"Number of sequences before filtering: {len(all_sequences)}")

    start_codons = ['ATG']
    stop_codons = ['TAA', 'TAG', 'TGA']

    filtered_records = []
    eliminadas = []  # Para armazenar as sequências eliminadas e o motivo
    count_tamanho = 0
    count_codons = 0
    count_stop_middle = 0
    count_aprovadas = 0
    count_1base = 0

    for record in all_sequences:
        seq = str(record.seq)
        motivo = ""

        start_idx = -1
        for i in range(0, len(seq)-2, 3):
            if seq[i:i+3] in start_codons:
                start_idx = i
                break

        stop_idx = -1
        if start_idx != -1:
            for i in range(start_idx+3, len(seq)-2, 3):
                if seq[i:i+3] in stop_codons:
                    stop_idx = i + 3
                    break

        if start_idx == -1 or stop_idx == -1 or start_idx >= stop_idx:
            count_codons += 1
            motivo = "Sem códon inicial no começo da sequencia ou de parada no final"
            eliminadas.append({'motivo': motivo,'id': record.id, 'seq': seq})
            continue

        seq_cds = seq[start_idx:stop_idx]
        middle_nts = seq_cds[3:-3]
        if len(middle_nts) > 0 and len(set(middle_nts)) == 1:
            count_1base += 1
            motivo = "Apenas uma base nitrogenada entre códon inicial e de parada"
            eliminadas.append({'motivo': motivo, 'id': record.id, 'seq': seq_cds})
            continue

        if (len(seq_cds) % 3 != 0 or len(seq_cds) <= 9):
            count_tamanho += 1
            if (len(seq_cds) % 3 != 0):
                motivo = "Tamanho inválido: não é divisível por 3"
            else:
                motivo = "Tamanho inválido: menor que 9 nt"
            eliminadas.append({'motivo': motivo,'id': record.id, 'seq': seq_cds})
            continue

        has_stop_codon_in_middle = False
        for i in range(3, len(seq_cds) - 3, 3):
            codon = seq_cds[i:i+3]
            if codon in stop_codons:
                has_stop_codon_in_middle = True
                break

        if has_stop_codon_in_middle:
            count_stop_middle += 1
            motivo = "Códon de parada no meio da sequencia"
            eliminadas.append({'motivo': motivo,'id': record.id, 'seq': seq_cds})
            continue

        filtered_records.append(SeqRecord(record.seq.__class__(seq_cds), id=record.id, description=record.description))
        count_aprovadas += 1

    print(f"Filtradas por tamanho inválido: {count_tamanho}")
    print(f"Filtradas por não achar códon inicial/final: {count_codons}")
    print(f"Filtradas por códon de parada no meio: {count_stop_middle}")
    print(f"Filtradas por apenas uma base entre códon inicial e de parada: {count_1base}")

    print(f"Sequências aprovadas: {count_aprovadas}")

    print(f"Number of sequences after filtering: {len(filtered_records)}")
    if os.path.exists(output_fasta_path):
        os.remove(output_fasta_path)
    with open(output_fasta_path, 'w') as output_handle:
        SeqIO.write(filtered_records, output_handle, "fasta")

    print(f"Filtered sequences saved to {output_fasta_path}")



def main():
    parser = argparse.ArgumentParser(description="Executa filtro das sequências do fasta para rodar no csORF-finder.")
    parser.add_argument("-i", "--input", required=True, help="Fasta Original.")
    parser.add_argument("-o", "--output", required=True, help="Fasta filtrado.")
    args = parser.parse_args()
    
    filtrar_fasta_csORF_finder(args.input, args.output)


if __name__ == "__main__":
    main()
