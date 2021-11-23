FROM python:3.10

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt requirements.txt
COPY ./main.py main.py

RUN pip install -r requirements.txt

ENV SPEEDTEST_DATA_URL=localhost:7898

CMD ["streamlit", "run", "main.py", "--server.port", "8555", "--server.address", "0.0.0.0"]