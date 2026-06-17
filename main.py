from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
import sqlite3

from database import get_conn, init_db
from models import (Aluno, AlunoEntrada, Disciplina, DisciplinaEntrada,
                    Matricula, MatriculaEntrada, Infracao, InfracaoEntrada)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="API Escolar com SQLite", version="1.0.0", lifespan=lifespan)

# ═══════════════════ RAIZ ═══════════════════

@app.get("/")
def raiz():
    return {"mensagem": "API Escolar com SQLite funcionando! 🏫"}

# ═══════════════════ ALUNOS ═══════════════════

@app.post("/alunos", response_model=Aluno, status_code=201)
def criar_aluno(dados: AlunoEntrada):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO alunos (nome, matricula, email) VALUES (?, ?, ?)",
            (dados.nome, dados.matricula, dados.email)
        )
        conn.commit()
    return Aluno(id=cur.lastrowid, **dados.model_dump())

@app.get("/alunos", response_model=List[Aluno])
def listar_alunos():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, nome, matricula, email FROM alunos").fetchall()
    return [Aluno(**dict(r)) for r in rows]

@app.get("/alunos/{id}", response_model=Aluno)
def buscar_aluno(id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, nome, matricula, email FROM alunos WHERE id = ?", (id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return Aluno(**dict(row))

@app.put("/alunos/{id}", response_model=Aluno)
def editar_aluno(id: int, dados: AlunoEntrada):
    with get_conn() as conn:
        res = conn.execute(
            "UPDATE alunos SET nome = ?, matricula = ?, email = ? WHERE id = ?",
            (dados.nome, dados.matricula, dados.email, id)
        )
        conn.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return Aluno(id=id, **dados.model_dump())

@app.delete("/alunos/{id}", status_code=204)
def remover_aluno(id: int):
    with get_conn() as conn:
        res = conn.execute("DELETE FROM alunos WHERE id = ?", (id,))
        conn.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

# ═══════════════════ DISCIPLINAS ═══════════════════

@app.post("/disciplinas", response_model=Disciplina, status_code=201)
def criar_disciplina(dados: DisciplinaEntrada):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO disciplinas (nome, codigo, descricao) VALUES (?, ?, ?)",
            (dados.nome, dados.codigo, dados.descricao)
        )
        conn.commit()
    return Disciplina(id=cur.lastrowid, **dados.model_dump())

@app.get("/disciplinas", response_model=List[Disciplina])
def listar_disciplinas():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, nome, codigo, descricao FROM disciplinas").fetchall()
    return [Disciplina(**dict(r)) for r in rows]

@app.get("/disciplinas/{id}", response_model=Disciplina)
def buscar_disciplina(id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, nome, codigo, descricao FROM disciplinas WHERE id = ?", (id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return Disciplina(**dict(row))

@app.put("/disciplinas/{id}", response_model=Disciplina)
def editar_disciplina(id: int, dados: DisciplinaEntrada):
    with get_conn() as conn:
        res = conn.execute(
            "UPDATE disciplinas SET nome = ?, codigo = ?, descricao = ? WHERE id = ?",
            (dados.nome, dados.codigo, dados.descricao, id)
        )
        conn.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return Disciplina(id=id, **dados.model_dump())

@app.delete("/disciplinas/{id}", status_code=204)
def remover_disciplina(id: int):
    with get_conn() as conn:
        res = conn.execute("DELETE FROM disciplinas WHERE id = ?", (id,))
        conn.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

# ═══════════════════ MATRÍCULAS ═══════════════════

@app.post("/matriculas", response_model=Matricula, status_code=201)
def matricular_aluno(dados: MatriculaEntrada):
    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO matriculas (aluno_id, disciplina_id) VALUES (?, ?)",
                (dados.aluno_id, dados.disciplina_id)
            )
            conn.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=409, detail="Aluno já matriculado nesta disciplina")
        raise HTTPException(status_code=404, detail="Aluno ou disciplina não encontrado")
    return Matricula(id=cur.lastrowid, **dados.model_dump())

