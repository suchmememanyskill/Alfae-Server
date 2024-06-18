FROM python:3.12-slim
WORKDIR /app
ADD requirements.txt serve.py templates/template.html .
RUN mkdir templates && mv template.html templates && pip install -r requirements.txt
CMD ["python3", "serve.py"]