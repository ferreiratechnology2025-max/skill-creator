@echo off
REM test.bat - Script de teste para landing-page-generator (Windows)
REM Uso: test.bat

echo ========================================
echo Landing Page Generator - Suite de Testes
echo ========================================
echo.

set SCRIPTS_DIR=scripts
set OUTPUT_DIR=output\test-suite
set EVALS_DIR=evals\inputs

REM Limpar saida anterior
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%"

echo [1/3] Testando landing-page (templates/default)...
echo -----------------------------------------------
python "%SCRIPTS_DIR%\generate.py" --test-all --output "%OUTPUT_DIR%"
if errorlevel 1 (
    echo.
    echo [AVISO] Alguns testes de landing-page falharam (isso e' esperado para casos de bloqueio).
)
echo.

echo [2/3] Testando proposta-comercial...
echo -----------------------------------------------
python "%SCRIPTS_DIR%\generate.py" --template proposta "%EVALS_DIR%\proposta_teste.json" --output "%OUTPUT_DIR%"
if errorlevel 1 (
    echo [ERRO] Falha na geracao da proposta.
) else (
    echo [OK] Proposta gerada com sucesso.
)
echo.

echo [3/4] Executando QA nos arquivos gerados...
echo -----------------------------------------------
for /d %%D in ("%OUTPUT_DIR%\*") do (
    if exist "%%D\index.html" (
        echo Verificando: %%~nD
        python "%SCRIPTS_DIR%\check.py" "%%D\index.html"
        echo.
    )
)

echo [4/4] Regressao: schema comanda a validacao (Fase 5, gate 2)...
echo -----------------------------------------------
python "%SCRIPTS_DIR%\test_schema_reflete.py"
if errorlevel 1 (
    echo [ERRO] Mudanca no schema nao refletiu no comportamento do generate.py.
)
echo.

echo ========================================
echo Testes finalizados!
echo ========================================
echo.
pause
