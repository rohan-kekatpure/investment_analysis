<h3>Why</h3>
The project started with my need for a unified analysis of US mutual funds -- a sizeable universe with dozens of companies each offering several fund classes having various mandates. While companies like Fidelity and Vanguard have search-and-compare functionalities, their paginated presentation formats, predefined search facets and restricted fund selections may not allow cross-company exploration for detail-oriented investors. Personally, I wanted a system where I could pick best funds across compaines according to performance criteria I cared about -- preferably in a queryable database. As I discovered, it is fairly difficult get such cross-company aggregate data. There do exist APIs, but those, according to one email response I received, are statedly overbudget for individual investors :) 

<h3>How</h3>
This project aggregates profile, performance, and risk data for ~27,000 US mutual funds by combination of multi-site html downloading + scraping. The project, written in Python 2.7, primarily uses the requests and BeautifulSoup libraries. It'll generate approimately 7GB of data after processing. 

Upon data generation, you can feed it to PGSQL for querying and analysis.

