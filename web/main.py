from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import pandas as pd
from fastapi.responses import FileResponse
from collections import Counter

# Configuracoes
CSV_FOLDER = Path("../metadata")

app = FastAPI(title="CSV Explorer")

# Servir arquivos estaticos (se tiver HTML/CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse("templates/index.html")

@app.get("/list", response_class=JSONResponse)
def explorer():
    """API simples para retornar a lista de arquivos CSV."""
    files = [f.name for f in CSV_FOLDER.glob("*.txt")]
    return {"files": files}


@app.get("/file")
def view_file(name: str, columns: str = None, nrows: int = 5, split_by: str = None):
    print(columns)
    file_path = CSV_FOLDER / name
    if not file_path.exists():
        return JSONResponse({"error": "Arquivo não encontrado"}, status_code=404)

    if columns:
        columns = columns.split(",")
    else:
        columns = None

    # Se houver split_by, adiciona a coluna ao conjunto (se não estiver)
    if split_by and (columns is not None) and (split_by not in columns):
        columns.append(split_by)

    # Lê o arquivo completo com as colunas selecionadas
    df = pd.read_csv(file_path, usecols=columns, dtype=str)

    if split_by:
        # Seleciona as primeiras nrows para cada categoria
        sampled_df = df.groupby(split_by, group_keys=False).head(nrows)
    else:
        sampled_df = df.head(nrows)

    print('Fim do /file')

    # Substitui NaN por None para JSON válido
    sampled_df = sampled_df.where(pd.notnull(sampled_df), None)

    return JSONResponse(content=sampled_df.to_dict(orient="records"))


from typing import Optional

@app.get("/search")
def search_in_csv(name: str, column: str, query: str, limit: int = 10, columns: Optional[str] = None):
    file_path = CSV_FOLDER / name
    if not file_path.exists():
        return JSONResponse({"error": "Arquivo não encontrado"}, status_code=404)

    if columns:
        columns = columns.split(",")
    else:
        columns = None

    results = []
    for chunk in pd.read_csv(file_path, chunksize=50000,dtype=str):
        filtered = chunk[chunk[column].astype(str).str.contains(query, case=False, na=False)]
        if not filtered.empty:
            if columns:
                filtered = filtered[columns]
            filtered = filtered.fillna("").astype(str)
            results.extend(filtered.to_dict(orient="records"))
        if len(results) >= limit:
            break
    return results[:limit]


    
@app.get("/unique")
def unique_values(name: str, column: str):
    file_path = CSV_FOLDER / name
    if not file_path.exists():
        return JSONResponse({"error": "Arquivo não encontrado"}, status_code=404)

    counts = Counter()
    for chunk in pd.read_csv(file_path, usecols=[column], chunksize=100000, dtype=str):
        print(counts)
        counts.update(chunk[column].dropna())

    # Retorna todos os valores únicos com suas contagens
    result = [{"valor": val, "quantidade": qtd} for val, qtd in counts.items()]
    print(counts.items())
    return result



@app.get("/columns", response_class=JSONResponse)
def get_columns(name: str):
    file_path = CSV_FOLDER / name
    if not file_path.exists():
        return JSONResponse({"error": "Arquivo não encontrado"}, status_code=404)
    # Leitura só das colunas (sem dados) para ser rápido
    df = pd.read_csv(file_path, nrows=0,dtype=str)
    return {"columns": df.columns.tolist()}
