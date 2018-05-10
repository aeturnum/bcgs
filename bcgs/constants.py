DISQUS_ID_RE = "var\s*disqus_identifier\s*=\s*'(\d+)'"
THREAD_DATA_RE = '<script type="text/json" id="disqus-forumData">(.*)</script>$'
# this probably changes
API_KEY = "E8Uh5l5fHZ6gD8U3KycjAIAk46f68Zw7C6eW8WSjZvCLXebZ7p0r1yrYDrLilk2F"

DEBUG = True
VERIFY_SSL = False

# keep files for two days
KEEP_XLSX_FOR = 60 * 60 * 24 * 2