FROM python:3.10
COPY indraboi.py .
RUN pip install requests paho-mqtt
CMD ["python3", "./indraboi.py"]