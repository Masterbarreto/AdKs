# Use Python runtime
FROM python:3.12-slim

WORKDIR /app

# Copy requirements and patch script first to leverage cache
COPY requirements.txt patch_genai.py ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Apply patch to fix Pydantic serialization issue in google-genai
RUN python patch_genai.py

# Copy the rest of the project
COPY . .

# Expose port (Cloud Run expects 8080 by default)
EXPOSE 8080

# Run ADK API server via custom wrapper
CMD ["python", "run_server.py"]
