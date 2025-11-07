import Pyro5.api
from Pyro5.api import SerializerBase # <-- 1. IMPORTAR SerializerBase
from pojo import PlanoSaude, PlanoEmpresa, PlanoIndividual, Vendas, Cooperativa 

# --- 2. BLOCO DE REGISTO DE CLASSES (MÉTODO CORRETO E DEFINITIVO) ---
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

# --- O resto do seu código de cliente (sem alterações) ---
gestor_remoto = Pyro5.api.Proxy("PYRONAME:meu.gestor.planos")
plano_novo = PlanoEmpresa(codigo=0, nome_plano="Cliente Corp RMI", preco_base=999.0, is_ativo=True, cnpj="333")
print("--- Teste RMI (Trabalho 2) ---")
print(f"Objeto remoto encontrado em: {gestor_remoto._pyroUri}\n")
try:
    print("1. Listando planos atuais...")
    planos_antes = gestor_remoto.listar_planos() 
    print(f"Planos no servidor: {len(planos_antes)}")
    for p in planos_antes:
        print(f"  - {p.nome_plano}")
    print("\n2. Adicionando um novo plano ('Cliente Corp RMI')...")
    plano_adicionado = gestor_remoto.adicionar_plano(plano_novo)
    print(f"Servidor adicionou o plano com código: {plano_adicionado.codigo}")
    print(f"\n3. Buscando o plano que acabamos de adicionar (código {plano_adicionado.codigo})...")
    plano_encontrado = gestor_remoto.buscar_plano_por_codigo(plano_adicionado.codigo)
    print(f"Encontrado: {plano_encontrado.nome_plano}")
    print(f"\n4. Removendo o plano (código {plano_adicionado.codigo})...")
    sucesso = gestor_remoto.remover_plano_por_codigo(plano_adicionado.codigo)
    print(f"Remoção bem-sucedida: {sucesso}")
    print("\n5. Listando planos finais...")
    planos_depois = gestor_remoto.listar_planos()
    print(f"Planos no servidor agora: {len(planos_depois)}")
    for p in planos_depois:
        print(f"  - {p.nome_plano}")
    print("\n--- Teste concluído com sucesso! ---")
except Exception as e:
    print(f"Erro ao chamar objeto remoto: {e}")