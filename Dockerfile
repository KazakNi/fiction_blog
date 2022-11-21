FROM python:3.8-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /yatube
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "./yatube/manage.py", "runserver", "0.0.0.0:8000"]
