FROM python:3.11.14-slim-bookworm
COPY ./requirements.txt /requirements.txt
WORKDIR /var/www/app
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
CMD ["fastapi", "run", "main.py", "--port", "80"]