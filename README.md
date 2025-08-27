# CADD Threshold APP
#### This web application investigates the score distribution of known pathogenic and bening variants for different CADD PHRED-score thresholds.
#### The app was built with Shiny for Python and provides a framework for loading, processing and visualising data.

## Installation 
1. Clone the repository
```bash
git clone https://github.com/kircherlab/CADD_threshold_app.git
cd CADD_treshold_app
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the App Locally
```bash
python -m shiny run --port 8080 --host 0.0.0.0 app.py
```

## Running with Docker 
### The provided Dockerfile installs Shiny Server and app dependencies
## Build the Image
```bash 
docker build -t shiny-dashboard .
```

## Run the Container
```bash
docker run -p 8080:8080 shiny-dashboard
```

## Requirements
- Python 3.12+
- pandas
- pathlib
- anywidget
- shiny
- numpy
- plotly
- shinywidgets
- scikit-learn

