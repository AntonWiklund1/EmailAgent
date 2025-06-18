
import time
from typing import List, Dict
from llama_cloud_services import LlamaParse
import os
from dotenv import load_dotenv

load_dotenv()

parser = LlamaParse(
    api_key=os.getenv("LLAMAPARSE_API_KEY"),
    num_workers=4,       # if multiple files passed, split in `num_workers` API calls
    verbose=True,
    language="en",       # optionally define a language, default=en
)


def extract_from_file(file_path: str) -> List[Dict[str, str]]:
    """
    Submit a local file to LlamaParse and return extracted text sections
    """
    # Submit and poll
    result = parser.parse(file_path)
    markdown_documents = result.get_markdown_documents(split_by_page=True)

    full_text = ""
    for page in markdown_documents:
        full_text += page.text + "\n\n"

    return full_text


if __name__ == "__main__":
    # Example usage
    file_path = "Faktura_2071.pdf"  # Replace with your file path
    extracted_text = extract_from_file(file_path)
    print(extracted_text)