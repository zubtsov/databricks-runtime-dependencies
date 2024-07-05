import logging
import re
import scrapy
from databricks_runtimes_scraper.items import InstalledLibrary, DatabricksRuntimeInfo


# TODO: Find a more elegant way to access settings instead of [self.settings['CLOUD_NAME']]

class DatabricksRuntimesSpider(scrapy.Spider):
    name = "databricks_runtimes"

    def start_requests(self):
        yield scrapy.Request(url=self.settings['RELEASES_URL'][self.settings['CLOUD_NAME']], callback=self.parse)

    def parse(self, response, **kwargs):
        releases = response.xpath(self.settings['ALL_RELEASES_XPATH'][self.settings['CLOUD_NAME']])
        for release_info in releases:
            print('aaal', release_info.xpath(self.settings['RELEASE_INFO_XPATH'][self.settings['CLOUD_NAME']]).getall())
            version, spark_version, release_date, end_of_support_date = \
                release_info.xpath(self.settings['RELEASE_INFO_XPATH'][self.settings['CLOUD_NAME']]).getall()
            variants_links = [ri.attrib.get('href') for ri in
                              release_info.xpath(self.settings['RUNTIME_VARIANTS_XPATH'][self.settings['CLOUD_NAME']])]

            for vl in variants_links:
                url = response.urljoin(vl)
                version_number = re.sub(r'[^0-9\.]', '', version)
                is_lts = version.upper().endswith('LTS')
                is_ml = 'ml' in vl.removesuffix('.html').lower()

                runtime_info = {
                    'runtime_version': version_number,
                    'is_lts': is_lts,
                    'is_ml': is_ml,
                    'spark_version': spark_version,
                    'release_date': release_date,
                    'end_of_support_date': end_of_support_date,
                    'url': url,
                }
                yield response.follow(vl, callback=self.parse_installed_libraries,
                                      cb_kwargs={"runtime_info": runtime_info})

    def parse_installed_libraries(self, response, runtime_info):
        if runtime_info["is_ml"]:
            for is_gpu_accelerated, installed_libraries_xpath in [
                (True, self.settings['INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH'][self.settings['CLOUD_NAME']]),
                (False, self.settings['INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH'][self.settings['CLOUD_NAME']])
            ]:
                installed_libraries = self.parse_libraries(response, installed_libraries_xpath)
                yield DatabricksRuntimeInfo(
                    **runtime_info,
                    is_gpu_accelerated=is_gpu_accelerated,
                    installed_libraries=installed_libraries
                )
        else:
            scala_version = response.xpath(
                self.settings['SCALA_VERSION_XPATH'][self.settings['CLOUD_NAME']]).get().strip(': ')
            delta_lake_version = response.xpath(
                self.settings['DELTA_LAKE_VERSION_XPATH'][self.settings['CLOUD_NAME']]).get().strip(': ')
            installed_libraries = self.parse_libraries(response, self.settings['INSTALLED_JAVA_SCALA_LIBS_XPATH'][
                self.settings['CLOUD_NAME']])
            yield DatabricksRuntimeInfo(
                **runtime_info,
                is_gpu_accelerated=None,
                scala_version=scala_version,
                delta_lake_version=delta_lake_version,
                installed_libraries=installed_libraries
            )

    def parse_libraries(self, response, installed_libraries_xpath):
        installed_libraries = []
        for lib in response.xpath(installed_libraries_xpath):
            try:
                group_id, artifact_id, artifact_version = lib.xpath(self.settings['INSTALLED_JAVA_SCALA_LIBRARY_XPATH'][
                                                                        self.settings['CLOUD_NAME']]).getall()
                installed_library = InstalledLibrary(
                    group_id=group_id,
                    artifact_id=artifact_id,
                    artifact_version=artifact_version
                )
                installed_libraries.append(installed_library)
            except Exception as e:
                logging.error(e)  # TODO: use logging

        return installed_libraries
