import os
import requests
import hashlib

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
        ("http://s3.amazonaws.com/h2o-public-test-data/smalldata/prostate/prostate.csv.zip", "a81cec6688eb86be63f7a32193b1b92a"),
    ],
    "diabetes": [
        ("https://h2o-public-test-data.s3.amazonaws.com/smalldata/diabetes/dataset_diabetes.zip", ""),
    ],
    "zillow": [
        ("http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-test.csv", ""),
        ("http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-train.csv", ""),
    ],
}

def unzip_file(f):
    import zipfile
    with zipfile.ZipFile(f,"r") as zip_ref:
        file_path = os.path.dirname(f)
        zip_ref.extractall(file_path)

def maybe_unpack(local_file):
    if os.path.splitext(local_file)[-1] == ".zip":
        unzip_file(local_file)

def get_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def download_file(url, local_file):
    response = requests.get(url, stream=True)
    hash_md5 = hashlib.md5()
    with open(local_file, "wb") as handle:
        for chunk in response.iter_content(chunk_size=1024*1024): # tdqm(response.iter_content(chunk_size=1024), unit="kB"):
            hash_md5.update(chunk)
            handle.write(chunk)
    return hash_md5.hexdigest()

def download_dataset(name):
    downloaded_files = []
    for url, expected_md5 in DATASETS[name]:

        dataset_path = os.path.join(DATA_PATH, name)
        os.makedirs(dataset_path, exist_ok=True)
        local_file = os.path.join(dataset_path, os.path.basename(url))

        if os.path.exists(local_file):
            local_file_md5 = get_md5(local_file)
            if local_file_md5 == expected_md5:
                print(f"Skip downloading {url} since it exists already locally")
                continue

        hash = download_file(url, local_file)
        # downloaded_files.append((local_file, hash))

        print(f"Downloaded content to {local_file} with md5 {hash}")
        maybe_unpack(local_file)


def main():
    os.makedirs(DATA_PATH, exist_ok=True)

    download_dataset("prostate")
    download_dataset("diabetes")
    download_dataset("zillow")

if __name__ == "__main__":
    main()
