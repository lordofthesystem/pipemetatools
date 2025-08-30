# -*- coding: utf-8 -*-
import argparse
import json
import os
import pandas as pd
import glob
from typing import Optional


def process_experiment_results(experiment_name: str):
    """
    Processa os resultados de um experimento.

    Lê um arquivo de dados principal e o enriquece com os resultados de várias ferramentas,
    adicionando uma nova coluna para cada uma.

    Args:
        experiment_name (str): O nome do experimento a ser processado.
    Returns:
        tuple[Optional[pd.DataFrame], list[str]]: Uma tupla contendo o DataFrame combinado
                                                  e uma lista com os nomes das colunas adicionadas.
    """


    # 2. Carregar o DataFrame principal
    main_df_path = os.path.join('metadata', f'{experiment_name}.txt')
    try:
        # Tenta ler o arquivo como CSV separado por ,
        main_df = pd.read_csv(main_df_path, sep=',',dtype=str)

        if 'orf_name' not in main_df.columns:
            print(f"Erro: A coluna 'orf_name' não foi encontrada no DataFrame principal: {main_df_path}")
            return None, []
        print(f"DataFrame principal carregado com sucesso de: {main_df_path}")
        print(f"Shape do DataFrame principal: {main_df.shape}")

    except FileNotFoundError:
        print(f"Erro: Arquivo do DataFrame principal não encontrado em {main_df_path}")
        return None, []

    # 3. Encontrar e processar todos os arquivos de resultado das ferramentas
    results_dir = os.path.join('metadata', experiment_name)
    tool_files_pattern = os.path.join(results_dir, 'result_*.txt')
    tool_files = glob.glob(tool_files_pattern)

    if not tool_files:
        print(f"Aviso: Nenhum arquivo de resultado encontrado em {results_dir} com o padrão 'result_*.txt'")
    else:
        print(f"\nEncontrados {len(tool_files)} arquivos de resultado para processar.")

    added_tool_columns = []

    # 4. Iterar sobre cada arquivo, extrair dados e mesclar no DataFrame principal
    for tool_file_path in tool_files:
        filename = os.path.basename(tool_file_path)

        # Extrair o nome da ferramenta do nome do arquivo
        prefix = f"result_{experiment_name}-"
        suffix = ".txt"
        if filename.startswith(prefix) and filename.endswith(suffix):
            tool_name = filename[len(prefix):-len(suffix)]
        else:
            print(f"Aviso: Pulando arquivo com formato inesperado: {filename}")
            continue

        print(f"  - Processando ferramenta: {tool_name}")

        try:
            # Ler o DataFrame da ferramenta
            tool_df = pd.read_csv(tool_file_path, ',',dtype=str)

            if 'orf_name' not in tool_df.columns or 'result' not in tool_df.columns:
                print(f"    Aviso: Pulando '{tool_name}' pois a coluna 'orf_name' ou 'result' está ausente.")
                continue

            # Criar um mapa de orf_name para o valor de 'result'
            id_to_result_map = tool_df.set_index('orf_name')['result']

            # Adicionar a nova coluna ao DataFrame principal usando o mapa
            main_df[tool_name] = main_df['orf_name'].map(id_to_result_map)
            print(f"    -> Coluna '{tool_name}' adicionada com sucesso.")
            added_tool_columns.append(tool_name)

        except Exception as e:
            print(f"    Erro ao processar o arquivo {filename}: {e}")

    return main_df, added_tool_columns


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combina os resultados de predição de ferramentas em um arquivo de dados principal.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Caminho para o arquivo de configuração JSON do experimento.\nExemplo: experiment_combined_tools_v1.json'
    )
    args = parser.parse_args()

        # 1. Ler o JSON e obter o nome do experimento
    json_path=args.input
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        experiment_name = config['experiment_name']
        print(f"Processando o experimento: {experiment_name}")
    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em {json_path}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao ler ou analisar o arquivo JSON: {e}")
    
    final_df, added_columns = process_experiment_results(experiment_name)

    if final_df is not None:
        print("\nProcessamento concluído.")
        print("Informações do DataFrame final:")
        final_df.info(verbose=False)
        print("\nCabeçalho do DataFrame final:")
        print(final_df.head())

        # Salvar o DataFrame final
        if experiment_name:
            output_dir = os.path.join('result', experiment_name)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f'{experiment_name}.txt')

            final_df.to_csv(output_path, index=False, sep=',')
            print(f"\nDataFrame final salvo com sucesso em: {output_path}")

            # Salvar JSON com a lista de colunas adicionadas
            if added_columns:
                json_output_path = os.path.join(output_dir, f'{experiment_name}.json')
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump({"tools_columns": added_columns}, f, indent=4)
                print(f"Lista de colunas adicionadas salva em: {json_output_path}")
