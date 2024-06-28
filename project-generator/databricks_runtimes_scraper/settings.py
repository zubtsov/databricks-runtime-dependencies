from constants import AWS_CLOUD_NAME, AZURE_CLOUD_NAME, GCP_CLOUD_NAME

BOT_NAME = "databricks_runtimes_scraper"

SPIDER_MODULES = ["databricks_runtimes_scraper.spiders"]
NEWSPIDER_MODULE = "databricks_runtimes_scraper.spiders"

# Cloud specific settings
# Amazon Web Services
AWS_BASE_PATH = 'https://docs.databricks.com/en/release-notes/runtime/'
AWS_RELEASES_URL = f'{AWS_BASE_PATH}index.html'

AWS_LTS_RELEASES_XPATH = '//div[@id="supported-databricks-runtime-lts-releases"]//table//tr[td]'
AWS_ALL_RELEASES_XPATH = '//div[@id="all-supported-databricks-runtime-releases"]//table//tr[td]'
AWS_ALL_RELEASES_HEADER_XPATH = '//div[@id="all-supported-databricks-runtime-releases"]//table//tr//th/p'

AWS_INSTALLED_JAVA_SCALA_LIBS_XPATH = '//div[@id="installed-java-and-scala-libraries-scala-212-cluster-version"]//table//tr[td]'
AWS_INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH = '//div[@id="cpu-clusters"]//table//tr[td]'
AWS_INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH = '//div[@id="gpu-clusters"]//table//tr[td]'

AWS_SCALA_VERSION_XPATH = '//li/p[strong[text()="Scala"]]/text()'
AWS_DELTA_LAKE_VERSION_XPATH = '//li/p[strong[text()="Delta Lake"]]/text()'

# Microsoft Azure
AZURE_BASE_PATH = 'https://learn.microsoft.com/en-us/azure/databricks/release-notes/runtime/'
AZURE_RELEASES_URL = AZURE_BASE_PATH

AZURE_LTS_RELEASES_XPATH = '//table[1]//tr[td]'
AZURE_ALL_RELEASES_XPATH = '//table[2]//tr[td]'

AZURE_INSTALLED_JAVA_SCALA_LIBS_XPATH = '//table[3]//tr[td]'
AZURE_INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH = '//table[3]//tr[td]'
AZURE_INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH = '//table[4]//tr[td]'

AZURE_SCALA_VERSION_XPATH = '//li[strong[text()="Scala"]]/text()'
AZURE_DELTA_LAKE_VERSION_XPATH = '//li[strong[text()="Delta Lake"]]/text()'

# Google Cloud Platform
GCP_BASE_PATH = 'https://docs.gcp.databricks.com/en/release-notes/runtime/'
GCP_RELEASES_URL = f'{GCP_BASE_PATH}index.html'

# Project specific settings
BASE_PATH = {
    AZURE_CLOUD_NAME: AZURE_BASE_PATH,
    AWS_CLOUD_NAME: AWS_BASE_PATH,
    GCP_CLOUD_NAME: GCP_BASE_PATH
}

RELEASES_URL = {
    AZURE_CLOUD_NAME: AZURE_RELEASES_URL,
    AWS_CLOUD_NAME: AWS_RELEASES_URL,
    GCP_CLOUD_NAME: GCP_RELEASES_URL
}
LTS_RELEASES_XPATH = {
    AZURE_CLOUD_NAME: AZURE_LTS_RELEASES_XPATH,
    AWS_CLOUD_NAME: AWS_LTS_RELEASES_XPATH,
    GCP_CLOUD_NAME: AWS_LTS_RELEASES_XPATH
}
ALL_RELEASES_XPATH = {
    AZURE_CLOUD_NAME: AZURE_ALL_RELEASES_XPATH,
    AWS_CLOUD_NAME: AWS_ALL_RELEASES_XPATH,
    GCP_CLOUD_NAME: AWS_ALL_RELEASES_XPATH
}
RELEASE_INFO_XPATH = {
    AZURE_CLOUD_NAME: './/td[not(descendant::a)]/text()',
    AWS_CLOUD_NAME: './/td//p[not(descendant::a)]/text()',
    GCP_CLOUD_NAME: './/td//p[not(descendant::a)]/text()'
}
RUNTIME_VARIANTS_XPATH = {
    AZURE_CLOUD_NAME: './/td/a',
    AWS_CLOUD_NAME: './/td/ul/li/p/a',
    GCP_CLOUD_NAME: './/td/ul/li/p/a'
}

INSTALLED_JAVA_SCALA_LIBS_XPATH = {
    AZURE_CLOUD_NAME: AZURE_INSTALLED_JAVA_SCALA_LIBS_XPATH,
    AWS_CLOUD_NAME: AWS_INSTALLED_JAVA_SCALA_LIBS_XPATH,
    GCP_CLOUD_NAME: AWS_INSTALLED_JAVA_SCALA_LIBS_XPATH
}
INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH = {
    AZURE_CLOUD_NAME: AZURE_INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH,
    AWS_CLOUD_NAME: AWS_INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH,
    GCP_CLOUD_NAME: AWS_INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH
}
INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH = {
    AZURE_CLOUD_NAME: AZURE_INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH,
    AWS_CLOUD_NAME: AWS_INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH,
    GCP_CLOUD_NAME: AWS_INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH
}
INSTALLED_JAVA_SCALA_LIBRARY_XPATH = {
    AZURE_CLOUD_NAME: './/td/text()',
    AWS_CLOUD_NAME: './/td//p/text()',
    GCP_CLOUD_NAME: './/td//p/text()'
}
SCALA_VERSION_XPATH = {
    AZURE_CLOUD_NAME: AZURE_SCALA_VERSION_XPATH,
    AWS_CLOUD_NAME: AWS_SCALA_VERSION_XPATH,
    GCP_CLOUD_NAME: AWS_SCALA_VERSION_XPATH
}
DELTA_LAKE_VERSION_XPATH = {
    AZURE_CLOUD_NAME: AZURE_DELTA_LAKE_VERSION_XPATH,
    AWS_CLOUD_NAME: AWS_DELTA_LAKE_VERSION_XPATH,
    GCP_CLOUD_NAME: AWS_DELTA_LAKE_VERSION_XPATH
}

USER_AGENT = "http://github.com/zubtsov/databricks-runtime-dependencies"
ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0  # Cache never expires
HTTPCACHE_DIR = 'httpcache'  # Directory to store the cache
HTTPCACHE_IGNORE_HTTP_CODES = []  # List of HTTP codes to ignore
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
