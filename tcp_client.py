# tcp_client.py
import socket
from streams import PlanoSaudeStreamReader, PlanoSaudeStreamWriter
from pojo import PlanoEmpresa  # Vamos enviar um PlanoEmpresa

# -----------------------------------------------------------------
# ITEM 4: Cliente com Sockets e Serialização (Struct)
# -----------------------------------------------------------------

# Configurações do servidor para o qual vamos conectar
HOST = '127.0.0.1'  # O IP do servidor (localhost)
PORT = 65432        # A porta do servidor

# Cria o POJO que o cliente quer enviar
plano_novo = PlanoEmpresa(codigo=0, nome_plano="Cliente Corp", preco_base=999.0, is_ativo=True, cnpj="333")
lista_para_enviar = [plano_novo]

# Cria o objeto socket TCP/IP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # Tenta se conectar ao endereço e porta do servidor
        s.connect((HOST, PORT))
        print("Cliente: Conectado ao servidor.")
        
        # --- CORREÇÃO ---
        # "Embrulha" o socket 's' em objetos do tipo arquivo.
        # 'wb' para escrita, 'rb' para leitura.
        # Estes objetos têm os métodos .write() e .read()
        file_writer = s.makefile('wb')
        file_reader = s.makefile('rb')
        # ----------------

        # -----------------------------------------------------------------
        # Teste (2.b.iii) e Item (4): Cliente empacota request
        # -----------------------------------------------------------------
        # Instancia o Writer, usando o 'file_writer' (e não o 's')
        writer = PlanoSaudeStreamWriter(file_writer)
        # Envia a lista (com um plano) para o servidor
        writer.write_planos(lista_para_enviar)
        print(f"Cliente: Enviou {len(lista_para_enviar)} plano(s) para o servidor.")

        # -----------------------------------------------------------------
        # Teste (3.d) e Item (4): Cliente desempacota reply
        # -----------------------------------------------------------------
        print("Cliente: Aguardando resposta do servidor...")
        # Instancia o Reader, usando o 'file_reader' (e não o 's')
        reader = PlanoSaudeStreamReader(file_reader)
        # Lê a lista de planos enviada DE VOLTA pelo servidor
        resposta_servidor = reader.read_planos()
        
        print(f"Cliente: Resposta do servidor recebida ({len(resposta_servidor)} planos):")
        for p in resposta_servidor:
            print(f"  - [RESPOSTA] {p}")

    except ConnectionRefusedError:
        print(f"Erro: Não foi possível conectar a {HOST}:{PORT}.")
        print("Verifique se o 'tcp_server.py' está em execução.")
    except Exception as e:
        print(f"Erro durante a comunicação: {e}")

    # file_reader e file_writer são fechados automaticamente
    # quando o bloco 'with s:' termina.