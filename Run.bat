@echo off
call C:\Users\balaj\anaconda3\Scripts\activate.bat
conda activate streamlit
cd /d %~dp0
call streamlit run streamlit_app.py
