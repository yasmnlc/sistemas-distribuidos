# streams.py
import struct  # Para empacotar/desempacotar dados binários
import sys     # Para usar stderr em mensagens de erro
from typing import List, Any  # Para type hints (Any = qualquer tipo de stream)
from pojo import PlanoSaude   # Importa a classe base POJO e seus métodos

# -----------------------------------------------------------------
# ITEM 2: Implementação do "PojoEscolhidoOutputStream"
# -----------------------------------------------------------------
class PlanoSaudeStreamWriter:
    """
    Equivalente Python do 'PojoEscolhidoOutputStream'[cite: 7].
    Esta classe escreve uma LISTA de objetos PlanoSaude em um 
    stream de destino (como um arquivo, socket, ou stdout).
    """

    def __init__(self, dest_stream: Any):
        """
        Construtor. Recebe o stream de destino (Item 2.a.iv)[cite: 11].
        :param dest_stream: Um objeto com método .write() (ex: arquivo, socket)
        """
        # (iv) Armazena o "OutputStream de destino"
        self.stream = dest_stream

    def write_planos(self, planos: List[PlanoSaude]):
        """
        Método principal que escreve a lista de planos no stream.
        Este método lida com os requisitos (i), (ii), e (iii) do Item 2.a.
        """
        try:
            # (ii) Obtém o número de Objetos que serão enviados [cite: 10]
            num_objetos = len(planos)
            
            # (iii) Obtém o número de bytes de CADA objeto [cite: 11]
            # Usamos o método estático que você já criou no pojo.py
            serial_size = PlanoSaude.get_serial_size()

            # 1. Escreve o Cabeçalho: (Número de objetos, Tamanho de cada objeto)
            # Usamos '<II' (dois unsigned ints, little-endian)
            header_format = '<II' 
            # Empacota os dois inteiros em bytes
            header_bytes = struct.pack(header_format, num_objetos, serial_size)
            # Escreve o cabeçalho no stream
            self.stream.write(header_bytes)

            # 2. Escreve cada objeto da lista (Item 2.a.i) [cite: 9]
            for plano in planos:
                # Serializa o objeto POJO para bytes (usando seu método)
                plano_bytes = plano.to_bytes()
                # Escreve os bytes do objeto no stream
                self.stream.write(plano_bytes)
            
            # Garante que todos os dados "buffered" sejam enviados imediatamente
            self.stream.flush()

        except Exception as e:
            # Imprime erros no "standard error" para não corromper o stream
            print(f"Erro ao escrever no stream: {e}", file=sys.stderr)

# -----------------------------------------------------------------
# ITEM 3: Implementação do "PojoEscolhidoInputStream"
# -----------------------------------------------------------------
class PlanoSaudeStreamReader:
    """
    Equivalente Python do 'PojoEscolhidoInputStream'[cite: 21].
    Esta classe lê uma LISTA de objetos PlanoSaude de um 
    stream de origem (como um arquivo, socket, ou stdin).
    """

    def __init__(self, source_stream: Any):
        """
        Construtor. Recebe o stream de origem (Item 3.a)[cite: 23].
        :param source_stream: Um objeto com método .read() (ex: arquivo, socket)
        """
        # (a) Armazena o "InputStream de origem"
        self.stream = source_stream

    def read_planos(self) -> List[PlanoSaude]:
        """
        Lê e desserializa os planos do stream.
        """
        # Lista para armazenar os planos lidos
        planos_lidos = []
        try:
            # 1. Lê o Cabeçalho: (Número de objetos, Tamanho de cada objeto)
            # Define o formato esperado (dois unsigned ints)
            header_format = '<II'
            # Calcula o tamanho exato em bytes do cabeçalho
            header_size = struct.calcsize(header_format)
            
            # Lê o número exato de bytes do cabeçalho do stream
            header_bytes = self.stream.read(header_size)

            # Se não vier nada (stream fechado/vazio), retorna lista vazia
            if not header_bytes:
                return [] 

            # Desempacota os bytes do cabeçalho para inteiros
            num_objetos, serial_size = struct.unpack(header_format, header_bytes)

            # Verificação de segurança: checa se o tamanho no stream bate
            # com o tamanho que o pojo.py espera.
            expected_size = PlanoSaude.get_serial_size()
            if serial_size != expected_size:
                raise ValueError(f"Tamanho do objeto no stream ({serial_size}) não confere com o esperado ({expected_size})")

            # 2. Lê cada objeto do stream
            for _ in range(num_objetos):
                # Lê o número exato de bytes para UM objeto
                objeto_bytes = self.stream.read(serial_size)
                
                # Se o stream acabar antes do esperado, levanta um erro
                if len(objeto_bytes) < serial_size:
                    raise IOError("Stream interrompido no meio da leitura dos dados.")
                
                # Desserializa os bytes para um objeto (usando seu método)
                plano = PlanoSaude.from_bytes(objeto_bytes)
                # Adiciona o objeto lido à lista
                planos_lidos.append(plano)
            
            # Retorna a lista completa de planos lidos
            return planos_lidos

        except Exception as e:
            # Imprime erros no "standard error"
            print(f"Erro ao ler do stream: {e}", file=sys.stderr)
            # Retorna o que conseguiu ler até o momento
            return planos_lidos