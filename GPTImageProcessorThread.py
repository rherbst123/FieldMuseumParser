import base64
import requests
import os
from PIL import Image
from io import BytesIO

class GPTImageProcessorThread:
    #FINALLY GPT SUPPORT
    def __init__(self, api_key, prompt_text, urls, result_queue):
        self.api_key = api_key
        self.prompt_text = prompt_text
        self.urls = urls
        self.result_queue = result_queue
    
    def process_images(self):

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

       
        #same as the claude thread but with a different model
        for index, url in enumerate(self.urls):
            url = url.strip()
            try:
                response = requests.get(url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))

                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

                # you sneaky little thing
                payload = {
                       "model": "gpt-4o",
                      "messages": [
                 {
                     "role": "user",
                        "content": [
                {
                    "type": "text",
                    "text": self.prompt_text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
                  "max_tokens": 2048,
                  "temperature": 0,  #Change this value to adjust the randomness of the output (We want less randomness)
                  "seed": 42  
}

                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                response_data = response.json()

                output = self.format_response(f"Image {index + 1}", response_data, url)
                self.result_queue.put((image, output))

           

            except requests.exceptions.RequestException as e:
                error_message = f"Error processing image {index + 1}: {str(e)}"
                
               

    def format_response(self, image_name, response_data, url):
        if "choices" in response_data and response_data["choices"]:
            content = response_data["choices"][0].get("message", {}).get("content", "")
            formatted_output = f"{image_name}\nURL: {url}\n\n{content}\n"
        else:
            formatted_output = f"{image_name}\nURL: {url}\n\nNo data returned from API.\n"
        return formatted_output