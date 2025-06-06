FROM python:3-alpine

RUN adduser --system --no-create-home nonroot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
USER nonroot
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]