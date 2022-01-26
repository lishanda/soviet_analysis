FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app /app
COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt


CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]