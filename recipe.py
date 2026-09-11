import google.genai as genai 
from dotenv import load_dotenv
load_dotenv()
import json

client = genai.Client()

def generate_recipe(ingredients, cuisine, diet):
    prompt = f"Generate one food receipe using these ingredients: {','.join(ingredients)} Cuisine: {cuisine} Diet: {diet}"

    chat = client.chats.create(model="gemini-3.6-flash")
    response = chat.send_message(prompt)
    with open("food_recipe.txt", 'w', encoding='utf-8') as file:
        file.write(response.text)

    recipe_data = {
        "ingredients": ingredients,
        "cuisine": cuisine,
        "diet": diet,
        "receipe": response.text
    }

    with open("food_recipe.json", 'w', encoding='utf-8') as file:
        json.dump(recipe_data, file, indent=2, ensure_ascii=False)
    return response

result = generate_recipe(['Rice', 'Tomatoes', 'Meat', 'Maggi Seasoning','Vegetable Oil','Salt'], 'West African', 'Omivorous')
print("\n" + "="*50)
print("🍽️ YOUR RECIPE:")
print("="*50)
print(result.text)