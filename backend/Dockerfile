# lightweight Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements and install 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of code
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the app :D
CMD ["python", "app.py"]