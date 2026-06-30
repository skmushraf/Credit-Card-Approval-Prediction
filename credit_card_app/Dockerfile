FROM python:3.12-slim

# Create user to avoid running as root (Hugging Face requirement)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy and install dependencies
COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user . /app

# Expose Hugging Face Space port
EXPOSE 7860

# Run the Flask app on port 7860
CMD ["python", "-m", "flask", "--app", "app.main:app", "run", "--host", "0.0.0.0", "--port", "7860"]
