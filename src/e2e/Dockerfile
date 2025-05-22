FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy
WORKDIR /tests
COPY . /tests
RUN pip install pytest pytest-playwright
CMD ["pytest", "test_e2e.py"]