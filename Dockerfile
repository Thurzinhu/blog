FROM python:3.12.3-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN python -m pip install psycopg[binary]
COPY . .
EXPOSE 8000