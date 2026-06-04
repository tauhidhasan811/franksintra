# from src.services.prompt_templete import PromptGenerator
# from src.config.config_chat_model import ConfigOpenAI
# from dotenv import load_dotenv
# load_dotenv()


# prompt = PromptGenerator.gen_prompt(image_url="https://res.cloudinary.com/dhtiyigyy/image/upload/v1779690733/local_hgumf0.jpg")


# response = ConfigOpenAI().get_response(prompt)
# print(response)


from src.services.metada_seter import update_image_metadata
from src.config.config_cloudinary import ConfigCloudinary

cloudinary = ConfigCloudinary()
# ----------------------------------------------------------------------
# Example usage
# ----------------------------------------------------------------------
metadata = {
    "file_name": "nike-air-max-running-shoe-red",
    "title": "Nike Air Max - Mens Red Running Shoe",
    "caption": "Run faster and look better with Nike Air Max.",
    "description": (
        "Nike Air Max red running shoe designed for comfort and performance. "
        "Ideal for athletes and casual runners looking for premium footwear."
    ),
    "SEO_keywords": [
        "nike shoes",
        "air max",
        "running shoe",
        "red sneakers",
        "sports footwear",
    ],
    "assign_location": {
        "GPSLatitude": 23.8103,
        "GPSLatitudeRef": "N",
        "GPSLongitude": 90.4125,
        "GPSLongitudeRef": "E",
    },
}

new_path = update_image_metadata(
    image_path="local.jpg",
    output_data=metadata,
    cloudinary=cloudinary
)

print("Saved:", new_path)