@app.get("/alunos/{id}/disciplinas", response_model=List[Disciplina])
def disciplinas_do_aluno(id: int):
    with get_conn() as conn:
        if conn.execute("SELECT id FROM alunos WHERE id = ?", (id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        rows = conn.execute("""
            SELECT d.id, d.nome, d.codigo, d.descricao
            FROM disciplinas d
            JOIN matriculas m ON m.disciplina_id = d.id
            WHERE m.aluno_id = ?
        """, (id,)).fetchall()
    return [Disciplina(**dict(r)) for r in rows]

@app.get("/disciplinas/{id}/alunos", response_model=List[Aluno])
def alunos_da_disciplina(id: int):
    with get_conn() as conn:
        if conn.execute("SELECT id FROM disciplinas WHERE id = ?", (id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada")
        rows = conn.execute("""
            SELECT a.id, a.nome, a.matricula, a.email
            FROM alunos a
            JOIN matriculas m ON m.aluno_id = a.id
            WHERE m.disciplina_id = ?
        """, (id,)).fetchall()
    return [Aluno(**dict(r)) for r in rows]

@app.delete("/matriculas/{id}", status_code=204)
def cancelar_matricula(id: int):
    with get_conn() as conn:
        res = conn.execute("DELETE FROM matriculas WHERE id = ?", (id,))
        conn.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

# ═══════════════════ INFRAÇÕES ═══════════════════

@app.post("/infracoes", response_model=Infracao, status_code=201)
def registrar_infracao(dados: InfracaoEntrada):
    data = datetime.now().isoformat()
    try:
        with get_conn() as conn:
            cur = conn.execute(
                """INSERT INTO infracoes
                   (aluno_id, disciplina_id, descricao, gravidade, data)
                   VALUES (?, ?, ?, ?, ?)""",
                (dados.aluno_id, dados.disciplina_id, dados.descricao, dados.gravidade, data)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=404, detail="Aluno ou disciplina não encontrado")
    return Infracao(id=cur.lastrowid, data=data, **dados.model_dump())

@app.get("/infracoes", response_model=List[Infracao])
def listar_infracoes():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, aluno_id, disciplina_id, descricao, gravidade, data FROM infracoes"
        ).fetchall()
    return [Infracao(**dict(r)) for r in rows]

@app.get("/infracoes/{id}", response_model=Infracao)
def buscar_infracao(id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, aluno_id, disciplina_id, descricao, gravidade, data FROM infracoes WHERE id = ?", (id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Infração não encontrada")
    return Infracao(**dict(row))

@app.get("/alunos/{id}/infracoes", response_model=List[Infracao])
def infracoes_do_aluno(id: int):
    with get_conn() as conn:
        if conn.execute("SELECT id FROM alunos WHERE id = ?", (id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        rows = conn.execute(
            "SELECT id, aluno_id, disciplina_id, descricao, gravidade, data FROM infracoes WHERE aluno_id = ?",
            (id,)
        ).fetchall()
    return [Infracao(**dict(r)) for r in rows]

@app.get("/disciplinas/{id}/infracoes", response_model=List[Infracao])
def infracoes_da_disciplina(id: int):
    with get_conn() as conn:
        if conn.execute("SELECT id FROM disciplinas WHERE id = ?", (id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada")
        rows = conn.execute(
            "SELECT id, aluno_id, disciplina_id, descricao, gravidade, data FROM infracoes WHERE disciplina_id = ?",
            (id,)
        ).fetchall()
    return [Infracao(**dict(r)) for r in rows]

@app.put("/infracoes/{id}", response_model=Infracao)
def editar_infracao(id: int, dados: InfracaoEntrada):
    with get_conn() as conn:
        row = conn.execute("SELECT data FROM infracoes WHERE id = ?", (id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Infração não encontrada")
        conn.execute(
            """UPDATE infracoes
               SET aluno_id = ?, disciplina_id = ?, descricao = ?, gravidade = ?
               WHERE id = ?""",
            (dados.aluno_id, dados.disciplina_id, dados.descricao, dados.gravidade, id)
        )
        conn.commit()
    return Infracao(id=id, data=row["data"], **dados.model_dump())

@app.delete("/infracoes/{id}", status_code=204)
def remover_infracao(id: int):
    with get_conn() as conn:
        res = conn.execute("DELETE FROM infracoes WHERE id = ?", (id,))
        conn.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Infração não encontrada")