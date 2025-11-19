import Pyro5.api
from Pyro5.api import SerializerBase
from pojo import PlanoSaude, PlanoEmpresa, PlanoIndividual, Vendas, Cooperativa 
import sys

# --- FUNÇÕES AUXILIARES PARA EVITAR ERROS DE TIPO ---
def ler_campo(obj, campo):
    """
    Tenta ler um campo de um objeto. 
    Se o objeto for um Dicionário, lê via ['chave'].
    Se for um Objeto de Classe, lê via .atributo
    """
    if isinstance(obj, dict):
        return obj.get(campo, f"<{campo} não encontrado>")
    else:
        return getattr(obj, campo, f"<{campo} não encontrado>")

def imprimir_plano(p):
    nome = ler_campo(p, 'nome_plano')
    cod = ler_campo(p, 'codigo')
    print(f"  - [{cod}] {nome}")

# --- BLOCO DE REGISTO DE CLASSES ---
# Este bloco ensina o Pyro a converter os objetos para dicionários e vice-versa.
SerializerBase.register_class_to_dict(PlanoSaude, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(PlanoEmpresa, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(PlanoIndividual, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(Vendas, lambda obj: obj.__dict__)
SerializerBase.register_class_to_dict(Cooperativa, lambda obj: obj.__dict__)

SerializerBase.register_dict_to_class("pojo.PlanoSaude", PlanoSaude.from_dict)
SerializerBase.register_dict_to_class("pojo.PlanoEmpresa", PlanoEmpresa.from_dict)
SerializerBase.register_dict_to_class("pojo.PlanoIndividual", PlanoIndividual.from_dict)
SerializerBase.register_dict_to_class("pojo.Vendas", Vendas.from_dict)
SerializerBase.register_dict_to_class("pojo.Cooperativa", Cooperativa.from_dict)
# -----------------------------------------------------------------------

# --- Lógica do Cliente ---
gestor_remoto = Pyro5.api.Proxy("PYRONAME:meu.gestor.planos")

# Criação de um novo plano para teste
plano_novo = PlanoEmpresa(codigo=0, nome_plano="Cliente Corp RMI", preco_base=999.0, is_ativo=True, cnpj="333")

print("--- Teste RMI (Trabalho 2) ---")
try:
    # Print ajuda a debugar
    print(f"Objeto remoto encontrado em: {gestor_remoto._pyroUri}\n")

    print("1. Listando planos atuais...")
    planos_antes = gestor_remoto.listar_planos() 
    print(f"Planos no servidor: {len(planos_antes)}")
    for p in planos_antes:
        imprimir_plano(p)

    print("\n2. Adicionando um novo plano ('Cliente Corp RMI')...")
    plano_adicionado = gestor_remoto.adicionar_plano(plano_novo)
    cod_novo = ler_campo(plano_adicionado, 'codigo')
    print(f"Servidor adicionou o plano com código: {cod_novo}")

    print(f"\n3. Buscando o plano que acabamos de adicionar (código {cod_novo})...")
    plano_encontrado = gestor_remoto.buscar_plano_por_codigo(cod_novo)
    if plano_encontrado:
        print(f"Encontrado: {ler_campo(plano_encontrado, 'nome_plano')}")
    else:
        print("Erro: Plano não encontrado.")

    print(f"\n4. Removendo o plano (código {cod_novo})...")
    sucesso = gestor_remoto.remover_plano_por_codigo(cod_novo)
    print(f"Remoção bem-sucedida: {sucesso}")

    print("\n5. Listando planos finais...")
    planos_depois = gestor_remoto.listar_planos()
    print(f"Planos no servidor agora: {len(planos_depois)}")
    for p in planos_depois:
        imprimir_plano(p)

    print("\n--- Teste concluído com sucesso! ---")

except Exception as e:
    print(f"Erro ao chamar objeto remoto: {e}")
    # Imprime o erro completo para ajudar no debug se necessário
    import traceback
    traceback.print_exc()