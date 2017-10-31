FROM python:3

WORKDIR /var/app

COPY . .

ENV APP_ENV=docker

RUN pip install -r requirements.txt

CMD [ "python", "dataprocessor.py" ]
