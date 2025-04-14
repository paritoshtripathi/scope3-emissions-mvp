
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install flask requests psycopg2-binary
EXPOSE 5000
CMD ["python", "app.py"]
