"""
Sistema IoT - Monitoramento do Potencial de Geração Solar

Projeto acadêmico de Engenharia Elétrica/IoT.
Coleta dados meteorológicos reais da API Open-Meteo, estima a potência
fotovoltaica disponível para uma área de painéis e envia as medições ao TagoIO.

Antes de executar:
1. Copie o arquivo .env.example para .env
2. Preencha TAGOIO_TOKEN com o token do device criado no TagoIO
3. Instale as dependências com: pip install -r requirements.txt
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv


# Carrega variáveis do arquivo .env, quando ele existir.
load_dotenv()


@dataclass(frozen=True)
class Configuracao:
    """Configurações gerais do projeto."""

    latitude: float
    longitude: float
    area_painel_m2: float
    eficiencia_painel: float
    intervalo_segundos: int
    timezone: str
    tagoio_token: str
    tagoio_http_url: str


def obter_configuracao() -> Configuracao:
    """Lê as configurações a partir das variáveis de ambiente."""

    tagoio_token = os.getenv("TAGOIO_TOKEN")
    if not tagoio_token:
        raise RuntimeError(
            "TAGOIO_TOKEN não foi configurado. Copie .env.example para .env "
            "e informe o token do device criado no TagoIO."
        )

    return Configuracao(
        latitude=float(os.getenv("LATITUDE", "-27.5954")),
        longitude=float(os.getenv("LONGITUDE", "-48.5480")),
        area_painel_m2=float(os.getenv("AREA_PAINEL_M2", "10")),
        eficiencia_painel=float(os.getenv("EFICIENCIA_PAINEL", "0.20")),
        intervalo_segundos=int(os.getenv("INTERVALO_SEGUNDOS", "120")),
        timezone=os.getenv("TIMEZONE", "America/Sao_Paulo"),
        tagoio_token=tagoio_token,
        tagoio_http_url=os.getenv("TAGOIO_HTTP_URL", "https://api.eu-w1.tago.io/data"),
    )


def configurar_logs() -> None:
    """Configura a saída de mensagens no terminal."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def cabecalho(config: Configuracao) -> None:
    """Exibe um cabeçalho simples no terminal."""

    print("\n" + "=" * 60)
    print("  Sistema IoT - Monitoramento Solar")
    print("  UFSC - Engenharia Elétrica")
    print("  Florianópolis, SC - Brasil")
    print("=" * 60)
    print(f"  Localização: {config.latitude}, {config.longitude}")
    print(f"  Intervalo de coleta: {config.intervalo_segundos} segundos")
    print("  Pressione Ctrl+C para encerrar")
    print("=" * 60 + "\n")


def classificar_status(irradiancia: float) -> str:
    """Classifica o potencial de geração conforme a irradiância medida."""

    if irradiancia < 50:
        return "Baixa"
    if irradiancia < 200:
        return "Media"
    return "Alta"


def buscar_dados_meteorologicos(config: Configuracao) -> dict[str, Any]:
    """Busca dados horários de irradiância e clima na API Open-Meteo."""

    url = "https://api.open-meteo.com/v1/forecast"
    parametros = {
        "latitude": config.latitude,
        "longitude": config.longitude,
        "hourly": "shortwave_radiation,temperature_2m,relative_humidity_2m,wind_speed_10m",
        "forecast_days": 1,
        "timezone": config.timezone,
    }

    try:
        resposta = requests.get(url, params=parametros, timeout=15)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        raise RuntimeError(f"Falha ao consultar a API Open-Meteo: {erro}") from erro
    except ValueError as erro:
        raise RuntimeError("A resposta da API Open-Meteo não está em JSON válido.") from erro


def extrair_leitura_atual(dados: dict[str, Any], timezone: str) -> dict[str, Any]:
    """Extrai a leitura da hora atual a partir dos dados horários retornados pela API."""

    try:
        dados_horarios = dados["hourly"]
        horas = dados_horarios["time"]
        hora_atual = datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%dT%H:00")

        if hora_atual in horas:
            indice = horas.index(hora_atual)
        else:
            # Fallback: usa a leitura mais recente disponível, preservando a lógica original.
            indice = len(horas) - 1

        return {
            "timestamp": horas[indice],
            "irradiancia": float(dados_horarios["shortwave_radiation"][indice]),
            "temperatura": float(dados_horarios["temperature_2m"][indice]),
            "umidade": float(dados_horarios["relative_humidity_2m"][indice]),
            "vento": float(dados_horarios["wind_speed_10m"][indice]),
        }
    except (KeyError, IndexError, TypeError, ValueError) as erro:
        raise RuntimeError("Não foi possível extrair a leitura atual dos dados da Open-Meteo.") from erro


