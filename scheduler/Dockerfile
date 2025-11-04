FROM python
COPY .. /home/myapp/
RUN pip install -r /home/myapp/requirements.txt
CMD ["python3", "-u", "/home/myapp/scheduler.py"]