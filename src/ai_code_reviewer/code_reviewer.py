"""
Code reviewer module for analyzing code using Gemini AI.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown
import typer
from .gemini_client import GeminiAIClient
from rich.logging import RichHandler
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")
console = Console()

class ReviewMode(str, Enum):
    FILE = "file"
    PROJECT = "project"

app = typer.Typer(help="AI Code Reviewer - Review code using Google's Gemini AI")

class CodeReviewer:
    """Main code reviewer class for analyzing code files."""
    
    def __init__(self, client: Optional[GeminiAIClient] = None, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the code reviewer.
        
        Args:
            client (Optional[GeminiAIClient]): Gemini AI client instance
            max_retries (int): Maximum number of retry attempts for API calls
            retry_delay (int): Delay between retries in seconds
        """
        self.client = client if client is not None else GeminiAIClient(max_retries=max_retries, retry_delay=retry_delay)

    def load_guidelines(self, guidelines_path: Optional[str] = None) -> Optional[str]:
        """Load review guidelines from a file.
        
        Args:
            guidelines_path (Optional[str]): Path to the guidelines file
            
        Returns:
            Optional[str]: The guidelines content if file exists, None otherwise
        """
        if not guidelines_path:
            return None
            
        try:
            with open(guidelines_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Guidelines file not found: {guidelines_path}")
            return None

    def review_file(self, file_path: str, content: Optional[str] = None, guidelines: Optional[str] = None) -> str:
        """
        Review a single file.
        
        Args:
            file_path (str): Path to the file to review
            content (Optional[str]): File content. If not provided, will be read from file_path
            guidelines (Optional[str]): Optional review guidelines
            
        Returns:
            str: The review report formatted for inline comments
        """
        try:
            logger.info(f"Starting review for file: {file_path}")
            if content is None:
                logger.info(f"Reading content from file: {file_path}")
                with open(file_path, 'r') as f:
                    content = f.read()
            
            if guidelines:
                logger.info("Using provided review guidelines")
            else:
                logger.info("No specific guidelines provided, using default review criteria")
            
            logger.info("Sending content to Gemini AI for review")
            review = self.client.review_code(content, guidelines)
            logger.info("Successfully received review from Gemini AI")
            
            # Format the review for inline comments
            formatted_review = self._format_review_for_inline(review)
            return formatted_review
            
        except Exception as e:
            logger.error(f"Error reviewing file {file_path}: {str(e)}", exc_info=True)
            raise

    def _format_review_for_inline(self, review: str) -> str:
        """
        Format the review text for inline comments.
        
        Args:
            review (str): Raw review text from Gemini AI
            
        Returns:
            str: Formatted review text suitable for inline comments
        """
        # Split the review into sections
        sections = review.split('\n\n')
        formatted_sections = []
        
        for section in sections:
            if section.strip():
                # Add a header for each section
                formatted_sections.append(f"### Review Comment\n{section}")
        
        return '\n\n'.join(formatted_sections)

    def review_project(self, project_path: str, output_dir: str, 
                      exclude_dirs: Optional[List[str]] = None,
                      guidelines: Optional[str] = None) -> None:
        """
        Review all code files in a project directory.
        
        Args:
            project_path (str): Path to the project directory
            output_dir (str): Path to the output directory
            exclude_dirs (Optional[List[str]], optional): List of directories to exclude
            guidelines (Optional[str], optional): Optional review guidelines
        """
        project_path = Path(project_path)
        output_dir = Path(output_dir)
        exclude_dirs = set(exclude_dirs or [])
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create project-specific directory
        project_name = project_path.name
        project_output_dir = output_dir / project_name
        project_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all code files
        code_files = []
        for ext in ['.py', '.java', '.js', '.ts', '.cpp', '.c', '.h', '.hpp']:
            code_files.extend(project_path.rglob(f'*{ext}'))
            
        # Filter out excluded directories
        code_files = [f for f in code_files if not any(d in f.parts for d in exclude_dirs)]
        
        if not code_files:
            logger.warning(f"No code files found in {project_path}")
            return

        # Create all necessary output directories first
        logger.info(f"Creating output directory structure for project: {project_name}")
        for file_path in code_files:
            rel_path = file_path.relative_to(project_path)
            output_path = project_output_dir / rel_path.parent / f"{rel_path.stem}_review.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
        # Review each file with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Reviewing files...", total=len(code_files))
            
            for file_path in code_files:
                try:
                    # Create relative path for output, maintaining package structure
                    rel_path = file_path.relative_to(project_path)
                    output_path = project_output_dir / rel_path.parent / f"{rel_path.stem}_review.md"
                    
                    # Review the file
                    review = self.review_file(str(file_path))
                    
                    # Save the review
                    with open(output_path, 'w') as f:
                        f.write(f"# Code Review: {rel_path}\n\n")
                        f.write(review)
                        
                    progress.update(task, advance=1)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    progress.update(task, advance=1)
                    continue

@app.command()
def review(
    path: str = typer.Argument(..., help="Path to the file or project directory to review"),
    output_dir: str = typer.Argument(..., help="Directory to save review reports"),
    mode: ReviewMode = typer.Option(ReviewMode.PROJECT, "--mode", "-m", help="Review mode: 'file' or 'project'"),
    exclude_dirs: List[str] = typer.Option(None, "--exclude", "-e", help="Directories to exclude (only for project mode)"),
    guidelines_path: Optional[str] = typer.Option(None, "--guidelines", "-g", help="Path to review guidelines file"),
    max_retries: int = typer.Option(3, "--max-retries", "-r", help="Maximum number of retry attempts"),
    retry_delay: int = typer.Option(2, "--retry-delay", "-d", help="Delay between retries in seconds")
):
    """
    Review code using Google's Gemini AI. Can review either a single file or an entire project.
    """
    try:
        reviewer = CodeReviewer(max_retries=max_retries, retry_delay=retry_delay)
        guidelines = reviewer.load_guidelines(guidelines_path)
        
        if mode == ReviewMode.FILE:
            # Create output directory if it doesn't exist
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get the file name and create output path
            file_path = Path(path)
            output_path = output_dir / f"{file_path.stem}_review.md"
            
            # Review the file
            review = reviewer.review_file(str(file_path))
            
            # Save the review
            with open(output_path, 'w') as f:
                f.write(f"# Code Review: {file_path.name}\n\n")
                f.write(review)
                
            console.print(f"[green]Code review completed successfully! Review saved to: {output_path}[/green]")
        else:
            reviewer.review_project(path, output_dir, exclude_dirs, guidelines)
            console.print("[green]Code review completed successfully![/green]")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

def main():
    """Main entry point for the application."""
    app() 