def calcular_potencia_fotovoltaica(
    irradiancia: float,
    temperatura: float,
    area_painel_m2: float,
    eficiencia_painel: float,
) -> float:
    """
    Estima a potência fotovoltaica instantânea.

    Fórmula:
        P = G * A * eta * [1 - gamma * (T - 25)]

    Em que:
        G     = irradiância solar em W/m²
        A     = área dos painéis em m²
        eta   = eficiência do painel
        gamma = coeficiente térmico simplificado, adotado como 0,004 / °C
        T     = temperatura ambiente em °C
    """

    coeficiente_termico = 0.004
    correcao_temperatura = 1 - coeficiente_termico * (temperatura - 25)
    return irradiancia * area_painel_m2 * eficiencia_painel * correcao_temperatura


def montar_payload_tagoio(leitura: dict[str, Any], potencia: float, status: str) -> list[dict[str, Any]]:
    """Monta a lista de variáveis enviada ao TagoIO."""

    return [
        {"variable": "irradiancia", "value": leitura["irradiancia"], "unit": "W/m2"},
        {"variable": "temperatura", "value": leitura["temperatura"], "unit": "C"},
        {"variable": "umidade", "value": leitura["umidade"], "unit": "%"},
        {"variable": "vento", "value": leitura["vento"], "unit": "km/h"},
        {"variable": "potencia_estimada", "value": round(potencia, 2), "unit": "W"},
        {"variable": "status_geracao", "value": status, "unit": ""},
    ]


def enviar_para_tagoio(payload: list[dict[str, Any]], config: Configuracao) -> dict[str, Any]:
    """Envia os dados ao TagoIO via HTTP."""

    headers = {
        "Device-Token": config.tagoio_token,
        "Content-Type": "application/json",
    }

    try:
        resposta = requests.post(config.tagoio_http_url, json=payload, headers=headers, timeout=15)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        raise RuntimeError(f"Falha ao enviar dados ao TagoIO: {erro}") from erro
    except ValueError as erro:
        raise RuntimeError("O TagoIO respondeu, mas a resposta não está em JSON válido.") from erro


def executar_ciclo(numero_ciclo: int, config: Configuracao) -> None:
    """Executa um ciclo completo: coleta, cálculo, classificação e envio."""

    logging.info("Iniciando ciclo #%s", numero_ciclo)

    dados_brutos = buscar_dados_meteorologicos(config)
    leitura = extrair_leitura_atual(dados_brutos, config.timezone)

    potencia = calcular_potencia_fotovoltaica(
        irradiancia=leitura["irradiancia"],
        temperatura=leitura["temperatura"],
        area_painel_m2=config.area_painel_m2,
        eficiencia_painel=config.eficiencia_painel,
    )
    status = classificar_status(leitura["irradiancia"])
    payload = montar_payload_tagoio(leitura, potencia, status)

    print("\n" + "-" * 60)
    print(f"Ciclo #{numero_ciclo}")
    print(f"Horário da leitura : {leitura['timestamp']}")
    print(f"Irradiância solar  : {leitura['irradiancia']:.2f} W/m²")
    print(f"Temperatura        : {leitura['temperatura']:.2f} °C")
    print(f"Umidade            : {leitura['umidade']:.2f} %")
    print(f"Vento              : {leitura['vento']:.2f} km/h")
    print(f"Potência estimada  : {potencia:.2f} W")
    print(f"Status de geração  : {status}")

    resposta_tagoio = enviar_para_tagoio(payload, config)
    logging.info("Dados enviados ao TagoIO: %s", resposta_tagoio.get("result", resposta_tagoio))


def main() -> None:
    """Função principal do programa."""

    configurar_logs()

    try:
        config = obter_configuracao()
    except RuntimeError as erro:
        logging.error(erro)
        return

    cabecalho(config)

    ciclo = 1
    try:
        while True:
            try:
                executar_ciclo(ciclo, config)
            except RuntimeError as erro:
                logging.error(erro)

            ciclo += 1
            logging.info("Próxima coleta em %s segundos", config.intervalo_segundos)
            time.sleep(config.intervalo_segundos)
    except KeyboardInterrupt:
        print("\nSistema encerrado pelo usuário.\n")


if __name__ == "__main__":
    main()
