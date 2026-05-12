# db.py
from contextlib import contextmanager
import sqlite3
from typing import Any, Iterator, List, Optional, Sequence

DB_PATH: str = "ecommerce.db"
DEFAULT_TIMEOUT: float = 5.0  # segundos

class DatabaseError(Exception):
    """Excepción genérica para errores de base de datos."""
    pass

@contextmanager
def get_db_connection(db_path: str = DB_PATH, timeout: float = DEFAULT_TIMEOUT) -> Iterator[sqlite3.Connection]:
    """
    Context manager que abre una conexión SQLite, configura row_factory,
    y garantiza commit/rollback y cierre.
    """
    conn = sqlite3.connect(db_path, timeout=timeout, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def fetch_one(sql: str, params: Sequence[Any] = (), db_path: str = DB_PATH) -> Optional[sqlite3.Row]:
    """Ejecuta una consulta y devuelve la primera fila o None."""
    try:
        with get_db_connection(db_path) as conn:
            cur = conn.execute(sql, tuple(params))
            return cur.fetchone()
    except sqlite3.Error as e:
        raise DatabaseError(f"fetch_one error: {e}") from e

def fetch_all(sql: str, params: Sequence[Any] = (), db_path: str = DB_PATH) -> List[sqlite3.Row]:
    """Ejecuta una consulta y devuelve todas las filas (lista vacía si no hay)."""
    try:
        with get_db_connection(db_path) as conn:
            cur = conn.execute(sql, tuple(params))
            return cur.fetchall()
    except sqlite3.Error as e:
        raise DatabaseError(f"fetch_all error: {e}") from e

def execute(sql: str, params: Sequence[Any] = (), db_path: str = DB_PATH) -> Optional[int]:
    """
    Ejecuta una sentencia (INSERT/UPDATE/DELETE) y devuelve lastrowid.
    Para UPDATE/DELETE lastrowid puede ser 0; para INSERT devuelve el id.
    """
    try:
        with get_db_connection(db_path) as conn:
            cur = conn.execute(sql, tuple(params))
            return cur.lastrowid
    except sqlite3.IntegrityError as e:
        # errores de constraint (p. ej. UNIQUE) se exponen claramente
        raise DatabaseError(f"Integrity error: {e}") from e
    except sqlite3.Error as e:
        raise DatabaseError(f"execute error: {e}") from e

def execute_many(sql: str, seq_of_params: Sequence[Sequence[Any]], db_path: str = DB_PATH) -> None:
    """
    Ejecuta muchas sentencias parametrizadas (ej. inserciones en lote).
    No devuelve nada; lanza DatabaseError en caso de fallo.
    """
    try:
        with get_db_connection(db_path) as conn:
            conn.executemany(sql, [tuple(p) for p in seq_of_params])
    except sqlite3.Error as e:
        raise DatabaseError(f"execute_many error: {e}") from e

def exec_script(sql_script: str, db_path: str = DB_PATH) -> None:
    """
    Ejecuta un script SQL completo (varias sentencias). Útil para inicializar la BD.
    """
    try:
        with get_db_connection(db_path) as conn:
            conn.executescript(sql_script)
    except sqlite3.Error as e:
        raise DatabaseError(f"exec_script error: {e}") from e

def init_db_from_file(sql_file_path: str, db_path: str = DB_PATH) -> None:
    """
    Lee un archivo .sql y lo ejecuta como script para crear tablas/seed.
    """
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            script = f.read()
    except OSError as e:
        raise DatabaseError(f"No se pudo leer el archivo SQL: {e}") from e

    exec_script(script, db_path=db_path)

