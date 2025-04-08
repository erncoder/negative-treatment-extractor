#!/usr/bin/env python3
"""
legal_decision_negative_cases.py

A Python module that:
- Takes a slug string as input.
- Constructs a URL using the slug to retrieve the HTML of a legal decision.
- Uses the OpenAI ChatGPT SDK to prompt the LLM to find referenced cases that have been treated negatively.
- Summarizes the results into a JSON structure.

Usage:
    python legal_decision_negative_cases.py <slug>
"""

import sys
import json
import requests
from bs4 import BeautifulSoup
import openai
from openai import OpenAI
import os

# Ensure your OpenAI API key is set in the environment variable OPENAI_API_KEY.
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    value = input(f"OPENAI_API_KEY is not set. Please enter your OpenAI API key: ")
    openai.api_key = value

def fetch_legal_decision(slug: str) -> str:
    """
    Fetches and returns the text content from the legal decision HTML at the given slug.
    
    Args:
        slug (str): The slug to be inserted into the URL.
    
    Returns:
        str: The extracted legal decision text.
    """
    url = f"https://casetext/{slug}/html"
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML using BeautifulSoup to extract visible text.
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # You can customize the extraction according to the structure of the page.
    # For now, we'll simply extract all text.
    opinion_text = soup.get_text(separator="\n", strip=True)
    return opinion_text


def get_file_by_slug(slug: str) -> str:
    """
    Selects an HTML file from the 'test_data' directory whose filename (excluding the .html suffix) matches the provided slug.
    
    Args:
        slug (str): The slug to match against the filename.
    
    Returns:
        str: The path to the matching HTML file.
    """
    test_data_dir = "test_data"
    
    if not os.path.exists(test_data_dir) or not os.path.isdir(test_data_dir):
        sys.exit(f"Error: The directory '{test_data_dir}' does not exist or is not a directory.")
    
    # Construct the expected filename.
    expected_file = f"{slug}.html"
    file_path = os.path.join(test_data_dir, expected_file)
    
    if not os.path.exists(file_path):
        sys.exit(f"Error: No HTML file matching slug '{slug}' found in '{test_data_dir}'.")
    
    return file_path


def get_negative_treatments(opinion_text: str) -> list:
    """
    Uses the OpenAI ChatGPT API to analyze a legal decision text and extract
    a list of referenced cases that have been treated negatively.
    
    Args:
        opinion_text (str): The legal decision text.
    
    Returns:
        list: A list of cases (as strings) that have negative treatment.
    """
    # Prepare the prompt for the ChatGPT model.
    prompt = (
        "You are an expert legal analyst."
        "A case is treated negatively if the opinion expresses disapproval or disagreement with the case, or ignores it as precedent."
        "Below is the text of a legal opinion that references other cases."
        "DO NOT CONSIDER THE OPINION ITSELF AS A REFERENCED CASE AND DO NOT RETURN IT IN THE RESULTS."
        "Identify any of the referenced cases that are treated negatively in the opinion."
        "For each of such cases, determine the nature of the treatment, quote the text of the negative treatment, and give an explanation of why the treatment is negative."
        "If there are cases that are treated negatively, return a JSON encoded list where each negatively-treated case is a JSON object with the following keys: ['caseName', 'jurisdiction', 'citation', 'nature', 'quotedText', 'explanation']."
        "If there are no cases treated negatively, respond EXACTLY with '[]'."
        "\n"
        f"Legal Opinion Text:\n{opinion_text}\n"
    )

    try:
        client = OpenAI()

        response = client.responses.create(
            model="gpt-3.5-turbo",
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


def extract_text_from_html(file_path: str) -> str:
    """
    Reads an HTML file and extracts the visible text using BeautifulSoup.
    
    Args:
        file_path (str): The path to the HTML file.
    
    Returns:
        str: The extracted text content.
    """
    with open(file_path, "r", encoding="utf8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text

def main(slug: str):
    print(f"Fetching legal decision text for slug: {slug}")
    file = get_file_by_slug(slug)
    opinion_text = extract_text_from_html(file)
    
    print("Analyzing legal decision for negative case treatment using ChatGPT...")
    treatments = get_negative_treatments(opinion_text)

    if treatments == "[]":
        print("NO NEGATVIELY-TREATED CASES FOUND!")
        return
    else:
        with open("results.json", "w") as f:
            f.write(treatments)

        print("\nFOUND NEGATIVELY-TREATED CASE(S) (see 'results.json'):")
        print(treatments)
        return

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python legal_decision_negative_cases.py <slug>")
        sys.exit(1)
    slug_input = sys.argv[1]
    main(slug_input)
