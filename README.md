# Basic Breitbart comment scraper

Provides a HTML frontent for capturing comments on a story on breitbart.

Users who are anonymous or have marked their profiles as "private" in the disqus system will not have their comments recorded or their profiles listed.

In theory this should work for any disqus client, though you'd need to scrape their API Key

Sample gunicorn run.sh and nginx config are included for convience

## todos:
* Make it a little prettier maybe
* find the API key automatically instead of hardcoding it
* Keep running database of users to reduce requests

The main bottleneck is that we can only request comments 100 at a time, but breitbart threads routinely have over 10,000 comments. That's 100 sequential requests!
