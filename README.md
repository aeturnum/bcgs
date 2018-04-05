# Basic Breitbart comment scraper

This is setup as a flask application so it can be deployed simply. Next
steps are to add a tiny HTML frontent that allows the user to enter a
breitbart story URL.

In theory this should work for any disqus client, though you'd need to
scrape their API Key

## todos:

* find the API key automatically instead of hardcoding it
* add feontent
* ERROR HANDLING
* Support for backing database for comments, summary dumps of comments &
  users
