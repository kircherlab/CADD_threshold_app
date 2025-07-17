FROM python:3.12.11

# Create app user and home directory

RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /home/app

RUN chown app:app -R /home/app

# Get app data from repository
USER app
RUN git clone https://github.com/kircherlab/CADD_threshold_app.git /home/app

# Install shiny-server and dependencies
USER root
RUN apt update && apt install -y \
    install gdebi-core \
    && rm -rf /var/lib/apt/lists/*
RUN wget https://download3.rstudio.org/ubuntu-20.04/x86_64/shiny-server-1.5.23.1030-amd64.deb
RUN gdebi shiny-server-1.5.23.1030-amd64.deb

COPY /home/app/shiny-server.conf /etc/shiny-server/shiny-server.conf
RUN chmod 644 /etc/shiny-server/shiny-server.conf && \
    chown root:root /etc/shiny-server/shiny-server.conf

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Set port and run shiny-server
USER app
RUN mkdir -p /home/app/log
EXPOSE 8080
CMD [ "shiny-server"]
#CMD [ "python", "-m", "shiny", "run", "--port", "8080", "--host", "0.0.0.0", "--reload", "app.py"]
