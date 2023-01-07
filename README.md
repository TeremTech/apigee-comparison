# API Latency Comparison

This repo contains all the tools needed to compare and analyse the latency/Round Trip Time of different API targets from
multiple client sources.

## Quick Start

```shell
bash gen_keys.sh  # Keys default to 14 day validity
docker run --rm -d -p 8080:8080 $(docker build -q ./backend/)  # Build and run the backend target API image
docker run --rm -d -p 20456:20456 $(docker build -q ./client/)  # Build and run the client API image
pip install -r coordinator/requirements.txt  # Ensure requests is installed
python coordinator/gather_data.py
```

Results are saved in a sqlite database in this directory and can be reviewed using
the [Jupyter Notebook](https://jupyter.org/) in `process_data` (it defaults to processing the pre-gathered data).

## Setup

You will want to build and deploy both the backend and client containers to locations other than your local machine to
get useful data. When deployed, add the associated URLs to `coordinator/gather_data.py` and execute the script with the
desired number of runs. URLs must be routable by all client nodes.

If using Apigee as an API Gateway, a simple passthrough proxy can be used to access the backend API. The backend URL
must be globally routable in this case.

## Reviewing data

The requirements for the [Jupyter Notebook](https://jupyter.org/) are in `process_data`. Ensure that the correct results
file is loaded for the `conn` value.

## Security

The backend API is completely unauthenticated and uses HTTP. While it does not handle sensitive data and the MD5 hashing
it does is unlikely to result in a DoS vector, the container should be removed when testing is completed.

The client API uses data supplied in the payload to choose its backend target. This would be useful to a DDoS attacker.
The container enforces authentication using TLS to limit the exposure of this API. The keys are generated
by `gen_keys.sh` and default to a 14-day lifespan.

## Developed By

This project was initially developed by [Terem](https://terem.tech/) to answer a common question from our
clients. [Get in touch with us](https://terem.tech/build-a-product/) if there are questions we can help you solve.

## License

[MIT](https://choosealicense.com/licenses/mit/)
