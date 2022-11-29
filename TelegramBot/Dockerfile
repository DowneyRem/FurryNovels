FROM python:3.10-bullseye
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
 CMD ["python", "TelegramBot.py"]
#CMD ["python", "Task.py"]
