FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 80

# Run the application
CMD ["python", "main.py"]
