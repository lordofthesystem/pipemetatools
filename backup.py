import tarfile
import os
from datetime import datetime

# Caminho da pasta que você quer fazer backup
source_folder = "/mnt/dados/felipehaddad/pipemetatools/"

# Pasta onde o backup será salvo
backup_folder = "/mnt/dados/felipehaddad/pipemetatools/backups"
os.makedirs(backup_folder, exist_ok=True)

# Criar nome do arquivo com timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_filename = f"pipemetatools_backup_{timestamp}.tar.gz"
backup_path = os.path.join(backup_folder, backup_filename)

# Criar backup tar.gz
with tarfile.open(backup_path, "w:gz") as tar:
    tar.add(source_folder, arcname=os.path.basename(source_folder))

print(f"Backup criado com sucesso em: {backup_path}")
