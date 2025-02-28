# RapidKL Ridership Web Crawler from data.gov.my Dashboard [Generated by AI]

This Python script fetches passenger volume data between RapidKL railway stations from the [data.gov.my](https://data.gov.my/dashboard/rapid-explorer) dashboard, processes it into daily and monthly ridership statistics, and saves the results as CSV files. It uses web scraping and parallel processing to efficiently collect data for multiple station pairs.

## Features
- Scrapes daily and monthly ridership data for RapidKL railway station pairs.
- Processes data into pandas DataFrames with formatted dates.
- Updates or appends to existing CSV files (`rapidkl_daily_ridership.csv` and `rapidkl_monthly_ridership.csv`).
- Uses multithreading with `ThreadPoolExecutor` for faster data retrieval.
- Handles errors gracefully with retries and timeouts.

## Prerequisites
- Python 3.6 or higher
- Git (optional, for cloning the repository)

## Installation (Run the commands below on "Anaconda Prompt" or "Command Prompt")
1. **Clone the Repository:** (or download the script directly):
   ```bash
   git clone https://github.com/yung666666/rapidkl-ridership-web-crawler.git
   cd rapidkl-ridership-web-crawler
   ```
2. **Install Dependencies:**
The script requires a few Python libraries. Install them using the provided requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```
The required libraries are:

- requests: For making HTTP requests to fetch web pages.
- beautifulsoup4: For parsing HTML content.
- pandas: For data manipulation and CSV handling.
- lxml: As the parser for BeautifulSoup.

## Usage
1. **Run the Script: Execute the script from the command line:**
   ```bash
   python rapidkl_ridership_web_crawler.py
   ```
2. **Output:**
The script generates two CSV files in the same directory:
- rapidkl_daily_ridership.csv: Daily ridership data with columns date, A_station, B_station, and ridership.
- rapidkl_monthly_ridership.csv: Monthly ridership data with columns month, A_station, B_station, and ridership.
If these files already exist, the script updates them with new data or appends as needed.

## How It Works
1. **Data Source:** Fetches data from [https://data.gov.my/dashboard/rapid-explorer}](https://data.gov.my/dashboard/rapid-explorer).
- Station Pairs: Extracts valid station pairs from a sample page’s JSON data, excluding "A0: All Stations" and self-pairs (A to A).
2. **Scraping:** Uses requests and BeautifulSoup to scrape JSON data embedded in the HTML.
3. **Processing:** Converts timestamps to human-readable dates and organizes data into pandas DataFrames.
4. **Storage:** Merges new data with existing CSV files, preserving historical data.

## Notes
1. Rate Limiting: The script includes a delay between retries (5 + random.uniform(1, 3) seconds) to avoid overwhelming the server. Be respectful of the data source’s terms of use.
2. Error Handling: If data for a station pair isn’t found or the request fails after retries, it skips that pair and continues.
3. Performance: Execution time depends on the number of station pairs and network speed. Multithreading significantly speeds up the process.
   
## Key Additions
1. You can set up Windows Task Scheduler to run the script monthly, ensuring you always obtain the latest ridership data.

## Acknowledgments
Data provided by data.gov.my.
Built with Python and open-source libraries.
