FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /tests

RUN pip install playwright pytest pytest-playwright && playwright install

COPY . .

ENV BASE_URL=http://localhost:8000
ENV USE_TEST_POKEMON=1

CMD ["pytest", "-v"]
