FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY flaskr /app/flaskr/
COPY pyproject.toml /app/
RUN pip install -e .
RUN mkdir -p /app/instance
ENV FLASK_APP=flaskr:create_app
RUN python -m flask init-db
CMD ["flask", "run", "--host=0.0.0.0"]