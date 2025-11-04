# tcp_server.py
import socket
from streams import PlanoSaudeStreamReader, PlanoSaudeStreamWriter
from pojo import PlanoIndividual
from service import GestorPlanos  # Usa seu serviço original

# -----------------------------------------------------------------
# ITEM 4: Servidor com Sockets e Serialização (Struct)
# -----------------------------------------------------------------

# Instancia o serviço de gestão de planos
gestor = GestorPlanos()
# Adiciona um plano base para o gestor ter algum dado
gestor.adicionar_plano(PlanoIndividual(codigo=0, nome_plano="Plano Base Servidor", preco_base=100.0, is_ativo=True, cpf_titular="000"))

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP (localhost)
PORT = 65432        # Porta para ouvir

# Cria o objeto socket TCP/IP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Vincula o socket ao endereço e porta definidos
    s.bind((HOST, PORT))
    # Coloca o socket em modo de escuta, aguardando conexões
    s.listen()
    print(f"Servidor ouvindo em {HOST}:{PORT}")
    
    # Loop infinito para aceitar conexões
    while True:
        # Aceita uma nova conexão (bloqueia até um cliente conectar)
        # conn = o novo socket usado para falar com o cliente
        # addr = o endereço (IP, porta) do cliente
        conn, addr = s.accept()
        
        # Bloco 'with' garante que o socket 'conn' será fechado no final
        with conn:
            print(f"Conectado por {addr}")
            
            # --- CORREÇÃO ---
            # "Embrulha" o socket 'conn' em objetos do tipo arquivo.
            # 'rb' = Read Binary (para leitura)
            # 'wb' = Write Binary (para escrita)
            # Estes objetos 'file_reader' e 'file_writer' agora têm 
            # os métodos .read() e .write() que as classes de stream esperam.
            file_reader = conn.makefile('rb')
            file_writer = conn.makefile('wb')
            # ----------------

            # -----------------------------------------------------------------
            # Teste (3.d) e Item (4): Servidor desempacota request
            # -----------------------------------------------------------------
            print("Servidor: Aguardando dados do cliente...")
            # Instancia o Reader, usando o 'file_reader' (e não o 'conn')
            reader = PlanoSaudeStreamReader(file_reader)
            # Lê a lista de planos enviada pelo cliente
            planos_recebidos = reader.read_planos()
            
            print(f"Servidor: {len(planos_recebidos)} plano(s) recebido(s):")
            for p in planos_recebidos:
                print(f"  - [RECEBIDO] {p}")
                # Adiciona os planos recebidos ao gestor de planos
                gestor.adicionar_plano(p)
            
            print(f"Servidor: Total de planos agora: {len(gestor.planos_ativos)}")

            # -----------------------------------------------------------------
            # Teste (2.b.iii) e Item (4): Servidor empacota reply
            # -----------------------------------------------------------------
            print("Servidor: Enviando lista atualizada de volta...")
            # Instancia o Writer, usando o 'file_writer' (e não o 'conn')
            writer = PlanoSaudeStreamWriter(file_writer)
            # Envia a lista COMPLETA de planos ativos como resposta
            writer.write_planos(gestor.planos_ativos)
            print("Servidor: Resposta enviada.")

            # file_reader e file_writer são fechados automaticamente 
            # quando o bloco 'with conn:' termina.