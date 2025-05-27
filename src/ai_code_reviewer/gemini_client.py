"""
Gemini AI client for code review functionality.
"""

import os
import logging
import time
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")
console = Console()

class GeminiAIClient:
    """Client for interacting with Google's Gemini AI API."""
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the Gemini AI client.
        
        Args:
            max_retries (int): Maximum number of retries for API calls
            retry_delay (int): Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.console = Console()
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Get API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Please set GEMINI_API_KEY environment variable")
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('models/gemini-2.5-flash-preview-04-17')

    def review_code(self, code: str, guidelines: Optional[str] = None) -> str:
        """
        Review the given code using Gemini AI with retry logic.
        
        Args:
            code (str): The code to review
            guidelines (str, optional): Specific guidelines to follow during review
            
        Returns:
            str: The AI-generated code review
        """
        prompt = self._build_prompt(code, guidelines)
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to get review after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

    def _build_prompt(self, code: str, guidelines: Optional[str] = None) -> str:
        """
        Build the prompt for code review.
        
        Args:
            code (str): The code to review
            guidelines (str, optional): Specific guidelines to follow
            
        Returns:
            str: The formatted prompt
        """
        # Add line numbers to the code
        numbered_code = ""
        for i, line in enumerate(code.splitlines(), 1):
            numbered_code += f"{i:4d} | {line}\n"

        base_prompt = """
        Code to review (with line numbers):
        ```
        {code}
        ```
        """
        
        if guidelines:
            base_prompt = f"{guidelines}\n\n{base_prompt}"
            
        return base_prompt.format(code=numbered_code) 