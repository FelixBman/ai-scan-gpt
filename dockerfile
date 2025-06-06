FROM python:3-alpine

RUN adduser --system --no-create-home nonroot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY static static
COPY templates templates
COPY app.py app.py
COPY config.json config.json
USER nonroot
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]