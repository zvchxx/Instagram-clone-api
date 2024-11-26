FROM python:3.9.13
LABEL maintainer="Instagram"

ENV PYTHONUNBUFFERED 1

# Set up virtual environment and install dependencies
COPY ./requirements.txt /app/requirements.txt

RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /app/requirements.txt && \
    adduser --disabled-password django-user && \
    chown -R django-user /app

# Copy application code
COPY ./ ./app
WORKDIR /app

# Set user and PATH
USER django-user
ENV PATH="/venv/bin:$PATH"

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]