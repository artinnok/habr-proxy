FROM python:3.6.3

EXPOSE 8034

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /src
WORKDIR /src

CMD ["python", "proxy.py"]
