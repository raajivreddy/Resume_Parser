FROM python:3.12-slim

# Prevent Python from writing .pyc files to disk and buffering stdout/stderr
# Set HF_HOME so HuggingFace caches models in a directory we control
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.cache/huggingface

# Install LibreOffice Writer for .doc headless parsing
# --no-install-recommends drastically reduces the image size by skipping GUI dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security best practices
RUN useradd -m -r appuser

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies without caching the wheel archives to save space
RUN pip install --no-cache-dir -r requirements.txt

# Create the HuggingFace cache directory and assign ownership to the non-root user
RUN mkdir -p /app/.cache/huggingface && chown -R appuser:appuser /app

# Switch to the non-root user BEFORE downloading the model
# so the downloaded weights are owned by appuser
USER appuser

# Pre-download the BERT model into the Docker image during the build phase.
# This ensures the container boots instantly in production without needing internet access.
RUN python -c "from transformers import pipeline; pipeline('token-classification', model='yashpwr/resume-ner-bert-v2')"

# Copy the rest of the application code
COPY --chown=appuser:appuser app/ app/

# Expose the API port
EXPOSE 8000

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
