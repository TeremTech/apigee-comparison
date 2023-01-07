"""Use this to tap all client APIs"""
import logging
import socket
import urllib3.exceptions
from time import sleep
from hashlib import md5
from itertools import product
from random import sample, random
from sqlite3 import connect
from datetime import datetime, timezone
from pathlib import Path

import requests

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_local_ip() -> str:
    """Try to automatically determine local IP so that at least one target is usable by default"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def main() -> None:
    # Every client should call every backend
    client_targets = list(product(CLIENT_URLS, TARGET_URLS))
    client_targets_length = len(client_targets)
    con = connect(Path(__file__).parent.parent / f"results-{datetime.now(timezone.utc)}.db")
    con.execute(
        "CREATE TABLE measurements(id INTEGER PRIMARY KEY, client TEXT, target TEXT, elapsed FLOAT, result TEXT)"
    )
    query_id = 1
    for run_number in range(RUNS):
        logger.info(f"Run number: {run_number + 1: 4d}/{RUNS}")
        # Randomise the order each run in order to minmise the effect of any cached network resolutions
        for client, target in sample(client_targets, k=client_targets_length):
            for _ in range(5):
                try:
                    response = requests.post(
                        url=client[1],
                        json={
                            'url': target[1],
                            # Use a unique payload for every request to prevent caching
                            'payload': str(query_id),
                        },
                        verify=False,  # Unless you generated certificates with the actual SANs
                        cert=(
                            Path(__file__).parent / 'coordinator_cert.pem',
                            Path(__file__).parent / 'coordinator_key.pem',
                        ),
                    )
                except Exception as e:
                    # Give the request a few tries; we don't want to fail the whole run if the local internet drops out
                    logger.warning(f"Processing {client[0]} to {target[0]} gave: {e}")
                    sleep(random() * 5)
                    continue
                if response.status_code == 200 and response.json():
                    break
            else:
                logger.warning(f"Processing {client[0]} to {target[0]} gave no usable response")
                continue
            if response.json()['result'] != md5(str(query_id).encode('utf-8')).hexdigest():
                # This really shouldn't happen, but we have the data so may as well verify we're getting valid results
                logger.warning(
                    f"Did not receive expected hash for {query_id}; got {response.json()['result']} "
                    f"instead of {md5(str(query_id).encode('utf-8')).hexdigest()}"
                )
            con.execute(
                "INSERT INTO measurements VALUES (?,?,?,?,?)",
                (query_id, client[0], target[0], response.json()['elapsed'], response.json()['result']),
            )
            query_id += 1
        con.commit()
    con.close()


RUNS = 1  # FIXME: Set this as desired

# FIXME: Update the URLs to match your environment
# (label, url), ...
CLIENT_URLS = [
    ('External', 'https://127.0.0.1:20456/measure'),
    # ('AWS', 'https://YOUR_DATA_HERE.ap-southeast-2.elb.amazonaws.com:20456/measure'),
    # ('GCP', 'https://YOUR_DATA_HERE:20456/measure'),
]
TARGET_URLS = [
    ('Direct/External', f'http://{get_local_ip()}:8080/md5'),  # Only useful for testing
    # ('Direct/AWS', 'http://YOUR_DATA_HERE.ap-southeast-2.elb.amazonaws.com:8080/md5'),
    # ('Direct/GCP', 'http://YOUR_DATA_HERE:8080/md5'),
    # ('Apigee X/AWS', 'https://YOUR_DATA_HERE.nip.io/aws'),
    # ('Apigee X/GCP', 'https://YOUR_DATA_HERE.nip.io/gcp'),
    # ('Apigee Hybrid (AWS)/AWS', 'https://YOUR_DATA_HERE/aws'),
    # ('Apigee Hybrid (AWS)/GCP', 'https://YOUR_DATA_HERE/gcp'),
    # ('Apigee Hybrid (GCP)/AWS', 'https://YOUR_DATA_HERE/aws'),
    # ('Apigee Hybrid (GCP)/GCP', 'https://YOUR_DATA_HERE/gcp'),
]

if __name__ == '__main__':
    main()
