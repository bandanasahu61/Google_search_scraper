from google_scraper import GoogleScraper
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
import sys
import time
from pathlib import Path
import threading

class TimeoutError(Exception):
    pass

def timeout_handler():
    raise TimeoutError("Operation timed out")

def get_valid_number(console, default=10):
    while True:
        try:
            num = input(f"[bold cyan]Enter number of results to fetch (1-100) [default={default}]: [/bold cyan]")
            if not num:
                return default
            num = int(num)
            if 1 <= num <= 100:
                return num
            else:
                console.print("[yellow]Please enter a number between 1 and 100[/yellow]")
        except ValueError:
            console.print("[yellow]Please enter a valid number[/yellow]")

def main():
    console = Console()
    scraper = None
    
    try:
        # Create output directory
        Path("output").mkdir(exist_ok=True)
        
        # Initialize scraper
        scraper = GoogleScraper(max_retries=3, timeout=30)
        
        # Print welcome message
        welcome_text = Text()
        welcome_text.append("\n🔍 Google Search Scraper", style="bold cyan")
        welcome_text.append("\nA tool to scrape and analyze Google search results", style="italic")
        console.print(Panel(welcome_text, border_style="cyan"))

        while True:
            # Get user input
            query = Prompt.ask("\n[bold cyan]Enter your search query[/bold cyan] (or 'quit' to exit)")
            
            if query.lower() == 'quit':
                break
                
            # Get number of results with validation
            console.print()
            num_results = get_valid_number(console)
            
            # Display search info
            console.print(f"\n[bold]Searching for:[/bold] [green]{query}[/green]")
            console.print(f"[bold]Number of results:[/bold] [green]{num_results}[/green]\n")
            
            # Perform the search with timeout
            start_time = time.time()
            results = []
            
            # Create a timer for timeout
            timer = threading.Timer(300, timeout_handler)  # 5 minute timeout
            try:
                timer.start()
                results = scraper.search_google(query, num_results)
            except TimeoutError:
                console.print("[bold red]Search operation timed out![/bold red]")
                continue
            finally:
                timer.cancel()
            
            end_time = time.time()
            
            if results:
                # Display results
                scraper.display_results(results)
                
                # Save results
                output_file = scraper.save_to_csv(results, query)
                if output_file:
                    console.print(f"\n[bold green]✓[/bold green] Results saved to [blue]{output_file}[/blue]")
                
                # Display statistics
                console.print(f"\n[bold cyan]Search Statistics:[/bold cyan]")
                console.print(f"Time taken: {end_time - start_time:.2f} seconds")
                console.print(f"Results found: {len(results)}")
            else:
                console.print("[bold red]No results found![/bold red]")
            
            # Ask to continue
            continue_search = Prompt.ask(
                "\n[bold cyan]Would you like to perform another search?[/bold cyan]",
                choices=["y", "n"],
                default="y"
            )
            if continue_search.lower() != "y":
                break
        
    except KeyboardInterrupt:
        console.print("\n[bold red]Search cancelled by user[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An error occurred: {str(e)}[/bold red]")
    
    finally:
        # Clean up
        if scraper:
            scraper.close()
        console.print("\n[bold cyan]Search completed. Goodbye! 👋[/bold cyan]")

if __name__ == "__main__":
    main()
