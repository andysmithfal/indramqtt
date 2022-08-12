FROM python:3.10
COPY indramqtt.py .
RUN pip install requests paho-mqtt
CMD ["python3", "./indramqtt.py"]