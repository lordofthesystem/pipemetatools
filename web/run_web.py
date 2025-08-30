import subprocess

# Comando para rodar dentro do ambiente conda 'web'
command = [
    "conda", "run", "-n", "web",
    "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"
]

try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    print(f"Erro ao executar o servidor: {e}")
