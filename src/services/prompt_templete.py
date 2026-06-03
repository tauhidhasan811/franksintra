import json


class PromptGenerator:

    OUTPUT_FORMAT = {
        "file_name": "SEO-friendly lowercase hyphenated filename without extension (e.g., 'nike-air-max-running-shoe-red')",
        "title": "Short, compelling product or image title (e.g., 'Nike Air Max - Mens Red Running Shoe')",
        "caption": "One-sentence engaging social media caption for this image",
        "SEO_keywords": ["list", "of", "5-10", "relevant", "SEO", "keywords"],
        "description": "2-3 sentence detailed product/image description optimized for SEO",
        "assign_location": "Physical location or region visible or inferable from the image (e.g., 'New York, USA'). Use 'Unknown' if not determinable.",

        "gmb_post": {
            "title": "Short, catchy title with relevant emojis (e.g., '✨ Make Laundry Day Effortless! ✨')",
                    # Leave "" if title cannot be determined
            "intro": "One engaging opening sentence that hooks the reader and introduces the product/service",
                    # Leave "" if not enough product context
            "body": "2-3 sentences describing the product value proposition and who it is for",
                    # Leave "" if not enough product context
            "features": [
                "✅ Key feature or benefit",
                # 3-5 bullet points. Leave [] if no features can be identified
            ],
            "closing": "One sentence summarizing the overall benefit and encouraging the reader",
                    # Leave "" if not determinable
            "cta": "Call-to-action line with phone emoji (e.g., '📞 Contact us today to learn more!')",
                    # Leave "" if not determinable
            "hashtags": [
                "#RelevantHashtag"
                # 8-12 total hashtags mixing product, industry, and lifestyle tags
                # Leave [] if topic/product is completely unclear
            ]
        }
    }



    @staticmethod
    def _text_message(role: str, text: str) -> dict:
        return {
            "role": role,
            "content": [
                {
                    "type": "input_text",
                    "text": text
                }
            ]
        }

    @staticmethod
    def InitialPrompt() -> list:
        return [
            PromptGenerator._text_message(
                "system",
                "You are a helpful assistant. Be concise, friendly, and accurate."
            ),
            PromptGenerator._text_message(
                "user",
                "Start the conversation with a short helpful greeting."
            )
        ]

    @staticmethod
    def GeneralPrompt(
        user_query: str,
        relevent_info=None,
        previous_chat=None,
        file_data=None
    ) -> list:
        file_context = "No uploaded file data."
        if file_data and file_data.get("is_read"):
            file_context = file_data.get("data", "")

        return [
            PromptGenerator._text_message(
                "system",
                (
                    "You are a helpful assistant. Use previous conversation, relevant "
                    "knowledge, and uploaded file content when they help answer the user."
                )
            ),
            PromptGenerator._text_message(
                "user",
                (
                    f"Previous conversation:\n{previous_chat or 'No previous conversation.'}\n\n"
                    f"Relevant knowledge:\n{relevent_info or 'No relevant knowledge.'}\n\n"
                    f"Uploaded file content:\n{file_context}\n\n"
                    f"User request:\n{user_query}"
                )
            )
        ]

    @staticmethod
    def _build_system_instruction() -> str:
        schema = json.dumps(PromptGenerator.OUTPUT_FORMAT, indent=2)
        return (
            "You are an expert image analyst and SEO content specialist.\n"
            "When given an image, extract structured marketing and SEO metadata from it.\n"
            "Always respond with a single valid JSON object - no markdown, no explanation, no extra text.\n"
            "Your response must strictly follow this JSON schema:\n"
            f"{schema}\n"
            "Rules:\n"
            "- Every field is required. Never omit a field.\n"
            "- SEO_keywords must be a JSON array of 5 to 10 strings.\n"
            "- file_name must be lowercase, hyphen-separated, and contain no spaces or special characters.\n"
            "- If a field cannot be determined from the image, use the string 'Unknown'.\n"
            "- Output must be parseable by Python's json.loads()."
        )

    @staticmethod
    def gen_prompt(image_url: str) -> list:
        """
        Generates the initial prompt to analyze an image and return structured JSON metadata.
        """
        return [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": PromptGenerator._build_system_instruction()
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze the image below and return a single JSON object "
                            "with all required fields filled in based on what you see."
                        )
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]

    @staticmethod
    def regenerate_prompt(
        previous_response: dict,
        update_field_name: str,
        user_instruction: str | None,
        image_url: str ) -> list:
        """
        Generates a prompt to update a specific field in a previous response.

        Args:
            previous_response:  The full JSON dict returned from the previous gen_prompt call.
            update_field_name:  The exact field key to update (e.g., 'caption', 'gmb_post').
            user_instruction:   The user's specific instruction for how to change that field.
            image_url:          The original image URL for visual context.
        """
        valid_fields = list(PromptGenerator.OUTPUT_FORMAT.keys())
        if update_field_name not in valid_fields:
            raise ValueError(
                f"Invalid field '{update_field_name}'. Must be one of: {valid_fields}"
            )

        previous_json = json.dumps(previous_response, indent=2)
        instruction = (
            user_instruction
            or f"Regenerate '{update_field_name}' with a fresh, accurate, SEO-friendly alternative."
        )

        prompt =  [ {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are an expert image analyst and SEO content specialist.\n"
                            "You will receive a previously generated JSON metadata object and a user instruction "
                            "to update exactly ONE specific field.\n"
                            f"Rules:\n"
                            f"- Update ONLY the '{update_field_name}' field.\n"
                            "- Copy all other fields EXACTLY as they appear in the previous response.\n"
                            "- Apply the user's instruction precisely to generate the new value.\n"
                            "- Return a single valid JSON object with all fields present.\n"
                            "- No markdown, no explanation, no extra text - only the JSON object.\n"
                            "- Output must be parseable by Python's json.loads()."
                        )
                    }
                ]
            },
            { "role": "user",
                "content": [ {
                        "type": "input_text",
                        "text": (
                            f"Previous JSON response:\n{previous_json}\n\n"
                            f"Field to update: '{update_field_name}'\n"
                            f"User instruction: {instruction}\n\n"
                            f"Return the full updated JSON object with only '{update_field_name}' changed."
                        )
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]

        return prompt
