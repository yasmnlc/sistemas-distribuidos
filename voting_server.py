# voting_server.py
import socket
import threading
import json
import time
import struct # Necessário para o setup do multicast

# --- Configurações do Servidor ---
HOST_TCP = '0.0.0.0'  # Ouve em todas as interfaces
PORT_TCP = 50007      # Porta para TCP (Login, Votos) [cite: 41]

# --- Configurações do Multicast (UDP) ---
MCAST_GROUP = '224.1.1.1' # Endereço de grupo multicast
MCAST_PORT = 50008        # Porta para UDP (Notas) [cite: 42]

# --- "Banco de Dados" Global (Simulado) ---
# Dicionário de candidatos: {id: {"nome": "Nome"}}
candidatos = {
    1: {"nome": "Candidato A"},
    2: {"nome": "Candidato B"}
}
# Dicionário para contar votos: {id_candidato: contagem}
votos = {1: 0, 2: 0}
# Usuários válidos: {username: {"senha": "123", "tipo": "voter" or "admin"}}
usuarios = {
    "votante1": {"senha": "123", "tipo": "voter"},
    "votante2": {"senha": "abc", "tipo": "voter"},
    "admin": {"senha": "admin123", "tipo": "admin"}
}
# Conjunto de usuários logados (para controle)
usuarios_logados = set()
# Flag para controlar o período de votação [cite: 38]
votacao_aberta = True
# Lock para proteger o acesso às variáveis globais (necessário para multi-thread)
data_lock = threading.Lock()

# --- Funções de Ajuda ---

def enviar_nota_multicast(mensagem: str):
    """Envia uma mensagem para o grupo multicast UDP. [cite: 42]"""
    print(f"MULTICAST: Enviando nota: '{mensagem}'")
    try:
        # Cria um socket UDP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            # Define o "Time To Live" (TTL) dos pacotes
            # 1 = apenas na rede local
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            # Envia a mensagem (encodada) para o grupo e porta multicast
            s.sendto(mensagem.encode('utf-8'), (MCAST_GROUP, MCAST_PORT))
    except Exception as e:
        print(f"Erro ao enviar multicast: {e}")

def encerrar_votacao(tempo_segundos: int):
    """Thread timer que encerra a votação após um tempo. [cite: 38]"""
    global votacao_aberta
    print(f"Votação será encerrada em {tempo_segundos} segundos.")
    # Aguarda o tempo definido
    time.sleep(tempo_segundos)
    
    # --- Calcula os resultados ---
    print(">>> VOTAÇÃO ENCERRADA <<<")
    # Protege o acesso aos dados globais
    with data_lock:
        votacao_aberta = False # Impede novos votos
        
        # Encontra o ganhador
        ganhador_id = max(votos, key=votos.get)
        total_votos = sum(votos.values())
        
        # Prepara a mensagem de resultado
        resultado_msg = f"VOTAÇÃO ENCERRADA. Total de Votos: {total_votos}. "
        resultado_msg += f"Ganhador: {candidatos[ganhador_id]['nome']} com {votos[ganhador_id]} votos. "
        resultado_msg += f"Placar: {votos}"

    # Envia os resultados finais para todos via multicast
    enviar_nota_multicast(resultado_msg)

