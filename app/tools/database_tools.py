"""Ferramentas de banco de dados (PostgreSQL) do Jarvis.

Política de segurança (seção 6 do README): "alterar banco de dados" é
risco ALTO. Por isso, esta ferramenta de consulta:
  - aceita SOMENTE comandos de leitura (SELECT / WITH / EXPLAIN / SHOW);
  - é classificada como risco MÉDIO (passa pelo guard de confirmação);
  - recusa qualquer comando de escrita (INSERT/UPDATE/DELETE/DROP/...).

Escrita/DDL ficaria numa ferramenta separada de risco ALTO, numa fase
futura. A conexão vem de DATABASE_URL no `.env`. O driver `psycopg` é
importado de forma preguiçosa, para não ser dependência obrigatória.
"""

from __future__ import annotations

from app.config import settings
from app.security.permissions import RiskLevel
from app.tools.registry import tool

# Comandos de leitura permitidos (primeira palavra da query).
_LEITURA_PERMITIDA = {"select", "with", "explain", "show", "table"}
# Limite de linhas retornadas ao LLM.
_MAX_LINHAS = 50


@tool(
    risk=RiskLevel.MEDIUM,
    description="Executa uma consulta SQL de LEITURA (SELECT) no PostgreSQL e retorna as linhas.",
)
def consultar_postgres(sql: str) -> str:
    """Roda uma query de leitura no PostgreSQL. Recusa comandos de escrita."""
    if not settings.database_url:
        return (
            "DATABASE_URL não configurada no .env. "
            "Defina a conexão PostgreSQL para usar esta ferramenta."
        )

    primeira = sql.strip().split(None, 1)[0].lower() if sql.strip() else ""
    if primeira not in _LEITURA_PERMITIDA:
        return (
            f"[recusado] Só permito consultas de leitura ({', '.join(sorted(_LEITURA_PERMITIDA))}). "
            "Alterações no banco são risco ALTO e não passam por esta ferramenta."
        )

    try:
        import psycopg  # import preguiçoso
    except ImportError:
        return (
            "O driver 'psycopg' não está instalado. "
            "Instale com: pip install 'psycopg[binary]'"
        )

    try:
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                colunas = [d.name for d in cur.description] if cur.description else []
                linhas = cur.fetchmany(_MAX_LINHAS)
    except Exception as exc:  # noqa: BLE001 - reportar erro ao modelo
        return f"[erro de banco] {exc}"

    if not colunas:
        return "Consulta executada (sem linhas de resultado)."

    cabecalho = " | ".join(colunas)
    corpo = "\n".join(" | ".join(str(v) for v in linha) for linha in linhas)
    aviso = f"\n[mostrando até {_MAX_LINHAS} linhas]" if len(linhas) == _MAX_LINHAS else ""
    return f"{cabecalho}\n{corpo}{aviso}"
