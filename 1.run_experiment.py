import argparse
import json
import subprocess
import sys
import re
import os

def flatten_dict(d, parent_key='', sep='.'):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def substituir_variaveis(s, variaveis):
    padrao = r"\{\{(.*?)\}\}"

    def replace(match):
        chave = match.group(1).strip()
        return str(variaveis.get(chave, match.group(0)))  # mantém {{chave}} se não achar

    anterior = None
    atual = s
    while atual != anterior:
        anterior = atual
        atual = re.sub(padrao, replace, atual)
    return atual


def executar_experimento(file_name,config):
    experiment_name = config.get("experiment_name")
    create_dataset = config.get("create_dataset","Yes")
    create_dataset=create_dataset.lower()

    datasets = config.get("datasets", [])
    tools = config.get("tools", [])
    variaveis_flat_json = flatten_dict(config)

    #Gerar dataset
    #create_dataset informa se serão gerados os datasets para serem concatenados no metadado 
    # Yes - gera os datasets 
    # No - não gera os datasets (aproveita os arquivos gerados anteriormente)
    print("Gerando metadados:")
    cmd_template=f"conda run -n ferramentas env PYTHONUNBUFFERED=1 python datasets/run_metadado.py -i {file_name} -c {create_dataset}"    
    cmd = substituir_variaveis(cmd_template, variaveis_flat_json)
    print(f'Executando comando {cmd}')
    resultado = subprocess.run(
        cmd,
        shell=True,
        check=True,
        text=True
    )
    print(f"✅ Saída:\n{resultado.stdout}")
    
    for tool in tools:
        description_tool = tool.get("description", "tool_sem_descriptione")
        cmd_template = tool.get("cmd", "")
        cmd_dir = tool.get("directory", "./")
        cmd = substituir_variaveis(cmd_template, variaveis_flat_json)

        print(f"⚙️  Ferramenta: {description_tool}")
        print(f"🧪 Comando: {cmd}")

        try:
            resultado = subprocess.run(
                cmd,
                shell=True,
                check=True,
                text=True,
                cwd=cmd_dir,
                stdout=sys.stdout,
                stderr=sys.stderr
            )                
            print(f"✅ Saída:\n{resultado.stdout}")
            if resultado.stderr:
                print(f"Erros:\n{resultado.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Falha ao executar o comando da ferramenta '{description_tool}'")
            print(f"Comando: {cmd}")
            print(f"Erro: {e.stderr}")

def main():
    parser = argparse.ArgumentParser(description="Executa ferramentas definidas em um arquivo JSON sobre vários datasets.")
    parser.add_argument("-i", "--input", required=True, help="Caminho para o arquivo de configuração JSON.")
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        return

    executar_experimento(args.input,config)

if __name__ == "__main__":
    main()
