
FROM python:3.9.5

WORKDIR /yahoo

COPY requirements.txt /yahoo
ADD ./currencies /yahoo

RUN pip install -r requirements.txt

CMD python main.py
