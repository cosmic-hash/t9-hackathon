from typing import Optional, List, Dict
import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fdaDataProcessing import generic_fetch_summary


class HtmlParser:
    def __init__(self, imprint: str) -> None:
        self.imprint_code: str = imprint
        self.url: str = (
            f"https://www.drugs.com/imprints.php?imprint={self.imprint_code}&color=&shape=0"
        )
        self.soup: Optional[BeautifulSoup] = None
        self.imprints: List[str] = []
        self.pill_names: List[str] = []
        self.pill_descriptions: List[Dict[str, str]] = []
        self.output_imprint: Optional[str] = None  # Example: Manufacturer name
        self.output_name: Optional[str] = None    # Example: Drug classification
        self.output_summary: Optional[str] = None 

    def _fetch_html(self) -> bool:
        """
        Fetches HTML content from the provided URL

        Returns:
            bool: True if successful, False otherwise

        Expected Output:
            Prints nothing on success
            Prints error message on failure
        """
        try:
            headers: Dict[str, str] = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            response: requests.Response = requests.get(
                self.url, headers=headers, timeout=10
            )
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, "html.parser")
            return True
        except RequestException as e:
            print(f"Error fetching URL: {e}")
            return False

    def parse_content(self) -> None:
        """
        Parses HTML content according to specifications:
        - get imprints
        - get pill name (generic name as per fda guidelines)
        - get pill description

        Returns:
            None

        Expected Output:
            Populates class attributes:
            - imprints: List of imprint codes
            - pill_names: List of pill names
            - pill_descriptions: List of dictionaries with description key-value pairs
        """
        self._fetch_html()  # Fetching HTML content
        if not self.soup:
            print("HTML content not loaded")
            return

        # Parse imprints
        imprint_divs: List[Tag] = self.soup.find_all(
            "div", class_="ddc-pid-card-header"
        )
        self.imprints = [
            div.find("h2").get_text(strip=True)  # type: ignore
            for div in imprint_divs
            if div.find("h2")
        ]

        # Parse pill names
        name_links: List[Tag] = self.soup.find_all("a", class_="ddc-text-size-small")
        self.pill_names = [link.get_text(strip=True) for link in name_links]

        # Parse pill descriptions
        desc_dls: List[Tag] = self.soup.find_all("dl")
        for dl in desc_dls:
            items: Dict[str, str] = {}
            dts: List[Tag] = dl.find_all("dt")
            dds: List[Tag] = dl.find_all("dd")

            for dt, dd in zip(dts, dds):
                key: str = dt.get_text(strip=True)
                value: str = dd.get_text(strip=True)
                items[key] = value
            self.pill_descriptions.append(items)
        print("htlm parser=",self.imprint_code, self.pill_names[0])   
        self.output_imprint=self.imprint_code
        self.output_name=self.pill_names[0]
        self.output_summary = generic_fetch_summary(self.imprint_code ,self.pill_names[0])
        print(self.imprint_code, self.pill_names[0], self.output_summary)




    def print_results(self) -> None:
        """
        Prints parsed results to console

        Returns:
            None

        Expected Output:
            Example console output:

            === Parsed Results ===

            Imprint: ABC123
            Pill Name: Aspirin
            Description:
              Dosage: 81 mg
              Manufacturer: Bayer
            ----------------------------------------
        """
        print("\n=== Parsed Results ===")

        for imprint, name, desc in zip(
            self.imprints, self.pill_names, self.pill_descriptions
        ):
            print(f"\nImprint: {imprint}")
            print(f"Pill Name: {name}")
            print("Description:")
            for key, value in desc.items():
                print(f"  {key}: {value}")
            print("-" * 40)


# Example usage with expected output
if __name__ == "__main__":
    imprint: str = input("Enter code: ")
    parser = HtmlParser(imprint)
    if parser.fetch_html():
        parser.parse_content()
        parser.print_results()
    else:
        print("Failed to fetch HTML content")
