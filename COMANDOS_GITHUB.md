# Comandos para subir o projeto no GitHub

> Execute estes comandos dentro da pasta `projeto-iot-solar-final`.

## 1. Entrar na pasta do projeto

```bash
cd projeto-iot-solar-final
```

## 2. Conferir se o arquivo `.env` não será enviado

```bash
git status
```

O arquivo `.env` não deve aparecer para commit. Apenas `.env.example` deve aparecer.

## 3. Inicializar o Git

```bash
git init
git add .
git commit -m "Organiza projeto IoT solar"
```

## 4. Criar o repositório no GitHub

No GitHub, crie um repositório novo, por exemplo:

```text
projeto-iot-solar
```

Não adicione README pelo site, pois o projeto já tem um README pronto.

## 5. Conectar o repositório local ao GitHub

Troque `SEU_USUARIO` pelo seu usuário do GitHub:

```bash
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/projeto-iot-solar.git
git push -u origin main
```

## 6. Conferência final

Depois do envio, abra o repositório no navegador e confira se aparecem:

- `README.md`
- `src/monitoramento_solar.py`
- `docs/relatorio.tex`
- `docs/relatorio.pdf`
- `.env.example`
- `requirements.txt`
- `.gitignore`

O arquivo `.env` não deve aparecer no GitHub.
