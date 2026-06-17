import sqlite3

DB_PATH = "escolar.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS alunos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT NOT NULL,
                matricula TEXT NOT NULL,
                email     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS disciplinas (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT NOT NULL,
                codigo    TEXT NOT NULL,
                descricao TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS matriculas (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id      INTEGER NOT NULL,
                disciplina_id INTEGER NOT NULL,
                FOREIGN KEY (aluno_id)      REFERENCES alunos(id),
                FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id),
                UNIQUE(aluno_id, disciplina_id)
            );

            CREATE TABLE IF NOT EXISTS infracoes (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id      INTEGER NOT NULL,
                disciplina_id INTEGER NOT NULL,
                descricao     TEXT NOT NULL,
                gravidade     TEXT NOT NULL,
                data          TEXT NOT NULL,
                FOREIGN KEY (aluno_id)      REFERENCES alunos(id),
                FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id)
            );
        """)