# teste_streams.py
import sys
from pojo import PlanoEmpresa, PlanoIndividual
from streams import PlanoSaudeStreamWriter, PlanoSaudeStreamReader

# Cria alguns POJOs de exemplo (Item 2.a.i)
plano1 = PlanoEmpresa(codigo=1, nome_plano="Empresa Gigante", preco_base=500.0, is_ativo=True, cnpj="111")
plano2 = PlanoIndividual(codigo=2, nome_plano="Individuo Comum", preco_base=150.0, is_ativo=True, cpf_titular="222")
meus_planos = [plano1, plano2]

def testar_escrita_arquivo():
    """Teste (ii): Escreve em um arquivo (FileOutputStream) [cite: 17]"""
    print("Testando (2.b.ii): Escrita para arquivo 'planos.bin'...")
    # 'wb' = Write Binary (equivale ao FileOutputStream)
    with open("planos.bin", "wb") as f:
        # Cria o Writer apontando para o arquivo
        writer_file = PlanoSaudeStreamWriter(f)
        # Escreve os planos no arquivo
        writer_file.write_planos(meus_planos)
    print("...Escrita no arquivo concluída.")

def testar_leitura_arquivo():
    """Teste (c): Lê de um arquivo (FileInputStream) [cite: 26]"""
    print("\nTestando (3.c): Leitura do arquivo 'planos.bin'...")
    try:
        # 'rb' = Read Binary (equivale ao FileInputStream)
        with open("planos.bin", "rb") as f:
            # Cria o Reader apontando para o arquivo
            reader_file = PlanoSaudeStreamReader(f)
            # Lê os planos do arquivo
            planos_do_arquivo = reader_file.read_planos()
            
            print(f"Planos lidos do arquivo ({len(planos_do_arquivo)}):")
            # Imprime os planos desserializados
            for p in planos_do_arquivo:
                print(f"  - {p}")
    except FileNotFoundError:
        print("Erro: execute o teste de escrita primeiro.")

def testar_stdout_writer():
    """Teste (i): Escreve na saída padrão (System.out) [cite: 15]"""
    # sys.stdout.buffer é o stream binário (equivale ao System.out)
    writer_stdout = PlanoSaudeStreamWriter(sys.stdout.buffer)
    # Escreve os planos no stdout
    writer_stdout.write_planos(meus_planos)

def testar_stdin_reader():
    """Teste (b): Lê da entrada padrão (System.in) [cite: 25]"""
    # sys.stdin.buffer é o stream binário (equivale ao System.in)
    reader_stdin = PlanoSaudeStreamReader(sys.stdin.buffer)
    # Lê os planos do stdin
    planos_do_stdin = reader_stdin.read_planos()
    
    # Imprime os resultados no 'stderr' para não poluir o 'stdout'
    print(f"\n--- Leitura do Stdin (3.b) ---", file=sys.stderr)
    print(f"Planos lidos do stdin ({len(planos_do_stdin)}):", file=sys.stderr)
    for p in planos_do_stdin:
        print(f"  - {p}", file=sys.stderr)
    print(f"--- Fim da Leitura do Stdin ---", file=sys.stderr)


# Define o que o script faz quando executado
if __name__ == "__main__":
    # Testa escrita/leitura de arquivo
    testar_escrita_arquivo()
    testar_leitura_arquivo()

    print("\n---")
    print("Testando (2.b.i) e (3.b): Escrita/Leitura de Stdout/Stdin")
    print("Para testar, execute no terminal:")
    print("python teste_streams.py --modo=writer | python teste_streams.py --modo=reader")
    print("---\n")

    # Verifica argumentos da linha de comando para o teste de pipe
    if len(sys.argv) > 1:
        if sys.argv[1] == "--modo=writer":
            # Modo writer: escreve para stdout
            testar_stdout_writer()
        elif sys.argv[1] == "--modo=reader":
            # Modo reader: lê de stdin
            testar_stdin_reader()