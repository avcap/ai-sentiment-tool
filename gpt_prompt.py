# gpt_prompt.py

import openai
import os

# Set your OpenAI API key here or use environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(technical_summary):
    prompt = f"""
    You're a trading assistant. Based on the following market summary, provide a short sentiment report.

    Summary:
    {technical_summary}

    Response:
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or use "gpt-4" if available
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error getting GPT response: {e}"

