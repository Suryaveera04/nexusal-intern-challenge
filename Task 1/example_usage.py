import asyncio
import os
from telecom_responder import handle_message


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


async def main():
    load_env()
    
    response = await handle_message(
        customer_message="My mobile data is not working",
        customer_id="CUST123",
        channel="whatsapp"
    )
    
    print(f"Response: {response.channel_formatted_response}")
    print(f"Confidence: {response.confidence}")
    print(f"Action: {response.suggested_action}")
    if response.error:
        print(f"Error: {response.error}")


if __name__ == "__main__":
    asyncio.run(main())
