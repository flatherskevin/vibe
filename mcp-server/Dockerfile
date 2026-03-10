FROM python:3.12-slim

WORKDIR /app

# Copy project metadata and source, then install
COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data/sessions /app/data/archive

CMD ["python", "-m", "src"]
