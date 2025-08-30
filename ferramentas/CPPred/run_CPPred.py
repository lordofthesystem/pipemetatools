# -*- coding: utf-8 -*-
import argparse
import subprocess
import sys
import os

# Nome do arquivo atual
name_file = os.path.basename(__file__)  # ex: run_algumacoisa.py

# Remove "run_" do início e ".py" do final
name_tool = name_file.replace("run_", "").replace(".py", "")



def run_command(description: str, cmd_template: str, experiment_name: str, directory: str = None, conda: str = None):
    """
    Substitui o placeholder do nome do experimento em um template de comando e o
    executa dentro do ambiente conda 'csORF-finder', tratando erros e exibindo o progresso.

    Args:
        description (str): Uma breve descrição do que o comando faz.
        cmd_template (str): O comando a ser executado com "{{experiment_name}}" como placeholder.
        experiment_name (str): O nome do experimento para substituir no template.
        directory (str, optional): O diretório de trabalho para executar o comando. Defaults to None.
    """
    # Substitui o placeholder {{experiment_name}}
    base_cmd = cmd_template.replace("{{experiment_name}}", experiment_name)
    base_cmd = base_cmd.replace("{{name_tool}}", name_tool)

    # Monta o comando para ser executado dentro do ambiente conda.
    if conda:
        cmd = f"conda run -n {conda} {base_cmd}"
    else:   
        cmd = f"conda run -n {name_tool} {base_cmd}"

    print(f"--- {description} ---")
    print(f"Executando: {cmd}")
    if directory:
        print(f"No diretório: {directory}")

    try:
        # Executa o comando, capturando a saída para exibição
        # Usar executable='/bin/bash' é importante para que 'conda activate' funcione.
        resultado = subprocess.run(
            cmd,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            cwd=directory,  # Define o diretório de trabalho se especificado
            executable="/bin/bash"
        )
        # Imprime a saída padrão e de erro se houver
        if resultado.stdout:
            print("Saída:\n", resultado.stdout)
        if resultado.stderr:
            print("Erros:\n", resultado.stderr)
        print(f"Sucesso: {description}\n")

    except subprocess.CalledProcessError as e:
        print(f"ERRO ao executar: {description}")
        print(f"Comando: {e.cmd}")
        print(f"Código de saída: {e.returncode}")
        print(f"Saída de erro:\n{e.stderr}")
        sys.exit(1) # Interrompe o script se um comando falhar
    except FileNotFoundError as e:
        # Este erro pode acontecer se /bin/bash não for encontrado (e.g., no Windows puro)
        # ou se o comando 'conda' não estiver no PATH.
        print("ERRO: Comando ou diretório não encontrado.")
        print("   Verifique se 'conda' está no PATH e se você está em um ambiente shell compatível (como bash, zsh, etc.).")
        print(f"Detalhes: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Executa a pipeline de análise do csORF-finder para um experimento específico."
    )
    parser.add_argument(
        "-e", "--experiment_name",
        required=True,
        help="O nome do experimento a ser processado (ex: 'combined_tools_v1')."
    )
    args = parser.parse_args()
    experiment_name = args.experiment_name

    # Lista de comandos a serem executados em sequência
    commands = [        
        {"description": "Criar diretório de metadados para os resultados",
         "cmd": "mkdir -p metadata/{{experiment_name}}"},
        {"description": "Limpar resultados antigos no diretório de metadados",
         "cmd": "rm -f metadata/{{experiment_name}}/"+name_tool+"*"},
         {"description": "Executar CPPred.py",
         "directory": "ferramentas/CPPred/CPPred/bin",
         "cmd": "python CPPred.py -i ../../../../metadata/{{experiment_name}}.fasta  -hex ../Hexamer/Integrated_Hexamer.tsv -r ../Integrated_Model/Integrated.range -mol ../Integrated_Model/Integrated.model -spe Integrated -o {{experiment_name}}_"+name_tool+".txt"},
        {"description": "Mover novos resultados para o diretório de metadados",
         "directory": "ferramentas/CPPred/",
         "conda":"ferramentas",
         "cmd": "python run_{{name_tool}}_transfer_metadata.py -i {{experiment_name}}_"+name_tool+".txt -e {{experiment_name}}"}
    ]


    print(f"Iniciando pipeline para o experimento: {experiment_name}\n")

    # Executa cada comando na sequência
    for command_info in commands:
        run_command(
            description=command_info["description"],
            cmd_template=command_info["cmd"],
            experiment_name=experiment_name,
            directory=command_info.get("directory",),
            conda=command_info.get("conda",)
        )


    print("Pipeline concluída com sucesso!")

if __name__ == "__main__":
    main()