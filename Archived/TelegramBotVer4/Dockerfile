FROM python:3.10.13-bookworm
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN bash install_caddy.sh
EXPOSE 8880
# CMD ["python", "TelegramBot.py"]
# CMD ["python", "Task.py"]
CMD ["bash", "launch.sh"]
