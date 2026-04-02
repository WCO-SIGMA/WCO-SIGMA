@echo off
title MOTOR WCO-SIGMA
echo ---------------------------------------------------
echo 🛡️ INICIANDO WCO-SIGMA - SISTEMA HSEQ
echo ---------------------------------------------------
echo.
:: Intentamos usar 'py' que es el lanzador oficial de Windows
py -m pip install streamlit pandas plotly --quiet
py -m streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ INTENTANDO METODO ALTERNATIVO...
    python -m pip install streamlit pandas plotly --quiet
    python -m streamlit run app.py
)

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR CRITICO: Python no esta respondiendo.
    echo Por favor, escriba 'N' si le sale el mensaje de ayuda.
    pause
)