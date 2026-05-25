class PromptGenerator:
    @staticmethod
    def gen_prompt(image_url):
        output_format = {
            'product_name': "string",
            'file_name': "string",
            'brand_name': "string",
            'SEO_keywords': ["string"],
            'description': "string"
        }

        input_data = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are a helpful assistant that describes images in detail. "
                            "Extract information like product name, brand name, SEO keywords, description, "
                            "and SEO-friendly file name. "
                            f"Provide the output in this format {output_format}. "
                            "Respond strictly in JSON."
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "What's in this image?"},
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]
        return input_data