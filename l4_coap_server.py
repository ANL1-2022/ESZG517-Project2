import asyncio
import aiocoap
import aiocoap.resource as resource
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

light_state = {"state": "OFF"}


class LightResource(resource.Resource):
    async def render_get(self, request):
        payload = json.dumps(light_state).encode()
        logging.info(f"[GET] /light  ->  {light_state}")
        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

    async def render_put(self, request):
        try:
            data = json.loads(request.payload.decode())
            if "state" in data and data["state"] in ("ON", "OFF"):
                light_state.update(data)
                logging.info(f"[PUT] /light  ->  updated to {light_state}")
            else:
                logging.warning("[PUT] Invalid payload received")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logging.error(f"[PUT] Payload parse error: {e}")
        return aiocoap.Message(code=aiocoap.CHANGED)


async def main():
    root = resource.Site()
    root.add_resource(["light"], LightResource())

    await aiocoap.Context.create_server_context(root, bind=("localhost", 5683))
    logging.info("CoAP server listening on coap://localhost:5683/light")
    logging.info("Waiting for requests … (Ctrl+C to stop)")

    await asyncio.get_event_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
