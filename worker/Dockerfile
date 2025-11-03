FROM python:3.12-slim
COPY .. /home/myapp/
WORKDIR /home/myapp
RUN pip install -r /home/myapp/requirements.txt
CMD ["python3", "-u", "/home/myapp/worker.py"]