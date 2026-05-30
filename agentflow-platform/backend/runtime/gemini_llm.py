import os
import uuid
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
import io
from routers.websocket import manager

load_dotenv()

class GeminiLLM:
    def __init__(self, model_name: str = "gemini-3.1-flash-lite", temperature: float = 0.7):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature

    async def generate_response(self, system_prompt: str, messages: list, run_id: str = None):
        """
        Generates a response from Gemini. Handles text and multimodal image generation.
        """
        # Pre-process messages
        messages = messages or []
        last_message_obj = messages[-1] if messages else {}
        last_content = last_message_obj.get("content", "") or last_message_obj.get("message", "") or ""
        
        # 1. Handle Multimodal Image Generation Models
        if "image-preview" in self.model_name or "nano-banana" in self.model_name:
            if run_id:
                await manager.broadcast(json.dumps({
                    "type": "log", "run_id": run_id, "message": f"🎨 Visual engine initializing for {self.model_name}..."
                }))
            
            processed_prompt = last_content
            try:
                import json as json_lib
                clean_content = str(last_content).strip()
                if clean_content.startswith("```json"):
                    clean_content = clean_content[7:].strip()
                if clean_content.endswith("```"):
                    clean_content = clean_content[:-3].strip()
                
                data = json_lib.loads(clean_content)
                if isinstance(data, dict):
                    processed_prompt = f"Subject: {data.get('subject', '')}. Style: {data.get('style', '')}. Lighting: {data.get('lighting', '')}. Composition: {data.get('composition', '')}. Mood: {data.get('mood', '')}."
            except Exception:
                processed_prompt = last_content

            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=[processed_prompt],
                config={"system_instruction": system_prompt}
            )

            result_text = ""
            image_filename = None
            
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        result_text += part.text
                    elif hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        image_uuid = str(uuid.uuid4())
                        image_filename = f"{image_uuid}.png"
                        static_dir = os.path.join(os.getcwd(), "static", "generated_images")
                        os.makedirs(static_dir, exist_ok=True)
                        file_path = os.path.join(static_dir, image_filename)
                        
                        try:
                            img = Image.open(io.BytesIO(image_data))
                            img.save(file_path)
                            if run_id:
                                await manager.broadcast(json.dumps({
                                    "type": "log", "run_id": run_id, "message": "📸 Image rendered and saved successfully."
                                }))
                        except Exception:
                            with open(file_path, "wb") as f:
                                f.write(image_data)
            
            if image_filename:
                image_url = f"/static/generated_images/{image_filename}"
                # Smart Content Passing: Show text only if it's not raw JSON
                final_text = result_text.strip()
                if not final_text and last_content:
                    try:
                        import json as json_lib
                        json_lib.loads(str(last_content).strip())
                        # If JSON, it's a prompt, suppress it
                        final_text = ""
                    except:
                        # Not JSON, likely blog content, keep it
                        final_text = last_content
                
                return f"![Generated Image]({image_url})\n\n{final_text}".strip(), 1000
            return result_text or "Image generation failed.", 0

        # 2. Handle Legacy Image Models (Imagen)
        if "imagen" in self.model_name:
            if run_id:
                await manager.broadcast(json.dumps({
                    "type": "log", "run_id": run_id, "message": "🖌️ Triggering Imagen engine..."
                }))
            
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=str(last_content) or "A beautiful painting",
                config={"number_of_images": 1}
            )
            
            if hasattr(response, 'generated_images') and response.generated_images:
                image_data = response.generated_images[0].image_bytes
                import base64
                base64_image = base64.b64encode(image_data).decode('utf-8').strip().replace('\n', '').replace('\r', '')
                return f"![Generated Image](data:image/png;base64,{base64_image})", 1000
            return "Failed to generate image.", 0

        # 3. Standard Text Generation
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "model"
            msg_text = msg.get("content") or msg.get("message") or ""
            contents.append({"role": role, "parts": [{"text": str(msg_text)}]})

        # Logic for tool handling
        final_tool_output = ""
        try:
            from .tools import AVAILABLE_TOOLS
            
            # YouTube Logic
            if "youtube.com" in str(last_content) or "youtu.be" in str(last_content):
                import re
                yt_match = re.search(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([0-9A-Za-z_-]{11})', str(last_content))
                if yt_match:
                    full_url = yt_match.group(0)
                    if run_id:
                        await manager.broadcast(json.dumps({
                            "type": "log", "run_id": run_id, "message": "📥 Fetching YouTube transcript..."
                        }))
                    transcript = AVAILABLE_TOOLS["youtube_transcript"].invoke(full_url)
                    final_tool_output = f"\n\n[SYSTEM: TOOL OUTPUT - YOUTUBE TRANSCRIPT]\n{transcript}\n"
                    if run_id:
                        await manager.broadcast(json.dumps({
                            "type": "log", "run_id": run_id, "message": f"✅ Transcript received ({len(transcript)} chars)."
                        }))
            
            # Scraper Logic
            elif "http" in str(last_content) and "url_scraper" in str(system_prompt).lower():
                import re
                url_match = re.search(r'https?://[^\s]+', str(last_content))
                if url_match:
                    url = url_match.group(0)
                    if run_id:
                        await manager.broadcast(json.dumps({
                            "type": "log", "run_id": run_id, "message": f"🌐 Scraping content from {url}..."
                        }))
                    scraped = AVAILABLE_TOOLS["url_scraper"].invoke(url)
                    final_tool_output = f"\n\n[SYSTEM: TOOL OUTPUT - WEBSITE CONTENT]\n{scraped}\n"
                    if run_id:
                        await manager.broadcast(json.dumps({
                            "type": "log", "run_id": run_id, "message": "✅ Website data extracted."
                        }))

        except Exception as e:
            print(f"Tool trigger error: {e}")

        # Inject tool output
        if final_tool_output and contents:
            try:
                contents[-1]["parts"][0]["text"] += final_tool_output
            except Exception:
                pass

        # Google Search grounding
        tools_config = None
        if "web_search" in str(system_prompt).lower() and not final_tool_output:
            tools_config = [{"google_search": {}}]
            if run_id:
                await manager.broadcast(json.dumps({
                    "type": "log", "run_id": run_id, "message": "🔍 Activating Google Search grounding..."
                }))

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={
                    "system_instruction": system_prompt,
                    "temperature": self.temperature,
                    "tools": tools_config
                }
            )
        except Exception as e:
            return f"Error communicating with AI: {str(e)}", 0
        
        extracted_text = ""
        try:
            if hasattr(response, 'text') and response.text:
                extracted_text = response.text
            elif hasattr(response, 'parts') and response.parts is not None:
                for part in response.parts:
                    if hasattr(part, 'text') and part.text:
                        extracted_text += part.text
            if not extracted_text and hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    c_content = candidate.content
                    if hasattr(c_content, 'parts') and c_content.parts is not None:
                        for p in c_content.parts:
                            if hasattr(p, 'text') and p.text:
                                extracted_text += p.text
        except Exception:
            pass

        # Estimate tokens if metadata not found
        token_count = len(extracted_text.split()) + 50
        if hasattr(response, 'usage_metadata'):
            token_count = response.usage_metadata.total_token_count

        return extracted_text.strip() or "The agent analyzed the data but returned no text.", token_count
