import asyncio
import os
from telecom_responder import handle_message


# Load API key from .env file
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
    
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("ERROR: XAI_API_KEY not found in environment")
        return
    
    print(f"Using API key: {api_key[:10]}...")
    print("Testing WhatsApp channel...\n")
    
    try:
        response = await handle_message(
            customer_message="My mobile data is not working",
            customer_id="CUST123",
            channel="whatsapp"
        )
        
        print(f"Response:\n{response.channel_formatted_response}")
        print(f"\nConfidence: {response.confidence}")
        print(f"Action: {response.suggested_action}")
        if response.error:
            print(f"Error: {response.error}")
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
