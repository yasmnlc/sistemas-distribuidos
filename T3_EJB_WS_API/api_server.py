from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
from service import GestorPlanos
from pojo import PlanoSaude, PlanoEmpresa, PlanoIndividual

app = FastAPI()
gestor = GestorPlanos()

# --- Adaptação dos POJOs para Pydantic (para validação automática na API) ---
# O FastAPI prefere Pydantic, mas podemos aceitar dicts e converter manualmente
# para reutilizar sua lógica do service.py que já trata dicts.

class PlanoRequest(BaseModel):
    tipo: str  # "Empresa" ou "Individual"
    nome_plano: str
    preco_base: float
    is_ativo: bool
    cnpj: Optional[str] = None
    cpf_titular: Optional[str] = None

# --- Endpoints da API (Substituem os métodos expostos no RMI) ---

@app.get("/planos")
def listar_planos():
    """Retorna todos os planos (Substitui gestor.listar_planos)"""
    return gestor.listar_planos()

@app.get("/planos/{codigo}")
def buscar_plano(codigo: int):
    """Busca um plano específico"""
    plano = gestor.buscar_plano_por_codigo(codigo)
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return plano

@app.post("/planos")
def adicionar_plano(plano: PlanoRequest):
    """Adiciona um novo plano"""
    dados = plano.dict()
    novo_plano = gestor.adicionar_plano(dados)
    return novo_plano

@app.delete("/planos/{codigo}")
def remover_plano(codigo: int):
    """Remove um plano"""
    sucesso = gestor.remover_plano_por_codigo(codigo)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Plano não encontrado para remoção")
    return {"status": "removido", "codigo": codigo}

# Para rodar: uvicorn api_server:app --reload