import base64
import anthropic
import requests
from PIL import Image
from io import BytesIO

class ClaudeImageProcessorThread:

    def __init__(self, api_key, prompt_text, urls, result_queue):
        self.api_key = api_key
        self.prompt_text = prompt_text
        self.urls = urls
        self.result_queue = result_queue
        self.client = anthropic.Anthropic(api_key=self.api_key)

        print("ClaudeImageProcessor")


    def process_images(self):
        for index, url in enumerate(self.urls):
            url = url.strip()
            try:
                response = requests.get(url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))

                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=2500,
                    temperature=0,
                    system="You are an assistant that has a job to extract text from an image and parse it out. Only include the text that is relevant to the image. Do not Hallucinate",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": self.prompt_text},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": base64_image,
                                    },
                                },
                            ],
                        }
                    ],
                )

                output = self.format_response(f"Image {index + 1}", message.content, url)
                self.result_queue.put((image, output))

            except requests.exceptions.RequestException as e:
                error_message = f"Error processing image {index + 1}: {str(e)}"
                self.result_queue.put((None, error_message))

        # Signal that all processing is complete
        self.result_queue.put((None, None))

    def format_response(self, image_name, response_data, url):
        text_block = response_data[0].text
        lines = text_block.split("\n")

        formatted_result = f"{image_name}\n"
        formatted_result += f"URL: {url}\n\n"
        formatted_result += "\n".join(lines)

        return formatted_result
