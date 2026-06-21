import google.generativeai as genai
from PIL import Image

vision_model = genai.GenerativeModel("gemini-2.5-flash")

def generate_image_caption(image_path):

    image = Image.open(image_path)

    response = vision_model.generate_content([
        image,
        "Describe this image in one short sentence for document retrieval."
    ])

    return response.text.strip()


# from transformers import AutoProcessor, AutoModelForCausalLM
# from PIL import Image
# import torch

# print("Loading Florence-2 model...")

# model = AutoModelForCausalLM.from_pretrained(
#     "microsoft/Florence-2-base",
#     trust_remote_code=True
# )

# processor = AutoProcessor.from_pretrained(
#     "microsoft/Florence-2-base",
#     trust_remote_code=True
# )

# print("Florence-2 loaded!")

# def generate_image_caption(image_path):

#     image = Image.open(image_path).convert("RGB")

#     prompt = "<MORE_DETAILED_CAPTION>"

#     inputs = processor(
#         text=prompt,
#         images=image,
#         return_tensors="pt"
#     )

#     generated_ids = model.generate(
#         input_ids=inputs["input_ids"],
#         pixel_values=inputs["pixel_values"],
#         max_new_tokens=128
#     )

#     generated_text = processor.batch_decode(
#         generated_ids,
#         skip_special_tokens=True
#     )[0]

#     return generated_text