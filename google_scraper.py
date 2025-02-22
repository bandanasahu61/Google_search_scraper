from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import requests.exceptions
from pathlib import Path
import os

class GoogleScraper:
    def __init__(self, max_retries=3, timeout=30):
        self.console = Console()
        self.max_retries = max_retries
        self.timeout = timeout
        self.setup_driver()
        self.create_output_directory()

    def create_output_directory(self):
        """Create output directory if it doesn't exist"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

    def setup_driver(self):
        """Initialize and configure the Chrome WebDriver"""
        with self.console.status("[bold green]Setting up Chrome driver..."):
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--page-load-strategy=eager")
            
            # Add additional headers to appear more like a real browser
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            self.driver.set_script_timeout(self.timeout)

    def reset_driver(self):
        """Reset the web driver in case of timeout"""
        try:
            self.driver.quit()
        except:
            pass
        finally:
            self.setup_driver()

    def search_google(self, query, num_results=10):
        """Perform Google search and extract results"""
        search_url = f"https://www.google.com/search?q={query}&num={num_results}"
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                with self.console.status("[bold blue]Performing search...") as status:
                    self.driver.get(search_url)
                    
                    # Wait for search results
                    WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
                    )
                    
                    status.update("[bold blue]Extracting results...")
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    
                    search_results = []
                    with Progress() as progress:
                        task = progress.add_task("[green]Processing results...", total=num_results)
                        
                        for result in soup.select('div.g'):
                            try:
                                title_element = result.select_one('h3')
                                link_element = result.select_one('a')
                                description_element = result.select_one('div.VwiC3b')
                                
                                if title_element and link_element:
                                    title = title_element.get_text().strip()
                                    link = link_element['href']
                                    description = description_element.get_text().strip() if description_element else "No description available"
                                    
                                    search_results.append({
                                        'title': title,
                                        'link': link,
                                        'description': description
                                    })
                                    progress.advance(task)
                                    
                                    if len(search_results) >= num_results:
                                        break
                                        
                            except Exception as e:
                                self.console.print(f"[yellow]Warning: Skipped a result due to parsing error[/yellow]")
                                continue
                                
                    return search_results
                    
            except (TimeoutException, WebDriverException) as e:
                retry_count += 1
                if retry_count == self.max_retries:
                    self.console.print(f"[bold red]Failed after {self.max_retries} attempts. Error: {str(e)}[/bold red]")
                    return []
                self.console.print(f"[yellow]Attempt {retry_count}/{self.max_retries} failed. Retrying...[/yellow]")
                self.reset_driver()
                time.sleep(2 * retry_count)
                
        return []

    def save_to_csv(self, results, query):
        """Save search results to CSV file"""
        if not results:
            self.console.print("[yellow]No results to save[/yellow]")
            return None
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"output/search_results_{query.replace(' ', '_')}_{timestamp}.csv"
        
        try:
            with self.console.status("[bold green]Saving results to CSV..."):
                df = pd.DataFrame(results)
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                return filename
        except Exception as e:
            self.console.print(f"[bold red]Error saving results: {str(e)}[/bold red]")
            return None

    def display_results(self, results):
        """Display search results in a formatted table"""
        if not results:
            self.console.print("[yellow]No results to display[/yellow]")
            return
            
        table = Table(show_header=True, header_style="bold magenta", width=None)
        table.add_column("No.", style="dim", width=6)
        table.add_column("Title", style="bold", width=40)
        table.add_column("Link", style="blue", width=60)
        table.add_column("Description", style="green", width=80)

        for i, result in enumerate(results, 1):
            title = result['title'][:75] + "..." if len(result['title']) > 75 else result['title']
            link = result['link'][:55] + "..." if len(result['link']) > 55 else result['link']
            description = result['description'][:150] + "..." if len(result['description']) > 150 else result['description']
            
            table.add_row(
                str(i),
                title,
                link,
                description
            )

        self.console.print(Panel(table, title="[bold cyan]Search Results", border_style="cyan"))

    def close(self):
        """Clean up resources"""
        try:
            self.driver.quit()
        except:
            pass
