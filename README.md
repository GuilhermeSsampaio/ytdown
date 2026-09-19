# YtDown

Aplicativo local, com interface simples, para baixar em MP4 vídeos que você tem o direito de baixar. Ele consulta os formatos disponíveis e une vídeo e áudio para preservar a qualidade selecionada.

## Rodar durante o desenvolvimento

1. Instale o Python 3.10 ou superior no Windows, marcando **Add Python to PATH**.
2. No PowerShell, dentro desta pasta, execute:

```powershell
python -m pip install -r requirements.txt
python app.py
```

O navegador abre em `http://127.0.0.1:5000`.

## Criar o executável portátil

Com o Python instalado somente na máquina que fará a compilação, dê dois cliques em `build_exe.bat`. O resultado será `dist\YtDown.exe`.

Copie apenas `YtDown.exe` para outro PC Windows e execute. A primeira execução pode demorar um pouco, pois o programa extrai arquivos temporários. O navegador padrão abrirá automaticamente; fechar a janela do terminal encerra o aplicativo.

> Alguns antivírus podem pedir confirmação para executáveis recém-criados e não assinados. Isso é esperado em um `.exe` local criado com PyInstaller.

## Observação de uso

Use o aplicativo apenas para conteúdo próprio, licenciado ou autorizado. Respeite os termos da plataforma de origem e direitos autorais.
