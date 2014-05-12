<h3>Why</h3>
This project aims to aggregate data from all US mutual funds. The primary motivator here is my desire to simplify my 401(K) investment analysis. I want a system where I could pick best funds globally (i.e., across providers) according to criteria I care about -- preferably in a queryable database. If you've tried this, you know it is fairly difficult get such cross-company aggregate data. There do exist APIs, but those are often overbudget for individual investors :-) 

<h3>How</h3>
This project aggregates profile, performance, and risk data for ~27,000 US mutual funds by combination of multi-site html downloading + scraping. The project, written in Python 2.7, primarily uses the requests and BeautifulSoup libraries. It'll, depending on your options, generate between 1 and 7GB of data after downloading. 

Upon data generation, you can feed it to PGSQL for querying and analysis. You've to know the knid of analysis you want to do with this. The code is not, meant to be a review of investment techniques and certainly does not claim to be investment advice. Please, respect laws, limits, terms of use, and know what you're doing. Enjoy!

