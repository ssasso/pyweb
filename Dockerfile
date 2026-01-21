FROM python:3.10-alpine

COPY server.py /

WORKDIR /

ENV PYTHONUNBUFFERED=1

CMD ["python3", "/server.py"]
