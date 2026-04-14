FROM python:3.13-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency spec first for layer caching
COPY pyproject.toml .

# Install dependencies
RUN uv sync --no-dev

# Copy source code
COPY src/ src/
COPY weather_trend.py .

# Create output directory
RUN mkdir -p output

CMD ["uv", "run", "python", "-m", "src.cli"]