@echo off
REM test.bat - Script de teste para landing-page-generator (Windows)
REM Uso: test.bat

setlocal enabledelayedexpansion
set FALHAS=0

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

echo [1/4] Testando landing-page (templates/default)...
echo -----------------------------------------------
REM --test-all separa a saida por template (output\test-suite\^<template^>\^<slug^>).
REM O exit code so' e' 0 quando real_errors == 0 (EXPECTED_FAILS ja' descontado)
REM -- por isso o errorlevel conta como falha real, nao so' aviso.
python "%SCRIPTS_DIR%\generate.py" --test-all --output "%OUTPUT_DIR%"
if errorlevel 1 (
    echo.
    echo [ERRO] generate.py --test-all reportou erros reais ^(alem dos esperados^).
    set /a FALHAS+=1
)
echo.

echo [2/4] Testando proposta-comercial...
echo -----------------------------------------------
python "%SCRIPTS_DIR%\generate.py" --template proposta "%EVALS_DIR%\proposta_teste.json" --output "%OUTPUT_DIR%\proposta"
if errorlevel 1 (
    echo [ERRO] Falha na geracao da proposta.
    set /a FALHAS+=1
) else (
    echo [OK] Proposta gerada com sucesso.
)
echo.

echo [3/4] Executando QA nos arquivos gerados...
echo -----------------------------------------------
REM check.py valida convencoes do template landing-page (CTA, LGPD) --
REM roda so sobre output\test-suite\landing-page, nao sobre output\test-suite\proposta.
for /d %%D in ("%OUTPUT_DIR%\landing-page\*") do (
    if exist "%%D\index.html" (
        echo Verificando: %%~nD
        python "%SCRIPTS_DIR%\check.py" "%%D\index.html"
        if errorlevel 1 set /a FALHAS+=1
        echo.
    )
)

echo [4/4] Regressao: schema comanda a validacao ^(Fase 5, gate 2^)...
echo -----------------------------------------------
python "%SCRIPTS_DIR%\test_schema_reflete.py"
if errorlevel 1 (
    echo [ERRO] Mudanca no schema nao refletiu no comportamento do generate.py.
    set /a FALHAS+=1
)
echo.

echo ========================================
if !FALHAS! EQU 0 (
    echo Testes finalizados! Todos os 4 estagios passaram.
    echo ========================================
    echo.
    pause
    exit /b 0
) else (
    echo Testes finalizados com !FALHAS! estagio^(s^) falhando.
    echo ========================================
    echo.
    pause
    exit /b 1
)
