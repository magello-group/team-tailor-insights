FROM python:3

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml pyproject.toml
RUN poetry install --no-root

COPY run.sh run.sh
COPY program.py program.py
COPY templates/* templates/

EXPOSE 5000

ENTRYPOINT [ "./run.sh" ]

