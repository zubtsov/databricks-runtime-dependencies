import os

import requests
from lxml import html
import pandas as pd
from functools import cache

# TODO: implement using scrapy

AWS_CLOUD_NAME = 'aws'
AZURE_CLOUD_NAME = 'azure'
GCP_CLOUD_NAME = 'gcp'

# AWS
AWS_BASE_PATH = 'https://docs.databricks.com/en/release-notes/runtime/'
AWS_RELEASES_URL = f'{AWS_BASE_PATH}index.html'

AWS_LTS_RELEASES_XPATH = '//div[@id="supported-databricks-runtime-lts-releases"]//table'
AWS_ALL_RELEASES_XPATH = '//div[@id="all-supported-databricks-runtime-releases"]//table'

AWS_INSTALLED_JAVA_SCALA_LIBS_XPATH = '//div[@id="installed-java-and-scala-libraries-scala-212-cluster-version"]//table'
AWS_INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH = '//div[@id="cpu-clusters"]//table'
AWS_INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH = '//div[@id="gpu-clusters"]//table'

AWS_SCALA_VERSION_XPATH = '//li/p[strong[text()="Scala"]]/text()'
AWS_DELTA_LAKE_VERSION_XPATH = '//li/p[strong[text()="Delta Lake"]]/text()'

# Azure
AZURE_BASE_PATH = 'https://learn.microsoft.com/en-us/azure/databricks/release-notes/runtime/'
AZURE_RELEASES_URL = AZURE_BASE_PATH

AZURE_LTS_RELEASES_XPATH = '//table[1]'
AZURE_ALL_RELEASES_XPATH = '//table[2]'

AZURE_INSTALLED_JAVA_SCALA_LIBS_XPATH = '//table[3]'
AZURE_INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH = '//table[3]'
AZURE_INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH = '//table[4]'

AZURE_SCALA_VERSION_XPATH = '//li[strong[text()="Scala"]]/text()'
AZURE_DELTA_LAKE_VERSION_XPATH = '//li[strong[text()="Delta Lake"]]/text()'

# GCP
GCP_BASE_PATH = 'https://docs.gcp.databricks.com/en/release-notes/runtime/'
GCP_RELEASES_URL = f'{GCP_BASE_PATH}index.html'

# Common
OUTPUT_DIR = 'scraped'

RELEASES_OUTPUT_FILE_NAME = {
    AWS_CLOUD_NAME: f'releases-{AWS_CLOUD_NAME}.parquet',
    AZURE_CLOUD_NAME: f'releases-{AZURE_CLOUD_NAME}.parquet',
    GCP_CLOUD_NAME: f'releases-{GCP_CLOUD_NAME}.parquet'
}

INSTALLED_LIBRARIES_OUTPUT_FILE_NAME = {
    AWS_CLOUD_NAME: f'installed_libraries-{AWS_CLOUD_NAME}.parquet',
    AZURE_CLOUD_NAME: f'installed_libraries-{AZURE_CLOUD_NAME}.parquet',
    GCP_CLOUD_NAME: f'installed_libraries-{GCP_CLOUD_NAME}.parquet'
}

CLOUD_URL_SUFFIX = {
    AWS_CLOUD_NAME: ".html",
    AZURE_CLOUD_NAME: "",
    GCP_CLOUD_NAME: ".html"
}

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


@cache
def load_content(url):
    return requests.get(url).content


def extract_from_content(content, xpath):
    return html.tostring(html.fromstring(content).xpath(xpath)[0])


def extract_from_content2(content, xpath):
    return html.fromstring(content).xpath(xpath)


def load_table(url, xpath):
    content = load_content(url)
    table_html = extract_from_content(content, xpath)
    return pd.read_html(table_html)[0]


