#!/usr/bin/env python3
"""
extract_negative_treatments.py

A Python module that:
- Takes an integer id as input.
- Constructs a URL using the id to retrieve the HTML of a legal decision.
- Uses the OpenAI ChatGPT SDK to prompt the LLM to find referenced cases that have been treated negatively.
- Summarizes the results into a JSON structure.

Usage:
    python extract_negative_treatments.py <id>
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import openai
from openai import OpenAI

model = os.getenv("CHAT_GPT_MODEL", "gpt-3.5-turbo")

# Ensure your OpenAI API key is set in the environment variable OPENAI_API_KEY.
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    value = input(f"OPENAI_API_KEY is not set. Please enter your OpenAI API key: ")
    openai.api_key = value

def fetch_opinion(id: int) -> str:
    """
    Fetches and returns the text content from the legal decision HTML with the given id.
    
    Args:
        id (int): The id to be passed into the query.
    
    Returns:
        str: The extracted legal decision text.
    """
    url = f"https://scholar.google.com/scholar_case?case={id}"
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML using BeautifulSoup to extract visible text.
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # You can customize the extraction according to the structure of the page.
    # For now, we'll simply extract all text.
    opinion_text = soup.get_text(separator="\n", strip=True)
    return opinion_text

def get_negative_treatments(opinion_text: str) -> str:
    """
    Uses the OpenAI ChatGPT API to analyze a legal decision text and extract
    a list of referenced cases that have been treated negatively.
    
    Args:
        opinion_text (str): The legal decision text.
    
    Returns:
        str: A JSON list of information on cases that have negative treatment.
    """
    # Prepare the prompt for the ChatGPT model.
    prompt = (
        "You are an expert legal analyst."
        "A case is treated negatively if the opinion expresses disapproval or disagreement with the case, or ignores it as precedent."
        "Below is the text of a legal opinion that references other cases."
        "DO NOT CONSIDER THE OPINION ITSELF AS A REFERENCED CASE AND DO NOT RETURN IT IN THE RESULTS."
        "Identify any of the referenced cases that are treated negatively in the opinion."
        "For each of such cases, determine the nature of the treatment, quote the text of the negative treatment, and give an explanation of why the treatment was determined to be negative."
        "If there are cases that are treated negatively, return a JSON encoded list where each negatively-treated case is a JSON object with the following keys: ['caseName', 'jurisdiction', 'citation', 'nature', 'quotedText', 'explanation']."
        "If there are no cases treated negatively, respond EXACTLY with '[]'."
        "\n"
        f"Legal Opinion Text:\n{opinion_text}\n"
    )

    try:
        client = OpenAI()

        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": "You are a helpful lawyer."},
                {"role": "system", "content": "Your response will consist ONLY of a list."},
                {"role": "system", "content": "You will NOT wrap the response with JSON md markers."},
                {"role": "system", "content": "The response JSON will have NO top-level keys."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=1
        )
    except Exception as e:
        sys.exit(f"Error calling OpenAI API: {e}")

    return response.output_text

def main(id: int):
    print(f"Fetching legal decision text with id: {id}")
    opinion_text = fetch_opinion(id)
    
    print("Analyzing legal decision for negative case treatment using ChatGPT...")
    treatments = get_negative_treatments(opinion_text)

    if treatments == "[]":
        print("NO NEGATIVELY-TREATED CASES FOUND!")
        f.write("")
        return
    else:
        with open("results.json", "w") as f:
            f.write(treatments)

        print("\nFOUND NEGATIVELY-TREATED CASE(S) (see 'results.json'):")
        print(treatments)
        return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_negative_treatments.py <id>")
        sys.exit(1)

    id = sys.argv[1]
    main(id)
