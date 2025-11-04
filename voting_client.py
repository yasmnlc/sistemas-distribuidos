# voting_client.py
import socket
import threading
import json
import sys
import struct # Para setup do multicast

# --- Configurações ---
SERVER_HOST = '127.0.0.1' # IP do servidor TCP
SERVER_PORT = 50007       # Porta do servidor TCP

MCAST_GROUP = '224.1.1.1' # Mesmo grupo multicast do servidor
MCAST_PORT = 50008        # Mesma porta multicast do servidor

# --- Thread para Ouvir UDP Multicast ---
def listen_for_multicast_notes():
    """Thread que ouve passivamente por notas do admin via UDP. """
    # Cria um socket UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        try:
            # Permite que múltiplos sockets na mesma máquina ouçam o mesmo grupo
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Vincula o socket à porta multicast, em TODAS as interfaces ('0.0.0.0')
            sock.bind(('', MCAST_PORT))
            
            # Prepara a estrutura 'mreq' para se juntar ao grupo multicast
            # 1. IP do grupo multicast
            # 2. IP da interface local (INADDR_ANY = qualquer uma)
            mreq = struct.pack("4sl", socket.inet_aton(MCAST_GROUP), socket.INADDR_ANY)
            
            # Pede ao kernel para adicionar este socket ao grupo multicast
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            print(f"[Multicast Listener iniciado. Ouvindo notas em {MCAST_GROUP}:{MCAST_PORT}]")
        except OSError as e:
            print(f"Erro ao 'bindar' socket multicast (porta {MCAST_PORT} já em uso?): {e}")
            return

        # Loop infinito para receber mensagens multicast
        while True:
            # Aguarda (bloqueia) até receber um pacote (até 1024 bytes)
            data, addr = sock.recvfrom(1024)
            # Imprime a nota recebida, e re-exibe o prompt ('> ')
            print(f"\n*** NOTA DO SISTEMA ***\n{data.decode('utf-8')}\n> ", end="")

# --- Funções Auxiliares (Comunicação TCP) ---

def send_request(sock: socket.socket, request: dict) -> dict:
    """Envia um dicionário (JSON) e retorna a resposta (dicionário)."""
    try:
        # Serializa o dicionário para JSON e envia
        sock.sendall(json.dumps(request).encode('utf-8'))
        # Aguarda a resposta
        response_data = sock.recv(2048)
        # Desserializa a resposta JSON para um dicionário
        return json.loads(response_data.decode('utf-8'))
    except (ConnectionResetError, BrokenPipeError):
        print("Erro: Conexão com o servidor perdida.")
        sys.exit(1) # Encerra o cliente
    except json.JSONDecodeError:
        print(f"Erro: Resposta inválida do servidor: {response_data.decode('utf-8')}")
        return {"status": "erro", "msg": "Resposta corrompida do servidor"}

def login(sock: socket.socket) -> bool:
    """Tenta autenticar o usuário via TCP. [cite: 39]"""
    print("--- Login do Votante ---")
    usuario = input("Usuário: ")
    senha = input("Senha: ")
    
    # Monta a requisição de login
    req = {"acao": "login", "usuario": usuario, "senha": senha}
    # Envia e recebe a resposta
    resp = send_request(sock, req)
    
    # Processa a resposta
    if resp.get('status') == 'ok' and resp.get('tipo') == 'voter':
        print("Login realizado com sucesso!")
        return True
    else:
        print(f"Falha no login: {resp.get('msg', 'Erro desconhecido')}")
        return False

# --- Função Principal (Main) do Cliente ---
def main():
    # 1. Inicia a thread que ouve o multicast UDP
    # 'daemon=True' faz a thread fechar quando o programa principal (main) fechar
    multicast_thread = threading.Thread(target=listen_for_multicast_notes, daemon=True)
    multicast_thread.start()

    # 2. Conecta ao servidor TCP [cite: 41]
    try:
        # Cria o socket TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Conecta ao servidor
            sock.connect((SERVER_HOST, SERVER_PORT))
            
            # 3. Executa o Login
            if not login(sock):
                print("Encerrando cliente.")
                return # Sai do programa se o login falhar

            # 4. Loop do Menu Principal (pós-login)
            while True:
                print("\n--- Menu do Votante ---")
                print("1. Ver lista de candidatos")
                print("2. Votar")
                print("3. Sair")
                escolha = input("> ")

                # Opção 1: Listar Candidatos [cite: 39]
                if escolha == '1':
                    req = {"acao": "get_candidatos"}
                    resp = send_request(sock, req)
                    if resp.get('status') == 'ok':
                        print("--- Lista de Candidatos ---")
                        for id_cand, info in resp.get('candidatos', {}).items():
                            print(f"  ID: {id_cand} - Nome: {info['nome']}")
                    else:
                        print(f"Erro: {resp.get('msg')}")
                
                # Opção 2: Votar [cite: 39]
                elif escolha == '2':
                    try:
                        id_voto = int(input("Digite o ID do candidato: "))
                        req = {"acao": "votar", "id_candidato": id_voto}
                        resp = send_request(sock, req)
                        print(f"Resposta do Servidor: {resp.get('msg')}")
                    except ValueError:
                        print("ID inválido. Deve ser um número.")
                
                # Opção 3: Sair
                elif escolha == '3':
                    print("Desconectando...")
                    break # Quebra o loop
                
                else:
                    print("Opção inválida.")
                    
    except ConnectionRefusedError:
        print(f"Erro: Não foi possível conectar ao servidor em {SERVER_HOST}:{SERVER_PORT}")
        print("Verifique se 'voting_server.py' está em execução.")

if __name__ == "__main__":
    main()