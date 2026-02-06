import asyncio
import os
from odyssey import Odyssey

async def main():
    api_key = os.environ.get("ODYSSEY_API_KEY")
    client = Odyssey(api_key=api_key)

    try:
        job = await client.simulate(
            script=[
                # Scene 1 — Man buys goat
                {
                    "timestamp_ms": 0,
                    "start": {
                        "prompt": (
                            "Ancient Indian village market. "
                            "A humble villager buys a healthy white goat "
                            "and carries it happily on his shoulders. "
                            "Traditional clothing, warm sunlight, rural setting."
                        )
                    }
                },

                # Scene 2 — First trickster
                {
                    "timestamp_ms": 4000,
                    "interact": {
                        "prompt": (
                            "A cunning man approaches and laughs, "
                            "telling the villager he is carrying a dog, not a goat. "
                            "The villager looks confused but continues walking."
                        )
                    }
                },

                # Scene 3 — Second trickster
                {
                    "timestamp_ms": 8000,
                    "interact": {
                        "prompt": (
                            "Another trickster stops the villager and mocks him, "
                            "insisting the animal is clearly a dirty stray dog. "
                            "The villager begins doubting himself."
                        )
                    }
                },

                # Scene 4 — Third trickster
                {
                    "timestamp_ms": 12000,
                    "interact": {
                        "prompt": (
                            "A third man loudly declares that carrying a dog "
                            "is shameful. The villager becomes frightened and uncertain."
                        )
                    }
                },

                # Scene 5 — Man abandons goat
                {
                    "timestamp_ms": 16000,
                    "interact": {
                        "prompt": (
                            "The villager panics, drops the goat, and runs away "
                            "in embarrassment and fear."
                        )
                    }
                },

                # Scene 6 — Tricksters celebrate
                {
                    "timestamp_ms": 20000,
                    "interact": {
                        "prompt": (
                            "The three tricksters gather, laugh loudly, "
                            "take the goat, and prepare a festive meal together. "
                            "Fire cooking scene, joyful celebration."
                        )
                    }
                },

                # End simulation
                {
                    "timestamp_ms": 24000,
                    "end": {}
                }
            ],
            portrait=False
        )

        print(f"Simulation started: {job.job_id}")

        while True:
            status = await client.get_simulate_status(job.job_id)

            if status.status == "completed":
                break
            if status.status == "failed":
                print(f"Simulation failed: {status.error_message}")
                return

            await asyncio.sleep(5)

        for stream in status.streams:
            recording = await client.get_recording(stream.stream_id)
            print("🎬 Panchatantra video:")
            print(recording.video_url)

    finally:
        await client.disconnect()

asyncio.run(main())
