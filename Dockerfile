FROM python:3.12.11

# Install shiny-server
USER root
RUN apt update && apt install -y \
    gdebi-core \
    && rm -rf /var/lib/apt/lists/*
RUN wget https://download3.rstudio.org/ubuntu-20.04/x86_64/shiny-server-1.5.23.1030-amd64.deb \
    && gdebi -n shiny-server-1.5.23.1030-amd64.deb \
    && rm shiny-server-1.5.23.1030-amd64.deb

# Set workdir directory
WORKDIR /home/shiny

# Get app data from repository
USER shiny
RUN git clone https://github.com/kircherlab/CADD_threshold_app.git /home/shiny/CADD_threshold_app

# config shiny server
USER root
RUN cp /home/shiny/CADD_threshold_app/shiny-server.conf /etc/shiny-server/shiny-server.conf \
    && chmod 644 /etc/shiny-server/shiny-server.conf \
    && chown root:root /etc/shiny-server/shiny-server.conf

# install app dependencies
RUN cd /home/shiny/CADD_threshold_app \
    && pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt

# Set port and run shiny-server
USER shiny
RUN mkdir -p /home/shiny/log
EXPOSE 8080
CMD [ "shiny-server"]
#CMD [ "python", "-m", "shiny", "run", "--port", "8080", "--host", "0.0.0.0", "--reload", "app.py"]