# --- Thread de Handler do Cliente (TCP) ---
def handle_client_tcp(conn: socket.socket, addr):
    """Função executada por thread para cada cliente TCP conectado. [cite: 42]"""
    print(f"TCP: Nova conexão de {addr}")
    user_info = None # Armazena quem é este cliente
    
    try:
        # Loop principal de comunicação com este cliente
        while True:
            # Aguarda receber dados (até 1024 bytes)
            data = conn.recv(1024)
            # Se não receber dados, o cliente desconectou
            if not data:
                break 
                
            # Desserializa a mensagem JSON recebida
            try:
                request = json.loads(data.decode('utf-8'))
                print(f"TCP: Recebido de {addr}: {request}")
            except json.JSONDecodeError:
                conn.sendall(json.dumps({"status": "erro", "msg": "JSON inválido"}).encode('utf-8'))
                continue

            # Processa a 'acao' solicitada
            acao = request.get('acao')
            
            # 1. Ação de Login (Votante e Admin) [cite: 39, 40]
            if acao == 'login':
                username = request.get('usuario')
                senha = request.get('senha')
                # Verifica se o usuário existe e a senha está correta
                if username in usuarios and usuarios[username]['senha'] == senha:
                    user_info = usuarios[username]
                    # Adiciona ao conjunto de logados (protegido por lock)
                    with data_lock:
                        usuarios_logados.add(username)
                    # Resposta de sucesso (JSON)
                    reply = {"status": "ok", "tipo": user_info['tipo']}
                else:
                    reply = {"status": "erro", "msg": "Usuário ou senha inválidos"}
                conn.sendall(json.dumps(reply).encode('utf-8'))

            # Se não estiver logado, ignora outras ações
            elif not user_info:
                reply = {"status": "erro", "msg": "Não autenticado"}
                conn.sendall(json.dumps(reply).encode('utf-8'))

            # 2. Ação de Listar Candidatos (Votante) [cite: 39]
            elif acao == 'get_candidatos' and user_info['tipo'] == 'voter':
                # Responde com a lista global de candidatos
                with data_lock:
                    reply = {"status": "ok", "candidatos": candidatos}
                conn.sendall(json.dumps(reply).encode('utf-8'))

            # 3. Ação de Votar (Votante) [cite: 39]
            elif acao == 'votar' and user_info['tipo'] == 'voter':
                # Protege o acesso às flags e contagem de votos
                with data_lock:
                    if votacao_aberta:
                        try:
                            candidato_id = int(request.get('id_candidato'))
                            if candidato_id in votos:
                                votos[candidato_id] += 1
                                reply = {"status": "ok", "msg": "Voto computado!"}
                            else:
                                reply = {"status": "erro", "msg": "ID de candidato inválido"}
                        except (ValueError, TypeError):
                            reply = {"status": "erro", "msg": "ID deve ser um número"}
                    else:
                        reply = {"status": "erro", "msg": "Votação encerrada!"}
                conn.sendall(json.dumps(reply).encode('utf-8'))

            # 4. Ação de Adicionar Candidato (Admin) 
            elif acao == 'add_candidato' and user_info['tipo'] == 'admin':
                nome_candidato = request.get('nome')
                if nome_candidato:
                    with data_lock:
                        # Cria um novo ID (simplesmente o próximo número)
                        novo_id = max(candidatos.keys()) + 1
                        candidatos[novo_id] = {"nome": nome_candidato}
                        votos[novo_id] = 0 # Inicia contagem de votos
                        reply = {"status": "ok", "msg": f"Candidato '{nome_candidato}' adicionado com ID {novo_id}"}
                else:
                    reply = {"status": "erro", "msg": "Nome do candidato não fornecido"}
                conn.sendall(json.dumps(reply).encode('utf-8'))
            
            # 5. Ação de Enviar Nota (Admin) -> (Gera UDP Multicast) [cite: 40, 42]
            elif acao == 'enviar_nota' and user_info['tipo'] == 'admin':
                mensagem_nota = request.get('nota')
                if mensagem_nota:
                    # Chama a função que envia a nota para TODOS via UDP
                    enviar_nota_multicast(f"[ADMIN] {mensagem_nota}")
                    reply = {"status": "ok", "msg": "Nota enviada para todos."}
                else:
                    reply = {"status": "erro", "msg": "Mensagem da nota está vazia"}
                conn.sendall(json.dumps(reply).encode('utf-8'))
            
            # Ação desconhecida
            else:
                reply = {"status": "erro", "msg": "Ação desconhecida ou não permitida"}
                conn.sendall(json.dumps(reply).encode('utf-8'))
                
    except (ConnectionResetError, BrokenPipeError):
        # Ocorre quando o cliente fecha a conexão abruptamente
        print(f"TCP: Conexão com {addr} perdida.")
    finally:
        # Garante que o usuário seja removido da lista de logados
        if user_info and user_info['usuario'] in usuarios_logados:
            with data_lock:
                usuarios_logados.remove(user_info['usuario'])
        # Fecha a conexão TCP com este cliente
        conn.close()
        print(f"TCP: Conexão com {addr} fechada.")

# --- Função Principal (Main) do Servidor ---
def main():
    # 1. Inicia a thread do timer da votação [cite: 38]
    # (Definido para 120 segundos = 2 minutos)
    timer_thread = threading.Thread(target=encerrar_votacao, args=(600,), daemon=True)
    timer_thread.start()

    # 2. Configura e inicia o servidor TCP [cite: 41]
    # (Usamos o 'with' para garantir que o socket será fechado)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        # Permite que o servidor re-use o endereço imediatamente
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Vincula o socket ao host e porta TCP
        tcp_socket.bind((HOST_TCP, PORT_TCP))
        # Começa a escutar por conexões
        tcp_socket.listen()
        print(f"Servidor TCP (Votação) ouvindo em {HOST_TCP}:{PORT_TCP}")

        # 3. Loop principal para aceitar novas conexões TCP
        while True:
            try:
                # Aceita uma nova conexão
                conn, addr = tcp_socket.accept()
                # Cria uma nova thread para cuidar desse cliente [cite: 42]
                client_thread = threading.Thread(target=handle_client_tcp, args=(conn, addr), daemon=True)
                # Inicia a thread
                client_thread.start()
            except KeyboardInterrupt:
                print("Servidor encerrando...")
                break # Sai do loop se (Ctrl+C) for pressionado
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")

if __name__ == "__main__":
    main()