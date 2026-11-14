FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -r -u 10001 agmail
COPY app.py .
COPY static ./static
EXPOSE 8787
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8787","--proxy-headers=false"]
