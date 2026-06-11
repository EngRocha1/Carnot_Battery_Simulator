# Usar uma imagem oficial e leve do Python
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de dependência e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código do projeto
COPY . .

# Expor a porta que o Streamlit usa (8501)
EXPOSE 8501

# Comando para rodar o simulador quando o container iniciar
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]