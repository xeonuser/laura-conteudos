@echo off
setlocal
cd /d "%~dp0"
title Aurora TV - Teste no computador
echo.
echo   AURORA TV - Vamos abrir sua TV no navegador!
echo.
py -3 -c "import sys; sys.exit(sys.version_info < (3,10))" >nul 2>&1
if not errorlevel 1 (
    py -3 -m smartbox.server --port 0 --open
    goto fim
)
python -c "import sys; sys.exit(sys.version_info < (3,10))" >nul 2>&1
if not errorlevel 1 (
    python -m smartbox.server --port 0 --open
    goto fim
)
echo Falta instalar o Python, um programa gratuito necessario para este teste.
echo Vou abrir a pagina oficial. Instale Python 3.10 ou mais recente.
echo No instalador, marque "Add python.exe to PATH" se essa opcao aparecer.
echo Depois de instalar, abra este arquivo de novo.
start "" https://www.python.org/downloads/windows/
:fim
echo.
echo Para encerrar a Aurora, feche esta janela.
echo Se houve erro, tire uma foto desta janela para pedir ajuda.
pause
