from dataclasses import dataclass
from typing import List, Any
import struct
import json
import sys

# ------------------------------------------------------------------
# 1. Classes do tipo POJO (Representam as informações do serviço)
#    Usamos 'dataclass' para simplificar o POJO em Python.
# -----------------------------------------------------------------

@dataclass
class PlanoSaude:
    """Superclasse: Plano de Saúde"""
    codigo: int
    nome_plano: str
    preco_base: float
    is_ativo: bool

    @staticmethod
    def from_dict(classname, d):
        return PlanoSaude(**d)

@dataclass
class PlanoEmpresa(PlanoSaude):
    """Subclasse: Plano Empresa"""
    cnpj: str

    @staticmethod
    def from_dict(classname, d):
        return PlanoEmpresa(**d)

@dataclass
class PlanoIndividual(PlanoSaude):
    """Subclasse: Plano Individual"""
    cpf_titular: str

    @staticmethod
    def from_dict(classname, d):
        return PlanoIndividual(**d)

@dataclass
class PlanoEnfermaria(PlanoSaude):
    """Subclasse: Plano Enfermaria"""
    tipo_acomodacao: str = "Enfermaria"

@dataclass
class PlanoApartamento(PlanoSaude):
    """Subclasse: Plano Apartamento"""
    tipo_acomodacao: str = "Apartamento"

# Outras classes POJO (para um conjunto de qualquer POJO)

@dataclass
class Vendas:
    """Classe Interface/Agregação: Vendas"""
    vendedor_nome: str
    plano_vendido: PlanoSaude

@dataclass
class Cooperativa:
    """Classe Agregação: Cooperativa"""
    nome: str
    planos_oferecidos: List[PlanoSaude]