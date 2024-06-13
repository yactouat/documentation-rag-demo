# documentation RAG demo

## how to run

- install dependencies with `pip install -r requirements.txt`
- run the dockerized stack with `docker-compose up`
- run the Streamlit app with `python3 -m streamlit run app.py`
- you can then visit the app @ `http://localhost:8501`

## how to pull models from `ollama`

- `ollama run deepseek-coder:1.3b` (or any other models listed in https://ollama.com/library)
- update a model with `ollama pull deepseek-coder:1.3b`