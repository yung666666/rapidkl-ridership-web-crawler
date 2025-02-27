# RapidKL Ridership Web Crawler

This Python script fetches passenger volume data between RapidKL railway stations from the [data.gov.my](https://data.gov.my/dashboard/rapid-explorer/rail) dashboard, processes it into daily and monthly ridership statistics, and saves the results as CSV files. It uses web scraping and parallel processing to efficiently collect data for multiple station pairs.

## Features
- Scrapes daily and monthly ridership data for RapidKL railway station pairs.
- Processes data into pandas DataFrames with formatted dates.
- Updates or appends to existing CSV files (`rapidkl_daily_ridership.csv` and `rapidkl_monthly_ridership.csv`).
- Uses multithreading with `ThreadPoolExecutor` for faster data retrieval.
- Handles errors gracefully with retries and timeouts.

## Prerequisites
- Python 3.6 or higher
- Git (optional, for cloning the repository)

## Installation
1. **Clone the Repository:** (or download the script directly):
   ```bash
   git clone https://github.com/yung666666/rapidkl-ridership-web-crawler.git
   cd rapidkl-ridership-web-crawler
   ```
2. **Install Dependencies:**
The script requires a few Python libraries. Install them using the provided requirements.txt:
3. 
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
4. 
5. 
6. 

