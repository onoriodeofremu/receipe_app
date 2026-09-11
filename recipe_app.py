"""Streamlit recipe generator built on the Gemini API.

Run with:  streamlit run recipe_app.py
"""

import json
import os
from datetime import datetime
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
import streamlit as st
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types

load_dotenv()

# Verified reachable on this API key; the 2.5 series 404s for new users.
MODELS = ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]

CUISINES = [
    "West African", "Nigerian", "Italian", "Mexican", "Indian", "Chinese",
    "Japanese", "Thai", "Mediterranean", "French", "Caribbean", "American",
]

DIETS = [
    "Omnivorous", "Vegetarian", "Vegan", "Pescatarian",
    "Gluten-free", "Dairy-free", "Low-carb / Keto", "Halal",
]

SYSTEM_INSTRUCTION = """You are a practical, experienced home cook.
Write one recipe in clean markdown using exactly these sections:

# <Recipe Name>
A one-sentence description.

**Prep:** X min | **Cook:** X min | **Serves:** N

## Ingredients
- Quantified list. Mark anything not supplied by the user with *(pantry)*.

## Instructions
1. Numbered steps, one action each.

## Tips
- Two or three short notes on substitutions or storage.

Use only the ingredients given plus common pantry staples. Respect the diet
strictly. Do not add commentary before or after the recipe."""


@st.cache_resource
def get_client():
    """One client per session, reused across reruns."""
    return genai.Client()


def build_prompt(ingredients, cuisine, diet, servings, notes):
    lines = [
        f"Ingredients: {', '.join(ingredients)}",
        f"Cuisine: {cuisine}",
        f"Diet: {diet}",
        f"Servings: {servings}",
    ]
    if notes:
        lines.append(f"Extra requirements: {notes}")
    return "Generate one food recipe.\n" + "\n".join(lines)


def stream_recipe(client, model, prompt, placeholder):
    """Stream the model response into `placeholder`, return the full text."""
    chunks = []
    stream = client.models.generate_content_stream(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )
    for chunk in stream:
        if chunk.text:
            chunks.append(chunk.text)
            placeholder.markdown("".join(chunks) + " ▌")
    recipe = "".join(chunks)
    placeholder.markdown(recipe)
    return recipe


st.set_page_config(page_title="Recipe Generator", page_icon="🍽️", layout="centered")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("🍽️ Recipe Generator")
st.caption("Tell it what's in your kitchen and it writes you a recipe.")

if not os.getenv("GOOGLE_API_KEY"):
    st.error("`GOOGLE_API_KEY` is not set. Add it to the `.env` file next to this script.")
    st.stop()

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", MODELS)
    cuisine = st.selectbox("Cuisine", CUISINES)
    diet = st.selectbox("Diet", DIETS)
    servings = st.slider("Servings", 1, 12, 4)
    notes = st.text_area(
        "Extra requirements",
        placeholder="e.g. under 30 minutes, no oven, extra spicy",
        height=80,
    )

raw_ingredients = st.text_area(
    "Ingredients (one per line, or comma separated)",
    value="Rice\nTomatoes\nMeat\nMaggi Seasoning\nVegetable Oil\nSalt",
    height=160,
)

ingredients = [
    item.strip()
    for line in raw_ingredients.splitlines()
    for item in line.split(",")
    if item.strip()
]

col_go, col_count = st.columns([1, 3])
with col_go:
    generate = st.button("Generate recipe", type="primary", use_container_width=True)
with col_count:
    st.write(f"**{len(ingredients)}** ingredient(s)")

if generate:
    if not ingredients:
        st.warning("Add at least one ingredient.")
    else:
        prompt = build_prompt(ingredients, cuisine, diet, servings, notes)
        placeholder = st.empty()
        try:
            with st.spinner("Cooking…"):
                recipe = stream_recipe(get_client(), model, prompt, placeholder)
        except Exception as exc:  # surface API/network errors in the UI
            placeholder.empty()
            text = str(exc)
            if "503" in text or "429" in text:
                st.error(
                    "The model is busy or you've hit a rate limit. "
                    "Try again, or pick a different model in the sidebar."
                )
            else:
                st.error(f"Generation failed: {exc}")
        else:
            st.session_state.history.insert(
                0,
                {
                    "generated_at": datetime.now().isoformat(timespec="seconds"),
                    "model": model,
                    "ingredients": ingredients,
                    "cuisine": cuisine,
                    "diet": diet,
                    "servings": servings,
                    "notes": notes,
                    "recipe": recipe,
                },
            )

if st.session_state.history:
    latest = st.session_state.history[0]
    if not generate:
        st.markdown(latest["recipe"])

    stem = f"recipe_{latest['generated_at'].replace(':', '-')}"
    dl_txt, dl_json = st.columns(2)
    with dl_txt:
        st.download_button(
            "Download .txt",
            data=latest["recipe"],
            file_name=f"{stem}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl_json:
        st.download_button(
            "Download .json",
            data=json.dumps(latest, indent=2, ensure_ascii=False),
            file_name=f"{stem}.json",
            mime="application/json",
            use_container_width=True,
        )

    if len(st.session_state.history) > 1:
        st.divider()
        st.subheader("Earlier this session")
        for entry in st.session_state.history[1:]:
            title = f"{entry['cuisine']} · {entry['diet']} · {entry['generated_at']}"
            with st.expander(title):
                st.markdown(entry["recipe"])
