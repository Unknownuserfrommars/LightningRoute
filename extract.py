# backend/extract.py
import openai
import os
import json

class GPTProcessor:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")

        # print(f"Retrieved API Key: {self.api_key}")

        # Set the global openai.api_key directly
        self.client = openai.Client(api_key=self.api_key)

    def extract_knowledge(self, text):
        try:
            prompt = f"""
            You are a knowledgeable assistant that helps extract and organize information into hierarchical structures.
            Extract key knowledge points from the following text and organize them into a hierarchical structure.
            Format the output as a JSON array with nodes having 'id', 'title', and 'children' fields.

            Text: {text}
            """
            # TODO: Add option for "New learners" and "Experienced learners" to the button
            # Use the ChatCompletion endpoint
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a knowledgeable assistant that helps extract and organize "
                            "information into hierarchical structures."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the text from the first choice
            content = response["choices"][0]["message"]["content"]
            knowledge_points = json.loads(content)
            return knowledge_points

        except Exception as e:
            raise Exception(f"Error in knowledge extraction: {str(e)}")
