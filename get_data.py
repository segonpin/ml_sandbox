import os
import requests

DATA_DIR = "data"
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATA_DIR))

# wget "http://s3.amazonaws.com/h2o-public-test-data/smalldata/prostate/prostate.csv.zip" -O $DATA_DIR/prostate.csv.zip
# unzip $DATA_DIR/prostate.csv.zip -d $DATA_DIR

# wget "https://h2o-public-test-data.s3.amazonaws.com/smalldata/diabetes/dataset_diabetes.zip" -O $DATA_DIR/dataset_diabetes.zip
# unzip $DATA_DIR/dataset_diabetes.zip -d $DATA_DIR

# wget "http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-test.csv" -O $DATA_DIR/zillow-test.csv
# wget "http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-train.csv" -O $DATA_DIR/zillow-train.csv

DATASETS = {
    "prostate": [
        "http://s3.amazonaws.com/h2o-public-test-data/smalldata/prostate/prostate.csv.zip",
    ],
    "diabetes": [
        "https://h2o-public-test-data.s3.amazonaws.com/smalldata/diabetes/dataset_diabetes.zip",
    ],
    "zillow": [
        "http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-test.csv",
        "http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-train.csv",
    ],
}

def unzip_file(f):
    import zipfile
    with zipfile.ZipFile(f,"r") as zip_ref:
        file_path = os.path.dirname(f)
        zip_ref.extractall(file_path)

def download_dataset(name):
    downloaded_files = []
    for url in DATASETS[name]:
        response = requests.get(url, stream=True)

        dataset_path = os.path.join(DATA_PATH, name)
        os.makedirs(dataset_path, exist_ok=True)
        local_file = os.path.join(dataset_path, os.path.basename(url))

        with open(local_file, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024*1024): # tdqm(response.iter_content(chunk_size=1024), unit="kB"):
                handle.write(chunk)
        downloaded_files.append(local_file)

    for local_file in downloaded_files:
        if os.path.splitext(local_file)[-1] == ".zip":
            unzip_file(local_file)


def main():
    os.makedirs(DATA_PATH, exist_ok=True)

    download_dataset("prostate")

if __name__ == "__main__":
    main()
