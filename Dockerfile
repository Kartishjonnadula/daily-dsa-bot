FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# COPY bot.py .
# COPY neet_code ./neet_code
COPY . .

CMD ["python", "bot.py"]