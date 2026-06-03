# Projeto IoT Solar - Monitoramento do Potencial de Geração Fotovoltaica

Projeto acadêmico de Engenharia Elétrica/IoT para monitoramento do potencial de geração solar em Florianópolis, SC. O sistema utiliza dados meteorológicos reais da API Open-Meteo, estima a potência fotovoltaica disponível e envia as medições para a plataforma TagoIO via HTTP.

## Objetivo

Desenvolver um sistema IoT simples, funcional e demonstrável para acompanhar o potencial de geração solar com base em dados reais de irradiância, temperatura, umidade e vento. O projeto simula o comportamento de um conjunto de painéis fotovoltaicos e apresenta os dados em um dashboard no TagoIO.

## Arquitetura do sistema

```text
Open-Meteo API
     |
     | Dados meteorológicos reais
     v
Script Python
     |
     | Processamento e cálculo fotovoltaico
     v
TagoIO HTTP API
     |
     | Armazenamento e visualização
     v
Dashboard TagoIO
```

Fluxo principal:

1. O script consulta a API Open-Meteo para Florianópolis.
2. A leitura da hora atual é extraída dos dados horários retornados.
3. O programa calcula a potência fotovoltaica estimada.
4. O status da geração é classificado como `Alta`, `Media` ou `Baixa`.
5. As variáveis são enviadas ao TagoIO via HTTP usando o token do device.
6. O dashboard do TagoIO exibe os dados em tempo real.

## Tecnologias usadas

- Python 3.10+
- Requests
- python-dotenv
- API Open-Meteo
- Plataforma TagoIO
- HTTP/JSON
- Dashboard em nuvem

## Fórmula usada para estimar a potência solar

A potência fotovoltaica estimada é calculada por:

```text
P = G * A * eta * [1 - gamma * (T - 25)]
```

Em que:

- `P`: potência estimada em watts (W)
- `G`: irradiância solar em W/m²
- `A`: área total dos painéis em m²
- `eta`: eficiência dos painéis
- `gamma`: coeficiente térmico simplificado, adotado como `0,004 / °C`
- `T`: temperatura ambiente em °C

No projeto, os valores padrão são:

- Área simulada: `10 m²`
- Eficiência: `20%`
- Local: Florianópolis, SC
- Coordenadas: latitude `-27.5954`, longitude `-48.5480`

## Classificação do status de geração

| Status | Critério |
|---|---|
| Alta | irradiância >= 200 W/m² |
| Media | 50 W/m² <= irradiância < 200 W/m² |
| Baixa | irradiância < 50 W/m² |

## Variáveis enviadas ao TagoIO

| Variável | Descrição | Unidade |
|---|---|---|
| `irradiancia` | Irradiância solar de onda curta | W/m² |
| `temperatura` | Temperatura do ar a 2 m | °C |
| `umidade` | Umidade relativa do ar | % |
| `vento` | Velocidade do vento a 10 m | km/h |
| `potencia_estimada` | Potência fotovoltaica estimada | W |
| `status_geracao` | Classificação da geração | texto |

## Estrutura do repositório

```text
projeto-iot-solar/
|
├── src/
│   └── monitoramento_solar.py
|
├── docs/
│   ├── relatorio.tex
│   └── relatorio.pdf
|
├── assets/
│   └── imagens_do_dashboard/
│       └── .gitkeep
|
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── COMANDOS_GITHUB.md
└── OBSERVACOES_ENTREGA.md
```

## Como configurar o ambiente

### 1. Criar e ativar um ambiente virtual

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

No macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar o arquivo `.env`

Copie o arquivo de exemplo:

No Windows:

```bash
copy .env.example .env
```

No macOS/Linux:

```bash
cp .env.example .env
```

Depois, abra o arquivo `.env` e preencha o token do device do TagoIO:

```text
TAGOIO_TOKEN=cole_aqui_o_token_do_device
```

O arquivo `.env` não deve ser enviado ao GitHub.

## Como rodar o projeto

Com o ambiente virtual ativado e o arquivo `.env` configurado:

```bash
python src/monitoramento_solar.py
```

O programa executa ciclos contínuos de coleta, cálculo e envio ao TagoIO. O intervalo padrão é de 120 segundos, definido pela variável `INTERVALO_SEGUNDOS`.

Para uso após a apresentação, é possível aumentar esse valor no `.env`, por exemplo:

```text
INTERVALO_SEGUNDOS=1200
```

## Como visualizar no TagoIO

1. Acesse sua conta no TagoIO.
2. Crie ou selecione o device usado no projeto.
3. Gere um token para esse device.
4. Cole o token no arquivo `.env` local.
5. Rode o script Python.
6. No TagoIO, abra o device e verifique o recebimento das variáveis.
7. Abra o dashboard configurado para visualizar irradiância, temperatura, umidade, vento, potência estimada e status de geração.

## Segurança sobre tokens

O token do TagoIO é uma credencial de acesso ao device. Por isso:

- Nunca coloque o token diretamente no código Python.
- Nunca publique o arquivo `.env` no GitHub.
- Use apenas `.env.example` como modelo sem token real.
- Caso um token real tenha sido compartilhado por engano, gere um novo token no TagoIO e substitua o antigo.

## Integrantes da equipe

- Luis Felipe Candido Sola
- Carlos Henrique Braatz Lautert

## Disciplina e professor

- Disciplina: Tópico Avançado em Telecomunicações IV / Redes de Sensores sem Fio para IoT
- Curso: Engenharia Elétrica - UFSC
- Professor: Prof. Richard Demo Souza

## Data da entrega

- Prazo informado: 05/06/2026

## Referências

- Open-Meteo: API de dados meteorológicos.
- TagoIO: plataforma IoT para armazenamento, visualização e automação de dados.
