FROM python:alpine
RUN mkdir /app
WORKDIR /app
COPY ./app /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]