FROM python:3.10

WORKDIR /app

RUN apt update

RUN apt-get install -y libmagic-dev poppler-utils tesseract-ocr libreoffice pandoc libxml2 libxslt1-dev

COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "webapp.py"]
