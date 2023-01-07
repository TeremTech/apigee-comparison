"""Latency measurement API"""
from datetime import datetime, timezone

import requests
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Measurement(BaseModel):
    """Data needed for a latency measurement"""
    url: str
    payload: str


@app.post("/measure")
async def measure(data: Measurement):
    start_time = datetime.now(timezone.utc)
    response = requests.post(
        url=data.url,
        json={'data': data.payload},
        verify=False,
    )
    end_time = datetime.now(timezone.utc)
    return {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'elapsed': response.elapsed.total_seconds(),
        'result': response.json()['hash'],
    }


if __name__ == '__main__':
    uvicorn.run(
        app,
        ssl_certfile='client_cert.pem',
        ssl_keyfile='client_key.pem',
        ssl_cert_reqs=1,
        ssl_ca_certs='coordinator_cert.pem',
        host="0.0.0.0",
        port=20456,
    )
