from pydantic import BaseModel

class AlunoEntrada(BaseModel):
    nome: str
    matricula: str
    email: str

class Aluno(AlunoEntrada):
    id: int

class DisciplinaEntrada(BaseModel):
    nome: str
    codigo: str
    descricao: str

class Disciplina(DisciplinaEntrada):
    id: int

class MatriculaEntrada(BaseModel):
    aluno_id: int
    disciplina_id: int

class Matricula(MatriculaEntrada):
    id: int

class InfracaoEntrada(BaseModel):
    aluno_id: int
    disciplina_id: int
    descricao: str
    gravidade: str

class Infracao(InfracaoEntrada):
    id: int
    data: str