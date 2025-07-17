FROM python:3.12.11

# Install shiny-server
RUN apt update && apt install -y \
    gdebi-core \
    && rm -rf /var/lib/apt/lists/*
RUN wget https://download3.rstudio.org/ubuntu-20.04/x86_64/shiny-server-1.5.23.1030-amd64.deb \
    && gdebi -n shiny-server-1.5.23.1030-amd64.deb \
    && rm shiny-server-1.5.23.1030-amd64.deb


# install app dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade uvicorn \
    && pip install --no-cache-dir --upgrade -r requirements.txt

# Set port and run shiny-server
EXPOSE 7000
CMD [ "shiny-server"]
#CMD [ "python", "-m", "shiny", "run", "--port", "8080", "--host", "0.0.0.0", "--reload", "app.py"]
