FROM mcr.microsoft.com/playwright/python:v1.44.0

WORKDIR /tests
COPY . .

ENV BASE_URL=http://host.docker.internal:8000

RUN pip install playwright pytest pytest-playwright && playwright install

CMD ["pytest", "-v"]
