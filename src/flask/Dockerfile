FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY flaskr /app/flaskr/
COPY pyproject.toml /app/
# Install with -e is required for the tests
RUN pip install -r requirements.txt && pip install -e .
RUN mkdir -p /app/instance
ENV FLASK_APP=flaskr:create_app
CMD flask --app flaskr init-db && flask run --host=0.0.0.0