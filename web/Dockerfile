FROM python:3.11-slim
WORKDIR /home/myapp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./static /home/myapp/static/
COPY ./templates /home/myapp/templates/
COPY app.py /home/myapp/
EXPOSE 8080
CMD ["python3", "app.py"]
