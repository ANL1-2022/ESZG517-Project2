import asyncio
import aiocoap
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SERVER_URI = "coap://localhost/light"


async def coap_get(protocol) -> float:
    start = time.perf_counter()
    request = aiocoap.Message(code=aiocoap.GET, uri=SERVER_URI)
    response = await protocol.request(request).response
    latency_ms = (time.perf_counter() - start) * 1000
    return response, latency_ms


async def coap_put(protocol, state: str) -> float:
    payload = json.dumps({"state": state}).encode()
    start = time.perf_counter()
    request = aiocoap.Message(code=aiocoap.PUT, uri=SERVER_URI, payload=payload)
    response = await protocol.request(request).response
    latency_ms = (time.perf_counter() - start) * 1000
    return response, latency_ms


async def main():
    protocol = await aiocoap.Context.create_client_context()
    latencies = []

    print("\n========== CoAP Client — 6-Step Demo ==========\n")

    # Step 1: GET initial state
    print("--- Step 1: GET initial light state ---")
    resp, lat = await coap_get(protocol)
    latencies.append(lat)
    print(f"  Payload : {resp.payload.decode()}")
    print(f"  Code    : {resp.code}  |  Latency: {lat:.2f} ms\n")

    # Step 2: PUT light ON
    print("--- Step 2: PUT light ON ---")
    resp, lat = await coap_put(protocol, "ON")
    latencies.append(lat)
    print(f"  Code    : {resp.code}  |  Latency: {lat:.2f} ms\n")

    # Step 3: GET after ON
    print("--- Step 3: GET state after ON ---")
    resp, lat = await coap_get(protocol)
    latencies.append(lat)
    print(f"  Payload : {resp.payload.decode()}")
    print(f"  Code    : {resp.code}  |  Latency: {lat:.2f} ms\n")

    # Step 4: PUT light OFF
    print("--- Step 4: PUT light OFF ---")
    resp, lat = await coap_put(protocol, "OFF")
    latencies.append(lat)
    print(f"  Code    : {resp.code}  |  Latency: {lat:.2f} ms\n")

    # Step 5: GET after OFF
    print("--- Step 5: GET state after OFF ---")
    resp, lat = await coap_get(protocol)
    latencies.append(lat)
    print(f"  Payload : {resp.payload.decode()}")
    print(f"  Code    : {resp.code}  |  Latency: {lat:.2f} ms\n")

    # Step 6: Latency summary
    print("--- Step 6: Latency Summary ---")
    labels = ["GET-initial", "PUT-ON", "GET-after-ON", "PUT-OFF", "GET-after-OFF"]
    for label, ms in zip(labels, latencies):
        print(f"  {label:<20}: {ms:.2f} ms")
    print(f"\n  Average latency : {sum(latencies)/len(latencies):.2f} ms")
    print(f"  Min             : {min(latencies):.2f} ms")
    print(f"  Max             : {max(latencies):.2f} ms")
    print("\n================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
