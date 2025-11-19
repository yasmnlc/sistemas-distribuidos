import Pyro5.api
from Pyro5.api import SerializerBase 
from service import GestorPlanos
from pojo import PlanoSaude, PlanoEmpresa, PlanoIndividual, Vendas, Cooperativa 

# --- BLOCO DE REGISTO DE CLASSES ---
# Este bloco ensina o Pyro a converter os objetos para dicionários e vice-versa.
SerializerBase.register_class_to_dict(PlanoSaude, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(PlanoEmpresa, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(PlanoIndividual, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(Vendas, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(Cooperativa, lambda obj: obj.__dict__)

# Criar um objeto a partir de um dicionário
SerializerBase.register_dict_to_class("pojo.PlanoSaude", PlanoSaude.from_dict)
SerializerBase.register_dict_to_class("pojo.PlanoEmpresa", PlanoEmpresa.from_dict)
SerializerBase.register_dict_to_class("pojo.PlanoIndividual", PlanoIndividual.from_dict)
SerializerBase.register_dict_to_class("pojo.Vendas", Vendas.from_dict)
SerializerBase.register_dict_to_class("pojo.Cooperativa", Cooperativa.from_dict)
# -----------------------------------------------------------------------

# "Embrulha" a sua classe GestorPlanos para expô-la ao Pyro
GestorPlanos_Exposto = Pyro5.api.expose(GestorPlanos)

# --- Configuração do Servidor RMI ---
def main():
    gestor = GestorPlanos_Exposto()
    gestor.adicionar_plano(PlanoIndividual(codigo=0, nome_plano="Plano Base Servidor RMI", preco_base=100.0, is_ativo=True, cpf_titular="000"))
    daemon = Pyro5.api.Daemon()             
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(gestor, "meu.gestor.planos")   
    ns.register("meu.gestor.planos", uri)
    print("Servidor RMI pronto. Objeto registrado como 'meu.gestor.planos'")
    daemon.requestLoop()

if __name__ == "__main__":
    main()