#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import pandas as pd
from elasticsearch import Elasticsearch, helpers

# Custom


##################
# Configurations #
##################

# Define connection details
HOST = "localhost"
PORT = 9200
SCHEME = "http"

# Define path to CSV file and index name in Elasticsearch
CSV_PATH = "cv-valid-dev.csv"
INDEX_NAME = "cv-transcriptions"

#############
# Functions #
#############


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean data by filling missing values and removing rows with missing 'generated_text'.

    Args:
        df (pd.DataFrame): DataFrame containing transcriptions.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    # Fill missing values with 'unknown'
    missing_count = df.isnull().sum().sum()
    df["age"].fillna("unknown", inplace=True)
    df["gender"].fillna("unknown", inplace=True)
    df["accent"].fillna("unknown", inplace=True)
    print(f"Filled {missing_count} missing value(s) with 'unknown'")

    # Remove rows where 'generated_text' is missing
    initial_count = len(df)
    df = df.dropna(subset=["generated_text"])
    dropped_count = initial_count - len(df)
    print(f"Removed {dropped_count} row(s) with missing 'generated_text'")

    return df


def read_csv_to_dict(csv_path: str = CSV_PATH) -> list[dict]:
    """
    Read CSV file and convert to a list of dictionaries.

    Args:
        csv_path (str): Path to CSV file.

    Returns:
        list[dict]: List of dictionaries.
    """
    df = pd.read_csv(csv_path)
    cleaned_df = clean_data(df)
    return cleaned_df.to_dict(orient="records")


def create_index(es_object: Elasticsearch, index_name: str = INDEX_NAME) -> bool:
    """
    Create an Elasticsearch index.

    Args:
        es_object: Elasticsearch object.
        index_name (str): Name of index.

    Returns:
        bool: True if index is created successfully.
    """
    try:
        es_object.indices.create(
            index=index_name,
            body={
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "generated_text": {"type": "text"},
                        "duration": {"type": "float"},
                        "age": {"type": "text"},
                        "gender": {"type": "text"},
                        "accent": {"type": "text"},
                    }
                },
            },
            ignore=400,
        )
        print(f"Created index {index_name}")
        return True
    except Exception as e:
        print(f"Failed to create index {index_name}: {e}")
        return False


def index_records(es_object: Elasticsearch, index_name: str, records: list[dict]):
    """
    Index records into Elasticsearch.

    Args:
        es_object: Elasticsearch object.
        index_name (str): Name of index.
        records (list[dict]): List of records.
    """
    try:
        actions = [
            {
                "_index": index_name,
                "_source": record,
            }
            for record in records
        ]
        helpers.bulk(es_object, actions)
        print(f"Indexed {len(records)} records into {index_name}")
    except Exception as e:
        print(f"Failed to index records into {index_name}: {e}")


def main():
    """
    Main function to process audio files and update CSV.
    """
    # Load mappings from CSV file
    records = read_csv_to_dict(CSV_PATH)

    # Connect to Elasticsearch at specified host and port
    es = Elasticsearch([{"host": HOST, "port": PORT, "scheme": SCHEME}])

    # Create index if it doesn't exist
    if create_index(es, INDEX_NAME):
        index_records(es, INDEX_NAME, records)


###########
# Classes #
###########


##########
# Script #
##########


if __name__ == "__main__":
    main()
