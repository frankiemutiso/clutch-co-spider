import json
from clutch_scraper import ClutchScraper


def main():
    url = "https://clutch.co/us/agencies/digital-marketing"

    clutch_scraper = ClutchScraper()
    clutch_scraper.scrape(url)


if __name__ == "__main__":
    main()
