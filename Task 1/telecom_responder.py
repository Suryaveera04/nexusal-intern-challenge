import asyncio
import json
import os
from dataclasses import dataclass
from typing import Literal, Optional

from openai import AsyncOpenAI


@dataclass
class MessageResponse:
    response_text: str
    confidence: float
    suggested_action: str
    channel_formatted_response: str
    error: Optional[str] = None


async def handle_message(
    customer_message: str,
    customer_id: str,
    channel: Literal["voice", "whatsapp", "chat"]
) -> MessageResponse:
    if not customer_message or customer_message.strip() == "":
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="request_valid_message",
            channel_formatted_response="",
            error="Empty customer message"
        )
    
    system_prompt = f"""You are a professional telecom customer support agent. Help customers with mobile network issues, billing, data plans, SIM issues, roaming, and connectivity problems.

Be polite, concise, and professional. Provide practical troubleshooting steps. Never fabricate account-specific data.

Channel-specific rules for {channel}:
{"- Maximum 2 sentences. Sound natural when spoken." if channel == "voice" else ""}
{"- Friendly conversational tone. Short paragraphs. Light emoji allowed." if channel == "whatsapp" else ""}
{"- Provide step-by-step instructions. Slightly more detailed explanations allowed." if channel == "chat" else ""}

You MUST respond with valid JSON only:
{{
  "response_text": "your response here",
  "confidence": 0.85,
  "suggested_action": "resolved|escalate|follow_up|request_info"
}}"""

    client = AsyncOpenAI(
        api_key=os.environ.get("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )
    
    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="grok-2-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": customer_message}
                ],
                max_tokens=500
            ),
            timeout=10.0
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        response_text = data["response_text"]
        confidence = max(0.0, min(1.0, data["confidence"]))
        suggested_action = data["suggested_action"]
        
        if channel == "voice":
            channel_formatted_response = response_text
        elif channel == "whatsapp":
            channel_formatted_response = f"Hi there! 👋\n{response_text}\n\nLet me know if you need more help."
        else:  # chat
            channel_formatted_response = response_text
        
        return MessageResponse(
            response_text=response_text,
            confidence=confidence,
            suggested_action=suggested_action,
            channel_formatted_response=channel_formatted_response
        )
        
    except asyncio.TimeoutError:
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="retry",
            channel_formatted_response="",
            error="API timeout"
        )
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            await asyncio.sleep(2)
            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model="grok-2-latest",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": customer_message}
                        ],
                        max_tokens=500
                    ),
                    timeout=10.0
                )
                
                content = response.choices[0].message.content
                data = json.loads(content)
                
                response_text = data["response_text"]
                confidence = max(0.0, min(1.0, data["confidence"]))
                suggested_action = data["suggested_action"]
                
                if channel == "voice":
                    channel_formatted_response = response_text
                elif channel == "whatsapp":
                    channel_formatted_response = f"Hi there! 👋\n{response_text}\n\nLet me know if you need more help."
                else:
                    channel_formatted_response = response_text
                
                return MessageResponse(
                    response_text=response_text,
                    confidence=confidence,
                    suggested_action=suggested_action,
                    channel_formatted_response=channel_formatted_response
                )
            except Exception as retry_error:
                return MessageResponse(
                    response_text="",
                    confidence=0.0,
                    suggested_action="escalate",
                    channel_formatted_response="",
                    error=f"API rate limit exceeded: {str(retry_error)}"
                )
        
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="escalate",
            channel_formatted_response="",
            error=f"AI service error: {error_msg}"
        )
