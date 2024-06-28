import scrapy


class DatabricksRuntimeInfo(scrapy.Item):
    runtime_version = scrapy.Field()
    is_lts = scrapy.Field()
    is_ml = scrapy.Field()
    is_gpu_accelerated = scrapy.Field()
    spark_version = scrapy.Field()
    scala_version = scrapy.Field()
    delta_lake_version = scrapy.Field()
    release_date = scrapy.Field()
    end_of_support_date = scrapy.Field()
    url = scrapy.Field()
    installed_libraries = scrapy.Field()


class InstalledLibrary(scrapy.Item):
    group_id = scrapy.Field()
    artifact_id = scrapy.Field()
    artifact_version = scrapy.Field()
