import json
import random


class PromptGenerator:

    OUTPUT_FORMAT = {
        "file_name": "SEO-friendly lowercase hyphenated filename without extension (e.g., 'nike-air-max-running-shoe-red')",
        "title": "Short, compelling product or image title (e.g., 'Nike Air Max - Mens Red Running Shoe')",
        "caption": "One-sentence engaging social media caption for this image",
        "SEO_keywords": ["list", "of", "5-10", "relevant", "SEO", "keywords"],
        "description": "2-3 sentence detailed product/image description optimized for SEO",
        "assign_location": {
            "GPSLatitude": 'float', 
            "GPSLatitudeRef": "N or S", 
            "GPSLongitude": 'float', 
            "GPSLongitudeRef": "E or W"
        },

        "gmb_post": {
            "title": "Short catchy title (under 60 characters) about the appliance service or job. No business name, no city.",
            "intro": "Opening sentence that names the business, the appliance service, and the city within its first 120 characters.",
            "body": "2-4 sentences on the problem and the expertise used to solve it. Do not repeat the business name.",
            "features": [],
            "closing": "One sentence on the benefits for the customer.",
            "cta": "One short plain-text call to action. No phone number and no business name.",
            "hashtags": []
        }
    }

    # Reasoning models ignore temperature, so variety comes from rotating the post angle.
    POST_STYLES = {
        "job_recap": (
            "Job recap: after the opening, tell what the customer's problem was, what the technician did, "
            "and how the appliance works now."
        ),
        "problem_solution": (
            "Problem and solution: after the opening, describe the symptom the customer noticed, "
            "what caused it, and how it was fixed."
        ),
        "expert_tip": (
            "Expert insight: after the opening, explain the repair and share one useful piece of advice "
            "that helps customers avoid the same problem."
        ),
        "before_after": (
            "Before and after: after the opening, contrast the appliance's condition before the service "
            "with the result after it."
        ),
        "local_neighbor": (
            "Local and friendly: after the opening, use a warm neighborly voice and connect the job to what "
            "local households deal with."
        ),
        "customer_question": (
            "Customer question: after the opening, answer a question customers often ask about this "
            "appliance problem, using the job as the example."
        ),
    }

    VARIETY_RULES = (
        "GMB post rules:\n"
        "- intro, body, closing and cta joined with spaces must total 400 to 650 characters.\n"
        "- The business name, the appliance service (e.g. 'refrigerator repair') and the city must all appear "
        "within the first 120 characters of the post.\n"
        "- Mention the business name exactly once in the whole post, in the intro.\n"
        "- Mention the city naturally 1 to 2 times in the whole post.\n"
        "- Write natural, engaging, professional content describing the problem, the expertise, "
        "and the customer benefits. Follow the chosen post style.\n"
        "- No hashtags, no phone numbers, no emojis, no keyword stuffing, and no repeated sentences or ideas.\n"
        "- title is separate from the post text and does not count toward the 400 to 650 characters; "
        "keep it under 60 characters with no business name, city, hashtags or emojis.\n"
        "- features must be [] and hashtags must be [].\n"
    )

    @staticmethod
    def pick_post_style(exclude: str | None = None) -> str:
        choices = [name for name in PromptGenerator.POST_STYLES if name != exclude]
        return random.choice(choices)

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
    def _build_system_instruction(assign_location: str, company_name: str, preference_instructions: str,
                                  post_style: str) -> str:
        schema = json.dumps(PromptGenerator.OUTPUT_FORMAT, indent=2)
        return (
            "You are an expert image analyst and SEO content specialist.\n"
            "When given an image, extract structured marketing and SEO metadata from it.\n"
            f"My Company Name is: {company_name}\n"
            "Your response tone should be user given preference instructions: " + preference_instructions + "\n"
            "Always respond with a single valid JSON object - no markdown, no explanation, no extra text.\n"
            "User provided assign_location for GPS metadata: " + assign_location + "\n"
            "Your response must strictly follow this JSON schema:\n"
            f"{schema}\n"
            "Rules:\n"
            "- Every field is required. Never omit a field.\n"
            "- SEO_keywords must be a JSON array of 5 to 10 strings.\n"
            "- file_name must be lowercase, hyphen-separated, and contain no spaces or special characters.\n"
            "- If a field cannot be determined from the image, use the string 'Unknown'.\n"
            "- Output must be parseable by Python's json.loads().\n"
            "Additional GMB Post Rules:\n"
            "- GMB posts must be written in a local SEO style.\n"
            f"Chosen post style for this GMB post: {PromptGenerator.POST_STYLES[post_style]}\n"
            f"{PromptGenerator.VARIETY_RULES}"
        )

    @staticmethod
    def gen_prompt(image_url: str, company_name: str, assign_location: str, preference_instructions: str,
                   post_style: str) -> list:
        """
        Generates the initial prompt to analyze an image and return structured JSON metadata.
        """
        return [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": PromptGenerator._build_system_instruction(assign_location=assign_location, 
                                                                          company_name = company_name,
                                                                          preference_instructions=preference_instructions,
                                                                          post_style=post_style)
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
        image_url: str,
        company_name: str,
        assign_location: str,
        preference_instructions: str,
        post_style: str) -> list:
        """
        Generates a prompt to rewrite a single field of a previous response.

        Args:
            previous_response:       The full JSON dict returned from the previous call.
            update_field_name:       The exact field key to update (e.g., 'caption', 'gmb_post').
            user_instruction:        The user's specific instruction for how to change that field.
            image_url:               The original image URL for visual context.
            company_name:            Company name from the original request.
            assign_location:         Location from the original request.
            preference_instructions: Tone preferences from the original request.
            post_style:              Post style to use; should differ from the previous one for gmb_post.
        """
        valid_fields = list(PromptGenerator.OUTPUT_FORMAT.keys())
        if update_field_name not in valid_fields:
            raise ValueError(
                f"Invalid field '{update_field_name}'. Must be one of: {valid_fields}"
            )

        field_schema = json.dumps({update_field_name: PromptGenerator.OUTPUT_FORMAT[update_field_name]}, indent=2)
        context_json = json.dumps(
            {key: value for key, value in previous_response.items() if key != update_field_name}, indent=2
        )
        previous_value = json.dumps(previous_response.get(update_field_name), indent=2)
        instruction = (
            user_instruction
            or f"Write a completely fresh version of '{update_field_name}'."
        )

        style_rules = ""
        if update_field_name == "gmb_post":
            style_rules = (
                f"New post style to use: {PromptGenerator.POST_STYLES[post_style]}\n"
                f"{PromptGenerator.VARIETY_RULES}"
            )

        prompt = [{
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are an expert image analyst and SEO content specialist.\n"
                            f"My Company Name is: {company_name}\n"
                            f"Location: {assign_location}\n"
                            f"Tone preference instructions: {preference_instructions}\n"
                            f"You will rewrite exactly ONE field: '{update_field_name}'.\n"
                            "Rules:\n"
                            "- Apply the user's instruction precisely.\n"
                            "- The previous value is shown only so you can avoid repeating it. Do not lightly edit it: "
                            "change the structure, opening, sentence patterns, and wording, not just a few words.\n"
                            "- Keep facts consistent with the image and the other fields.\n"
                            f"{style_rules}"
                            f"- Return a single valid JSON object with exactly one key, '{update_field_name}', "
                            "following this schema:\n"
                            f"{field_schema}\n"
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
                            f"Other fields (context only, do not return them):\n{context_json}\n\n"
                            f"Previous '{update_field_name}' (do not repeat it):\n{previous_value}\n\n"
                            f"User instruction: {instruction}\n\n"
                            f"Return only {{\"{update_field_name}\": ...}}."
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
