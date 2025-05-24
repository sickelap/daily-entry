FROM python:3.13-alpine

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

CMD [ "uvicorn", "config:application", "--host", "0.0.0.0" ]
