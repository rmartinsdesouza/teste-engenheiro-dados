import os
import sys
import time
import subprocess
from pathlib import Path
import utils_bq as bq

# Antes de rodar, garanta que os datasets existem
def _ensure_datasets():
    try:
        raw = os.getenv("RAW_DATASET_ID")
        curated = os.getenv("PROCESSED_DATASET_ID")
        analytics = os.getenv("ANALYTICS_DATASET_ID") or os.getenv("ANALYTICS_DATASET", "psa_analytics")

        for ds in [raw, curated, analytics]:
            if ds:
                try:
                    bq.create_dataset(ds)
                except Exception as e:
                    # Já existe ou erro transitório — logar e seguir
                    print(f"[warn] create_dataset({ds}) -> {e}")
    except Exception as e:
        print(f"[warn] Não foi possível garantir datasets: {e}")


def _prime_env_defaults():
    """Define variáveis de ambiente padrão ANTES do load_dotenv(),
    para que o dotenv não sobrescreva (override=False).
    """
    os.environ.setdefault("RAW_DATASET_ID", "psa_raw")
    os.environ.setdefault("PROCESSED_DATASET_ID", "psa_curated")
    os.environ.setdefault("ANALYTICS_DATASET_ID", "psa_analytics")

    # Tabelas padrão (curated)
    os.environ.setdefault("TABLE_CLIENTES", "clientes")
    os.environ.setdefault("TABLE_ANALISES_TRIBUTARIAS", "analises_tributarias")
    os.environ.setdefault("TABLE_NOTAS", "notas_fiscais")
    os.environ.setdefault("TABLE_TAREFAS", "tarefas_projetos")

    # Tabelas RAW
    os.environ.setdefault("RAW_TABLE_ANALISES", "analises_tributarias")
    os.environ.setdefault("RAW_TABLE_TAREFAS", "tarefas_projetos")
    os.environ.setdefault("RAW_TABLE_NOTAS", "notas_fiscais_raw")

    # Fontes locais (arquivos)
    os.environ.setdefault("SOURCE_PATH_CLIENTES", str(Path("dados/dados_clientes.csv")))
    os.environ.setdefault("SOURCE_PATH_ANALISES", str(Path("dados/analises_tributarias.txt")))
    os.environ.setdefault("SOURCE_PATH_NOTAS", str(Path("dados/notas_fiscais.xml")))
    os.environ.setdefault("SOURCE_PATH_TAREFAS", str(Path("dados/tarefas_projetos.json")))

    # Modo de escrita default
    os.environ.setdefault("WRITE_MODE", "truncate")

# Ordem sugerida: RAW -> CURATED -> ANALYTICS
RAW_SCRIPTS = [
    "clientes_raw.py",
    "analises_tributarias_raw.py",
    "notas_fiscais_raw.py",
    "tarefas_projetos_raw.py",
    "logs_sistema.py",
]

CURATED_SCRIPTS = [
    "clientes_curated.py",
    "analises_tributarias_curated.py",
    "notas_fiscais_curated.py",
    "logs_sistema_curated.py",
    "tarefas_projetos_curated.py",
]

ANALYTICS_SCRIPTS = [
    "resumo_clientes_tributos.py",
    "performance_projetos.py",
]

ALL = RAW_SCRIPTS + CURATED_SCRIPTS + ANALYTICS_SCRIPTS

SCRIPTS_DIR = Path(__file__).parent
PYTHON = sys.executable or "python"


def run_script(script: str) -> tuple[str, int, float]:
    path = SCRIPTS_DIR / script
    start = time.time()
    try:
        print(f"\n=== RUN {script} ===")
        proc = subprocess.run([PYTHON, str(path)], cwd=SCRIPTS_DIR.parent, env=os.environ)
        rc = proc.returncode
    except Exception as e:
        print(f"[ERROR] Falha ao executar {script}: {e}")
        rc = 1
    dur = time.time() - start
    print(f"=== END {script} (rc={rc}, {dur:.1f}s) ===\n")
    return script, rc, dur


def main():
    # 1) Instancia variáveis antes do load_dotenv
    _prime_env_defaults()
    # 2) Carrega .env/ADC sem sobrescrever defaults já setados
    bq.load_env()
    # 3) Garante datasets
    _ensure_datasets()
    failures = []
    results = []

    # Permitir filtrar por categoria via env RUN_GROUP=raw|curated|analytics
    group = os.getenv("RUN_GROUP", "all").lower()
    if group == "raw":
        to_run = RAW_SCRIPTS
    elif group == "curated":
        to_run = CURATED_SCRIPTS
    elif group == "analytics":
        to_run = ANALYTICS_SCRIPTS
    else:
        to_run = ALL

    for script in to_run:
        name, rc, dur = run_script(script)
        results.append((name, rc, dur))
        if rc != 0:
            failures.append(name)

    print("\n===== SUMMARY =====")
    for name, rc, dur in results:
        status = "OK" if rc == 0 else "FAIL"
        print(f"{status:4} | {dur:6.1f}s | {name}")

    if failures:
        print("\nFalharam:")
        for f in failures:
            print(f"- {f}")
        sys.exit(1)
    else:
        print("\nTodos os scripts finalizaram com sucesso.")
        sys.exit(0)


if __name__ == "__main__":
    main()
