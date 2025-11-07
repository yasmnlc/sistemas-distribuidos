from pojo import PlanoSaude, PlanoEmpresa, PlanoIndividual
from typing import List

# ----------------------------------------------------
# Classes de modelo que implementam serviços
# ----------------------------------------------------

class GestorPlanos:
    """Classe de modelo que implementa o serviço de Gestão de Planos de Saúde."""
    
    def __init__(self):
        self.planos_ativos: List[PlanoSaude] = []
        self.last_codigo = 0

    def adicionar_plano(self, plano: PlanoSaude) -> PlanoSaude:
        """Adiciona um novo plano ao sistema."""
        self.last_codigo += 1
        plano.codigo = self.last_codigo
        self.planos_ativos.append(plano)
        print(f"Plano '{plano.nome_plano}' adicionado com código {plano.codigo}.")
        return plano

    def buscar_plano_por_codigo(self, codigo: int) -> PlanoSaude | None:
        """Busca um plano pelo código."""
        print(f"Serviço: Buscando plano com código {codigo}.")
        for plano in self.planos_ativos:
            if plano.codigo == codigo:
                return plano
        return None

    # --- MÉTODOS ADICIONADOS PARA O TRABALHO 2 ---

    # NOVO MÉTODO 3
    def listar_planos(self) -> List[PlanoSaude]:
        """
        (Método Remoto 3) Retorna a lista completa de planos ativos.
        """
        print("Serviço RMI: Método 'listar_planos' invocado.")
        return self.planos_ativos
        
    # NOVO MÉTODO 4
    def remover_plano_por_codigo(self, codigo: int) -> bool:
        """
        (Método Remoto 4) Remove um plano pelo código e retorna True/False.
        """
        print(f"Serviço RMI: Método 'remover_plano_por_codigo' invocado para o código {codigo}.")
        plano_para_remover = self.buscar_plano_por_codigo(codigo)
        
        if plano_para_remover:
            self.planos_ativos.remove(plano_para_remover)
            print(f"Plano código {codigo} removido com sucesso.")
            return True
        
        print(f"Plano código {codigo} não encontrado.")
        return False

class ServicoVendas:
    """Classe de modelo que implementa o serviço de Vendas (Interface)."""
    
    def __init__(self, gestor_planos: GestorPlanos):
        self.gestor = gestor_planos

    def realizar_venda(self, tipo_plano: str, nome_cliente: str) -> PlanoSaude:
        """Simula a venda de um plano de saúde."""
        if tipo_plano == "Empresa":
            novo_plano = PlanoEmpresa(codigo=0, nome_plano=f"Empresa - {nome_cliente}", preco_base=500.00, is_ativo=True, cnpj="99.999.999/0001-99")
        elif tipo_plano == "Individual":
            novo_plano = PlanoIndividual(codigo=0, nome_plano=f"Individual - {nome_cliente}", preco_base=150.00, is_ativo=True, cpf_titular="111.111.111-11")
        else:
            raise ValueError("Tipo de plano inválido para venda.")
            
        return self.gestor.adicionar_plano(novo_plano)