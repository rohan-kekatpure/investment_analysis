<h3>Why</h3>
I want to analyze my investments my way. Not through the interface of Fidelity, or Vanguard, or Schwab, but in single shot, in my own private database. I want a system where I could pick best funds across the above compaines according to performance criteria I cared about -- preferably in a queryable database. If you've tried this, you know it is fairly difficult get such cross-company aggregate data. There do exist APIs, but those, according to one email response I received, are statedly overbudget for individual investors :) 

<h3>How</h3>
This project aggregates profile, performance, and risk data for ~27,000 US mutual funds by combination of multi-site html downloading + scraping. The project, written in Python 2.7, primarily uses the requests and BeautifulSoup libraries. It'll, depending on your options, generate between 1 and 7GB of data after downloading. 

Upon data generation, you can feed it to PGSQL for querying and analysis. You've to know the knid of analysis you want to do with this. The code is not, meant to be a review of investment techniques and certainly does not claim to be investment advice. Please, respect laws, limits, terms of use, and know what you're doing. Enjoy!

