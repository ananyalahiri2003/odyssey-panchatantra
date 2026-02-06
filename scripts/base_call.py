import asyncio
import os
from odyssey import Odyssey, OdysseyAuthError, OdysseyConnectionError

async def main():
    ody_api_key=os.environ.get("ODYSSEY_API_KEY")
    client = Odyssey(api_key=ody_api_key)

    try:
        await client.connect(
            on_video_frame=lambda frame: print(f"Frame: {frame.width}x{frame.height}"),
            on_stream_started=lambda stream_id: print(f"Ready: {stream_id}"),
        )
        await client.start_stream("A cat", portrait=True)
        await client.interact("Pet the cat")
        await client.end_stream()
    except OdysseyAuthError:
        print("Invalid API key")
    except OdysseyConnectionError as e:
        print(f"Connection failed: {e}")
    finally:
        await client.disconnect()

asyncio.run(main())