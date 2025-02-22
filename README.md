# Google_search_scraper

Google Search Scraper is a Python-based tool that allows users to perform Google searches, extract search results, and save them to a CSV file. It uses **Selenium**, **BeautifulSoup**, and **Rich** to provide a user-friendly interface with enhanced search result presentation.

## Features
- Scrapes Google search results efficiently.
- Saves search results to a CSV file.
- Displays search results in a formatted table.
- Implements retry mechanism for failed searches.
- Uses a headless Chrome browser for automation.

## Installation
To install the necessary dependencies, run:

```sh
pip install -r requirements.txt
```

## Usage
Run the script with the following command:

```sh
python main.py
```

Follow the on-screen prompts to enter a search query and specify the number of results.

## Requirements
- Python 3.7+
- Google Chrome
- Chrome WebDriver (installed automatically using `webdriver-manager`)

## Output
- The search results are displayed in the terminal in a structured table format.
- The results are saved as a CSV file in the `output/` directory.

## Project Structure
```
📂 GoogleSearchScraper
├── 📂 output            # Directory to store search result CSV files
├── main.py             # Entry point for the search script
├── google_scraper.py   # Contains the scraping logic
├── requirements.txt    # Required dependencies
└── README.md           # Project documentation
```

## License
This project is open-source and available under the MIT License.

