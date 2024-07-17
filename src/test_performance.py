import pytest
import httpx
import asyncio
from time import time

BASE_URL = "http://127.0.0.1:8000"

ADDRESS_SEARCH_URL = BASE_URL + "/v1/addresses/search"


async def fetch(client, url):
    response = await client.post(
        url,
        params={
            "geometry_output_format": "ewkb"
        },
        json={
            "streets": {
                "codes": [1253198]
            },
            "addresses": {
                "plot_or_building_number": {
                    "exact": "18A"
                }
            }
        }
    )

    print(f"{response.status_code}")
    return response


@pytest.mark.asyncio
async def test_performance():
    async with httpx.AsyncClient(timeout=10.0) as client:
        urls = [ADDRESS_SEARCH_URL for _ in range(100)]
        start_time = time()
        tasks = [fetch(client, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        end_time = time()

        # Check all responses are 200
        assert all(response.status_code == 200 for response in responses)

        # Print total time taken
        print(f"Total time taken for 100 requests: {end_time - start_time} seconds")
