@echo off
echo ========================================
echo   NLP Demo - Setup and Run
echo ========================================
echo.

echo [Step 1/4] Installing Python packages...
pip install -r requirements.txt

echo.
echo [Step 2/4] Downloading NLTK data...
python -c "import nltk; nltk.download('wordnet'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"

echo.
echo [Step 3/4] Downloading spaCy model...
python -m spacy download en_core_web_sm

echo.
echo [Step 4/4] Starting Streamlit app...
echo.
echo App will open in your browser at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run nlp_app.py
