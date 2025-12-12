FROM python:3.11.14-slim-bookworm
COPY ./requirements.txt /requirements.txt

# Normalize line endings in case the file was created on Windows (CRLF).
# CRLF in the shebang can cause "no such file or directory" at runtime.
# Use sed to remove CR carriage returns; sed is available in Debian base.
RUN sed -i 's/\r$//' /requirements.txt

WORKDIR /var/www/app
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
CMD ["fastapi", "run", "main.py", "--port", "80"]