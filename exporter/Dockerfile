FROM ubuntu

LABEL description "Dockerfile api employees"

WORKDIR /app

COPY . /app

RUN apt update
RUN apt install python3-pip -y
RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]