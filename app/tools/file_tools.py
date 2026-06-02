"""Ferramentas de arquivos do Jarvis.

Riscos atribuídos conforme a seção 6 do README:
  - ler/listar/pesquisar  -> BAIXO (executa direto)
  - criar/mover           -> MÉDIO (pede confirmação)
  - apagar                -> ALTO  (sempre confirma) — entra numa fase futura

Caminhos com "~" são expandidos para o home do usuário. Para evitar
respostas gigantes ao LLM, a leitura tem um limite de caracteres.
"""

from __future__ import annotations

from pathlib import Path

from app.security.permissions import RiskLevel
from app.tools.registry import tool

# Limite de conteúdo retornado ao LLM (evita estourar o contexto/custo).
_MAX_READ_CHARS = 8000
# Limite de itens listados de uma vez.
_MAX_LIST_ITEMS = 200


def _resolve(caminho: str) -> Path:
    """Expande ~ e resolve para um caminho absoluto."""
    return Path(caminho).expanduser().resolve()


@tool(risk=RiskLevel.LOW, description="Lê o conteúdo de um arquivo de texto.")
def ler_arquivo(caminho: str) -> str:
    """Lê e retorna o conteúdo de um arquivo de texto."""
    p = _resolve(caminho)
    if not p.exists():
        return f"Arquivo não encontrado: {p}"
    if not p.is_file():
        return f"Não é um arquivo: {p}"
    try:
        texto = p.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"Erro ao ler {p}: {exc}"
    if len(texto) > _MAX_READ_CHARS:
        return texto[:_MAX_READ_CHARS] + f"\n\n[... truncado em {_MAX_READ_CHARS} caracteres]"
    return texto


@tool(
    risk=RiskLevel.LOW,
    description="Lista os arquivos e pastas de um diretório.",
)
def listar_arquivos(diretorio: str = ".") -> str:
    """Lista os itens de um diretório (pastas marcadas com /)."""
    p = _resolve(diretorio)
    if not p.is_dir():
        return f"Diretório não encontrado: {p}"
    itens = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    linhas = [f"{item.name}/" if item.is_dir() else item.name for item in itens]
    extra = ""
    if len(linhas) > _MAX_LIST_ITEMS:
        extra = f"\n[... {len(linhas) - _MAX_LIST_ITEMS} itens a mais]"
        linhas = linhas[:_MAX_LIST_ITEMS]
    if not linhas:
        return f"O diretório {p} está vazio."
    return f"Conteúdo de {p}:\n" + "\n".join(linhas) + extra


@tool(
    risk=RiskLevel.LOW,
    description="Procura arquivos por padrão de nome (ex.: '*.pdf') a partir de um diretório.",
)
def pesquisar_arquivo(padrao: str, diretorio: str = ".") -> str:
    """Busca recursiva por arquivos cujo nome casa com o padrão (glob)."""
    p = _resolve(diretorio)
    if not p.is_dir():
        return f"Diretório não encontrado: {p}"
    encontrados = [str(m) for m in p.rglob(padrao) if m.is_file()]
    if not encontrados:
        return f"Nenhum arquivo casando com '{padrao}' em {p}."
    extra = ""
    if len(encontrados) > _MAX_LIST_ITEMS:
        extra = f"\n[... {len(encontrados) - _MAX_LIST_ITEMS} resultados a mais]"
        encontrados = encontrados[:_MAX_LIST_ITEMS]
    return f"{len(encontrados)} resultado(s):\n" + "\n".join(encontrados) + extra


@tool(
    risk=RiskLevel.MEDIUM,
    description="Cria um arquivo de texto com o conteúdo informado.",
)
def criar_arquivo(caminho: str, conteudo: str = "") -> str:
    """Cria (ou sobrescreve) um arquivo de texto. Risco MÉDIO: confirma."""
    p = _resolve(caminho)
    existia = p.exists()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(conteudo, encoding="utf-8")
    except OSError as exc:
        return f"Erro ao criar {p}: {exc}"
    verbo = "Sobrescrevi" if existia else "Criei"
    return f"{verbo} o arquivo {p} ({len(conteudo)} caracteres)."


@tool(
    risk=RiskLevel.MEDIUM,
    description="Move ou renomeia um arquivo de origem para um destino.",
)
def mover_arquivo(origem: str, destino: str) -> str:
    """Move/renomeia um arquivo. Risco MÉDIO: confirma."""
    orig = _resolve(origem)
    dest = _resolve(destino)
    if not orig.exists():
        return f"Origem não encontrada: {orig}"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        orig.rename(dest)
    except OSError as exc:
        return f"Erro ao mover {orig} -> {dest}: {exc}"
    return f"Movi {orig} para {dest}."
