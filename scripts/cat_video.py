import asyncio
import os
from odyssey import Odyssey

async def main():
    ody_api_key = os.environ.get("ODYSSEY_API_KEY")
    client = Odyssey(api_key=ody_api_key)

    try:
        job = await client.simulate(
            script=[
                {"timestamp_ms": 0, "start": {"prompt": "A cat sitting on a windowsill"}},
                {"timestamp_ms": 3000, "interact": {"prompt": "The cat watches a bird outside"}},
                {"timestamp_ms": 6000, "interact": {"prompt": "The cat stretches lazily"}},
                {"timestamp_ms": 9000, "end": {}}
            ],
            portrait=True
        )

        print(f"Simulation started: {job.job_id}")

        while True:
            status = await client.get_simulate_status(job.job_id)

            if status.status == "completed":
                break
            if status.status == "failed":
                print(f"Simulation failed: {status.error_message}")
                return
            if status.status == "cancelled":
                print("Simulation was cancelled")
                return

            await asyncio.sleep(5)

        for stream in status.streams:
            recording = await client.get_recording(stream.stream_id)
            print(f"Video URL: {recording.video_url}")

    finally:
        # This is the important part: close aiohttp sessions cleanly
        # Try disconnect() first (common in SDKs)
        if hasattr(client, "disconnect"):
            await client.disconnect()
        elif hasattr(client, "close"):
            await client.close()

asyncio.run(main())