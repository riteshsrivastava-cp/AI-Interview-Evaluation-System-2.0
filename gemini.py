from google import genai
import time

client = genai.Client()

for attempt in range(5):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What is Machine Learning?"
        )

        print(response.text)
        break

    except Exception as e:
        print(f"Attempt {attempt+1} failed")
        print(e)
        time.sleep(15)