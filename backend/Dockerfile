FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app
WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]