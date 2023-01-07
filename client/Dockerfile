FROM python
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./code /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "20456", "--ssl-keyfile", "app/client_key.pem", "--ssl-certfile", "app/client_cert.pem", "--ssl-cert-reqs", "2", "--ssl-ca-certs", "app/coordinator_cert.pem"]
