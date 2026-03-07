FROM python:3.10

WORKDIR /app

COPY backend /app/backend
COPY backend/requirements.txt /app

RUN pip install --upgrade pip \
 && pip install --default-timeout=1000 -r requirements.txt

EXPOSE 5000

CMD ["python", "backend/app.py"]