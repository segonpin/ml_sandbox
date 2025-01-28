set -euxo pipefail

DATA_DIR=data
mkdir -p $DATA_DIR
wget "http://s3.amazonaws.com/h2o-public-test-data/smalldata/prostate/prostate.csv.zip" -O $DATA_DIR/prostate.csv.zip
unzip $DATA_DIR/prostate.csv.zip -d $DATA_DIR

