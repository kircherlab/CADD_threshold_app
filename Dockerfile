FROM python:3.12.11



RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /home/app

RUN chown app:app -R /home/app

USER app

RUN git clone https://github.com/kircherlab/CADD_threshold_app.git /home/app

USER root
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

USER app
EXPOSE 8080
CMD [ "python", "-m", "shiny", "run", "--port", "8080", "--host", "0.0.0.0", "--reload", "app.py"]