def scrape_releases(cloud):
    global size, build_relative_path, build_url, extract_version
    releases = load_table(RELEASES_URL[cloud], ALL_RELEASES_XPATH[cloud])
    size = len(releases)
    releases['spark_version'] = releases['Apache Spark version']
    releases['release_date'] = pd.to_datetime(releases['Release date'], format='%b %d, %Y')
    releases['end_of_support_date'] = pd.to_datetime(releases['End-of-support date'], format='%b %d, %Y')
    releases['version'] = releases['Version'].transform(lambda v: v.split()[0])
    releases['is_lts'] = releases['Version'].transform(lambda v: v.upper().endswith('LTS'))
    releases['is_ml'] = pd.Series([[True, False]] * size)  # TODO: think of a better way
    releases_exploded_tmp = releases.explode('is_ml')
    releases_exploded_tmp['is_gpu_accelerated'] = releases_exploded_tmp['is_ml'].apply(
        lambda is_ml: [True, False] if is_ml else None)  # TODO: think of a better way
    releases_exploded = releases_exploded_tmp.explode('is_gpu_accelerated')

    def build_relative_path(version, is_lts, is_ml, is_gpu_accelerated):
        if is_ml:
            path = f'runtime-bom-{cloud}-{version}{"-lts" if is_lts else ""}' + f'/runtime-bom-{cloud}-' + version
        else:
            path = f'runtime-bom-{cloud}-{version}'
        if is_lts:
            path += '-lts'
        if is_ml and is_gpu_accelerated:
            path += '-ml-gpu'
        elif is_ml and not is_gpu_accelerated:
            path += '-ml-cpu'
        return path

    def build_url(version, is_lts, is_ml):
        if is_ml and is_lts:
            suffix = 'lts-ml'
        elif is_ml and not is_lts:
            suffix = 'ml'
        elif not is_ml and is_lts:
            suffix = 'lts'
        else:
            suffix = ''
        url = f'{BASE_PATH[cloud]}{version}{suffix}{CLOUD_URL_SUFFIX[cloud]}'
        return url

    releases_exploded['relative_path'] = releases_exploded.apply(lambda r: build_relative_path(
        r['version'],
        r['is_lts'],
        r['is_ml'],
        r['is_gpu_accelerated']
    ), axis=1)
    releases_exploded['url'] = releases_exploded.apply(lambda r: build_url(
        r['version'],
        r['is_lts'],
        r['is_ml']
    ), axis=1)

    def extract_version(url, xpath):
        arr = extract_from_content2(load_content(url), xpath)
        if len(arr) > 0:
            return arr[0].strip(': ')
        else:
            return None

    releases_exploded['scala_version'] = releases_exploded.apply(
        lambda r: extract_version(r['url'], SCALA_VERSION_XPATH[cloud]), axis=1)
    releases_exploded['delta_lake_version'] = releases_exploded.apply(
        lambda r: extract_version(r['url'], DELTA_LAKE_VERSION_XPATH[cloud]), axis=1)
    releases_exploded['scala_version'] = releases_exploded.groupby('version')['scala_version'].transform(
        lambda g: g.ffill().bfill())
    releases_exploded['delta_lake_version'] = releases_exploded.groupby('version')['delta_lake_version'].transform(
        lambda g: g.ffill().bfill())
    releases_exploded[
        ['version', 'is_lts', 'is_ml', 'is_gpu_accelerated', 'spark_version', 'scala_version', 'delta_lake_version',
         'release_date', 'end_of_support_date',
         'relative_path', 'url']].sort_values(
        by=['release_date', 'is_lts', 'is_ml', 'is_gpu_accelerated']).to_parquet(
        f'{OUTPUT_DIR}/{RELEASES_OUTPUT_FILE_NAME[cloud]}', index=False)


def scrape_installed_libraries(cloud):
    releases_exploded = pd.read_parquet(f'{OUTPUT_DIR}/{RELEASES_OUTPUT_FILE_NAME[cloud]}')
    poms_configurations = releases_exploded[
        ['version', 'is_lts', 'is_ml', 'is_gpu_accelerated', 'spark_version', 'url']]

    installed_libraries = []

    for index, pc in poms_configurations.iterrows():
        url = pc['url']
        print('Current configuration version: ', pc['version'], 'is_ml', pc['is_ml'])
        if not pc['is_ml']:
            table = load_table(url, INSTALLED_JAVA_SCALA_LIBS_XPATH[cloud])
        else:
            if pc['is_gpu_accelerated']:
                table = load_table(url, INSTALLED_JAVA_SCALA_LIBS_ML_GPU_XPATH[cloud])
            else:
                table = load_table(url, INSTALLED_JAVA_SCALA_LIBS_ML_CPU_XPATH[cloud])
        table_renamed = table.rename(columns={
            'Group ID': 'group_id',
            'Artifact ID': 'artifact_id',
            'Version': 'artifact_version'})
        table_renamed[[
            'version',
            'is_lts',
            'is_ml',
            'is_gpu_accelerated'
        ]] = pc.loc[[
            'version',
            'is_lts',
            'is_ml',
            'is_gpu_accelerated'
        ]].values  # TODO: think of a better way
        installed_libraries.append(table_renamed)

    installed_libraries = pd.concat(installed_libraries, ignore_index=True)

    installed_libraries[
        ['version', 'is_lts', 'is_ml', 'is_gpu_accelerated', 'group_id', 'artifact_id',
         'artifact_version']].sort_values(
        by=['version', 'is_lts', 'is_ml', 'is_gpu_accelerated', 'group_id', 'artifact_id']).to_parquet(
        f'{OUTPUT_DIR}/{INSTALLED_LIBRARIES_OUTPUT_FILE_NAME[cloud]}', index=False)


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for cloud in [AWS_CLOUD_NAME, AZURE_CLOUD_NAME, GCP_CLOUD_NAME]:
        scrape_releases(cloud)
        scrape_installed_libraries(cloud)
