import os
import json
from google import genai
from google.genai import types

# 1. Setup the client
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')  # Ensure your API key is set in the environment

def extract_prayer_times(image_bytes):
    # 2. Define the desired output structure (Schema)
    # The model will try to fill this structure from the image.
    prayer_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "month": types.Schema(type=types.Type.STRING),
            "year": types.Schema(type=types.Type.INTEGER),
            "daily_times": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "day": types.Schema(type=types.Type.INTEGER, description="The day of the month"),
                        "Fajr": types.Schema(type=types.Type.STRING, description="Fajr time in HH:MM format"),
                        "Sunrise": types.Schema(type=types.Type.STRING, description="Sunrise time in HH:MM format"),
                        "Dhuhr": types.Schema(type=types.Type.STRING, description="Dhuhr time in HH:MM format"),
                        "Asr": types.Schema(type=types.Type.STRING, description="Asr time in HH:MM format"),
                        "Maghrib": types.Schema(type=types.Type.STRING, description="Maghrib time in HH:MM format"),
                        "Isha": types.Schema(type=types.Type.STRING, description="Isha time in HH:MM format"),
                    },
                    required=["day", "Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"],
                ),
            ),
        }
    )

    # 3. Create the image part and the text prompt
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    
    prompt = "Extract all the prayer times from this schedule image. Organize the data according to the provided JSON schema."

    # 4. Call the Gemini API
    # Note: Use a model with vision capabilities, like gemini-2.5-flash
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, image_part],
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=prayer_schema)
    )

    # 5. Return the structured JSON text
    return response.text

if __name__ == "__main__":
    client = genai.Client(api_key=GEMINI_API_KEY) # Assumes GEMINI_API_KEY is set in environment
    # Example usage with your image:
    # get the prayer time as bytes
    with open('prayer_times_december.png', 'rb') as img_file:
        image_bytes = img_file.read()
    extracted_json = extract_prayer_times(image_bytes)
    # write to json file
    with open('prayer_times_december.json', 'w') as json_file:
        json_file.write(extracted_json)