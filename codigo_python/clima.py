# Arquivo: clima.py
import requests


def verificar_previsao_chuva(latitude: float, longitude: float) -> bool:
    """
    Consulta a API Open-Meteo para obter a probabilidade de chuva nas próximas horas
    e retorna True se a chance for considerada alta.
    """
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={latitude}&longitude={longitude}"
           f"&hourly=precipitation_probability&forecast_days=1")

    try:
        print(
            f"\n🛰️  Consultando previsão do tempo (Open-Meteo) para Lat:{latitude}, Lon:{longitude}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        dados = response.json()

        probabilidades = dados['hourly']['precipitation_probability']
        proximas_6_horas = probabilidades[:6]

        print(
            f"  -> Probabilidades de chuva para as próximas 6h: {proximas_6_horas}%")

        # Lógica: Se qualquer hora tiver mais de 50% de chance, considera-se previsão de chuva.
        for prob in proximas_6_horas:
            if prob > 50:
                print("  -> ALERTA: Alta probabilidade de chuva detectada!")
                return True

        print("  -> Tempo firme. Baixa probabilidade de chuva.")
        return False

    except requests.exceptions.RequestException as e:
        print(f"  -> ERRO: Falha ao conectar à API de clima. {e}")
        return False
    except (KeyError, IndexError):
        print("  -> ERRO: A resposta da API não veio no formato esperado.")
        return False
