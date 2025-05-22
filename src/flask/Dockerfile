FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY flaskr /app/flaskr/
RUN mkdir -p /app/instance
ENV FLASK_APP=flaskr
RUN flask init-db
CMD ["flask", "run", "--host=0.0.0.0"]