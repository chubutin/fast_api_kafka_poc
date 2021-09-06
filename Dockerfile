FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project

COPY ./app /app