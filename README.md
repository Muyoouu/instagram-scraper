
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<div align="center">
<img src="img/Logo.png" width="20%" height="20%">
<h2 align="center">google-scraper</h2>

  <p align="center">
    Python and Scrapy-based Google's search result scraping software
    <br />
    <br />
</div>


<!-- ABOUT THE PROJECT -->
## About The Project

Scraping data from Google search results can be challenging due to two main obstacles. Firstly, Google's search results are dynamic and constantly changing, making it difficult to extract accurate and reliable data consistently. Secondly, Google has robust bot detection measures in place, which pose a significant obstacle to gathering data from their website.
To conquer these challenges, a specialized web scraping software solution has been developed with the following features:

1. **Dynamic Web Page Navigation:** The software is equipped with intelligent algorithms that effortlessly navigate through Google's dynamic web pages, ensuring accurate data collection regardless of how frequently the pages change.

2. **Bypassing Bot Detection Measures:** A sophisticated proxy network has been integrated into the software to ensure that your scraping activities remain undetected as a bot by Google, allowing you to gather data seamlessly and without interruptions.

With this web scraping software, you can overcome the hurdles of scraping Google search results and extract the data you need efficiently and reliably..

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

* [![Python][Python.py]][Python-url]  
* [![Scrapy][Scrapy]][Scrapy-url]
* [![Pandas][Pandas]][Pandas-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

1. Activate Virtual Environment
   ```bash
   source env/bin/activate
   ```
2. Move inside the google_scraper/ directory
   ```bash
   cd google_scraper
   ```
3. Run the scrapy spider ("google_serp") to start scraping, specify the output file (JSON or CSV)
   ```bash
   scrapy crawl google_serp -o output/output.json
   ```
4. Run the analysis script
   ```bash
   python3 keyword_analysis.py
   ```

For project's complete demo see this [`Google Scraper Notion Page`](https://muyoouu.notion.site/Accurate-and-Anti-Bot-Google-Scraper-Built-with-Python-and-Scrapy-8d5a29a126ab402bb874551abf572eef?pvs=4)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See [`LICENSE.txt`](LICENSE.txt) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Musa Yohanes - musayohanes00@gmail.com

Project Link: [https://github.com/Muyoouu/google-scraper](https://github.com/Muyoouu/google-scraper)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* Credits to the README file template provided by [Best-README-Template](https://github.com/othneildrew/Best-README-Template), very helpful!

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Python.py]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[Scrapy]: https://img.shields.io/badge/scrapy-00a86b?style=for-the-badge&logo=python&logoColor=ffdd54
[Scrapy-url]: https://scrapy.org/
[Pandas]: https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white
[Pandas-url]: https://pandas.pydata.org/docs/