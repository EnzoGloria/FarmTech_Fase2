# Arquivo: cerebro_irrigacao.py
import time
import json
import csv
from datetime import datetime
from pathlib import Path

# Importa a função específica do nosso arquivo clima.py, que está na mesma pasta.
from clima import verificar_previsao_chuva

# --- PARÂMETROS GLOBAIS E CONFIGURAÇÕES ---
# Utilizando os parâmetros calibrados durante os testes.
PARAMETROS_CULTURA = {
    "Soja": {
        "umidade_min": 35.0,
        "ph_min": 5.8,
        "ph_max": 7.0,
        "nutriente_essencial": "n"
    },
    "Açaí": {
        "umidade_min": 45.0,
        "ph_min": 4.8,
        "ph_max": 6.2,
        "nutriente_essencial": "k"
    }
}
# Cria um caminho absoluto para o arquivo CSV, garantindo que ele seja sempre salvo na mesma pasta do script.
CAMINHO_DO_SCRIPT = Path(__file__).parent
NOME_ARQUIVO_LOG = CAMINHO_DO_SCRIPT / "historico_irrigacao.csv"

# --- FUNÇÕES AUXILIARES E PRINCIPAIS ---


def escolher_cultura() -> str:
    print("="*40 + "\n🌱 BEM-VINDO AO CÉREBRO DA FARMTECH 🌱\n" + "="*40)
    print("Culturas disponíveis:", list(PARAMETROS_CULTURA.keys()))
    while True:
        escolha = input("Qual cultura deseja monitorar? ").strip().capitalize()
        if escolha in PARAMETROS_CULTURA:
            print(f"✅ Cultura '{escolha}' selecionada.\n" + "="*40)
            return escolha
        else:
            print(
                f"❌ '{escolha}' não é uma opção válida. Por favor, escolha uma da lista.")


def decidir_irrigacao(dados_sensores: dict, cultura_atual: str) -> str:
    try:
        regras = PARAMETROS_CULTURA[cultura_atual]
        umidade = dados_sensores['umidade']
        ph = dados_sensores['ph']
        nutriente_chave = regras['nutriente_essencial']
        nutriente_presente = dados_sensores[nutriente_chave] == 1
        umidade_baixa = umidade < regras['umidade_min']
        ph_na_faixa = regras['ph_min'] <= ph <= regras['ph_max']

        print(f"  -> Diagnóstico ({cultura_atual}):")
        print(
            f"     - Umidade: {umidade}% (Ideal: > {regras['umidade_min']}%) -> Baixa? {umidade_baixa}")
        print(
            f"     - pH: {ph} (Ideal: {regras['ph_min']}-{regras['ph_max']}) -> OK? {ph_na_faixa}")
        print(
            f"     - Nutriente Essencial ({nutriente_chave.upper()}): Presente? {nutriente_presente}")

        if umidade_baixa and ph_na_faixa and nutriente_presente:
            return "LIGAR"
        else:
            return "DESLIGAR"
    except KeyError as e:
        print(f"  -> ERRO: Chave {e} não encontrada nos dados dos sensores.")
        return "DESLIGAR"


def registrar_dados(nome_arquivo: str, dados_sensores: dict, decisao: str):
    """
    Salva uma nova linha em um arquivo CSV, escrevendo o cabeçalho apenas se o arquivo for novo.
    """
    # <<< ALTERAÇÃO AQUI >>>
    # Usamos o objeto Path que já tínhamos para verificar de forma robusta se o arquivo existe e não está vazio.
    arquivo_path = Path(nome_arquivo)

    # A condição para escrever o cabeçalho é: o arquivo não existe OU ele existe mas está vazio (tamanho 0).
    escrever_cabecalho = not arquivo_path.exists() or arquivo_path.stat().st_size == 0

    cabecalho = ['timestamp', 'n', 'p', 'k', 'ph', 'umidade', 'acao_bomba']
    nova_linha = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'n': dados_sensores.get('n', 0), 'p': dados_sensores.get('p', 0), 'k': dados_sensores.get('k', 0),
        'ph': dados_sensores.get('ph', 0.0), 'umidade': dados_sensores.get('umidade', 0.0), 'acao_bomba': decisao
    }

    try:
        # Abrimos o arquivo em modo 'a' (append)
        with open(arquivo_path, 'a', newline='', encoding='utf-8') as f:
            escritor = csv.DictWriter(f, fieldnames=cabecalho)

            # Escrevemos o cabeçalho apenas se a nossa condição for verdadeira
            if escrever_cabecalho:
                escritor.writeheader()

            # Escrevemos a nova linha de dados
            escritor.writerow(nova_linha)

    except IOError as e:
        print(f"  -> ERRO ao escrever no arquivo CSV: {e}")

# --- BLOCO DE EXECUÇÃO PRINCIPAL ---


def main():
    # Definindo as coordenadas da nossa fazenda virtual em Cuiabá, MT.
    LATITUDE_FAZENDA = -15.6010
    LONGITUDE_FAZENDA = -56.0974

    cultura_monitorada = escolher_cultura()
    estado_bomba_atual = "DESLIGAR"

    print(f"Iniciando monitoramento para '{cultura_monitorada}'.")
    print(f"Registrando dados em: '{NOME_ARQUIVO_LOG}'")
    print("Para sair, pressione Ctrl+C.")
    print("\nAguardando o primeiro JSON do ESP32...")

    try:
        while True:
            json_string = input(
                "\n📋 Cole o JSON do Monitor Serial do Wokwi aqui e pressione Enter: ")
            try:
                dados_sensores = json.loads(json_string)
                decisao_sensores = decidir_irrigacao(
                    dados_sensores, cultura_monitorada)

                ha_previsao_chuva = verificar_previsao_chuva(
                    LATITUDE_FAZENDA, LONGITUDE_FAZENDA)

                decisao_final = ""
                if ha_previsao_chuva and decisao_sensores == "LIGAR":
                    decisao_final = "DESLIGAR"
                    print(
                        "  => DECISÃO FINAL: DESLIGAR (Irrigação suspensa devido à previsão de chuva)")
                else:
                    decisao_final = decisao_sensores
                    print(f"  => DECISÃO FINAL: {decisao_final}")

                if decisao_final != estado_bomba_atual:
                    print(
                        f"  ⚡️ AÇÃO NECESSÁRIA! O estado da bomba deve ser '{decisao_final}'.")
                    print(
                        f"  👉 Por favor, digite '{decisao_final}' no Monitor Serial do Wokwi e pressione Enter.")
                    estado_bomba_atual = decisao_final
                else:
                    print("  ... Nenhuma mudança de estado necessária.")

                registrar_dados(NOME_ARQUIVO_LOG,
                                dados_sensores, estado_bomba_atual)
                print(f"  -> Dados registrados com sucesso.")
            except json.JSONDecodeError:
                print(
                    "  -> ERRO: O texto inserido não é um JSON válido. Tente copiar novamente.")
            except KeyError:
                print(
                    "  -> ERRO: O JSON recebido não contém todas as chaves esperadas (n, p, k, ph, umidade).")
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
    finally:
        print("Simulação finalizada. Verifique o arquivo CSV para o histórico.")


if __name__ == "__main__":
    main()
