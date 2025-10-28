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

    def to_bytes(self) -> bytes:
        """Serializa os atributos selecionados para uma sequência de bytes.

        Serializa: codigo (I - unsigned int), nome_plano (str), preco_base (f - float).
        Usamos um formato fixo para os bytes:
        - 4 bytes para codigo (int)
        - 4 bytes para preco_base (float)
        - 50 bytes (fixos) para nome_plano (string preenchida com espaços)

        O comprimento do nome_plano é arbitrariamente fixado em 50 para
        demonstrar o envio de um tamanho fixo, crucial para streams.
        """
        # Formato: I (unsigned int - 4 bytes), 50s (string de 50 bytes), f (float - 4 bytes)
        # O '<' indica little-endian. Total de bytes por objeto = 4 + 50 + 4 = 58 bytes.
        FORMAT = '<I50sf'

        # Encodificar o nome do plano para 50 bytes, preenchendo com espaços ou truncando
        nome_bytes = self.nome_plano.encode('utf-8')[:50].ljust(50, b' ')

        return struct.pack(FORMAT, self.codigo, nome_bytes, self.preco_base)

    @classmethod
    def from_bytes(cls, data: bytes) -> 'PlanoSaude':
        """Desserializa uma sequência de bytes para um objeto PlanoSaude."""
        FORMAT = '<I50sf'

        # Desempacota os dados
        codigo, nome_bytes, preco_base = struct.unpack(FORMAT, data)

        # Decodifica e remove espaços em branco extras (strip)
        nome_plano = nome_bytes.decode('utf-8').strip()

        # Assume is_ativo como True por padrão (o atributo não foi transmitido, mas é do POJO)
        return cls(codigo=codigo, nome_plano=nome_plano, preco_base=preco_base, is_ativo=True)

    @classmethod
    def get_serial_size(cls) -> int:
        """Retorna o número de bytes usados para gravar os 3 atributos (codigo, nome, preco_base)."""
        return struct.calcsize('<I50sf')


@dataclass
class PlanoEmpresa(PlanoSaude):
    """Subclasse: Plano Empresa"""
    cnpj: str

@dataclass
class PlanoIndividual(PlanoSaude):
    """Subclasse: Plano Individual"""
    cpf_titular: str

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