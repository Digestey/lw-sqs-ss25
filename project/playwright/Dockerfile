FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /tests
COPY . .

ENV BASE_URL=http://localhost:8000

RUN pip install playwright pytest pytest-playwright && playwright install

CMD ["pytest", "-v"]
