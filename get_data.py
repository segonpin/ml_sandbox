import os
import requests
import hashlib
import logging

logging.basicConfig(format='%(asctime)s:%(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging.INFO)

DATA_DIR = "data"
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), DATA_DIR))

# TODO: Ideally we should check the md5hash before downloading the file and verify that it is the same as the expected one, 
# if it is the same, then we compare it with the hash of the file in the expected destination
DATASETS = {
    "prostate": [
        ("http://s3.amazonaws.com/h2o-public-test-data/smalldata/prostate/prostate.csv.zip", "a81cec6688eb86be63f7a32193b1b92a"),
    ],
    "diabetes": [
        ("https://h2o-public-test-data.s3.amazonaws.com/smalldata/diabetes/dataset_diabetes.zip", "f22425753cefbc18e321825450ec0f00"),
    ],
    "zillow": [
        ("http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-train.csv", "438f027384c5b52e555f35b755f53458"),
        ("http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-test.csv", "59f84ec230562b471a64d9a3ef52a66b"),
    ],
}

def list_datasets(print_details=False):
    logging.info("The following datasets are available")
    for dataset, details in DATASETS.items():
        logging.info(f"* {dataset}")
        if print_details:
            for url, hash in details:
                logging.info(f"  - {url} {hash}")

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
    logging.info(f"Downloading dataset {name}")
    downloaded_files = []
    for url, expected_md5 in DATASETS[name]:
        os.makedirs(DATA_PATH, exist_ok=True)
        dataset_path = os.path.join(DATA_PATH, name)
        os.makedirs(dataset_path, exist_ok=True)
        local_file = os.path.join(dataset_path, os.path.basename(url))

        if os.path.exists(local_file):
            local_file_md5 = get_md5(local_file)
            if local_file_md5 == expected_md5:
                logging.debug(f"Skip downloading {url} since it exists already locally")
                continue

        downloaded_md5 = download_file(url, local_file)
        if downloaded_md5 != expected_md5:
            logging.warning(f"Md5 for {url} was expected to be {expected_md5}, but it is {downloaded_md5}. Please update hash to avoid future downloads.")
        downloaded_files.append((local_file, hash))

        logging.debug(f"Downloaded content to {local_file} with md5 {hash}")
        maybe_unpack(local_file)
    if not downloaded_files:
        logging.info("Nothing downloaded since all files existed locally")
    return downloaded_files


def main():
    list_datasets(print_details=False)
    download_dataset("prostate")
    download_dataset("diabetes")
    download_dataset("zillow")

if __name__ == "__main__":
    main()
