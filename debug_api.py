import asyncio
import os
from openai import AsyncOpenAI


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


async def test_api():
    load_env()
    
    api_key = os.environ.get("XAI_API_KEY")
    print(f"API Key loaded: {api_key[:20]}...")
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )
    
    try:
        response = await client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "user", "content": "Say hello"}
            ]
        )
        print(f"Success! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_api())
