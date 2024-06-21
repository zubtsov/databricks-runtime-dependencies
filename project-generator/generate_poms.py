import os
import pandas as pd
from xml.etree import ElementTree as ET

AWS_CLOUD_NAME = 'aws'
AZURE_CLOUD_NAME = 'azure'
GCP_CLOUD_NAME = 'gcp'

INPUT_DIR = 'scraped'
OUTPUT_DIR = '..'
RELEASES_DATASET_FILE_NAME = {
    AWS_CLOUD_NAME: f'releases-{AWS_CLOUD_NAME}.parquet',
    AZURE_CLOUD_NAME: f'releases-{AZURE_CLOUD_NAME}.parquet',
    GCP_CLOUD_NAME: f'releases-{GCP_CLOUD_NAME}.parquet'
}
INSTALLED_LIBRARIES_DATASET_FILE_NAME = {
    AWS_CLOUD_NAME: f'installed_libraries-{AWS_CLOUD_NAME}.parquet',
    AZURE_CLOUD_NAME: f'installed_libraries-{AZURE_CLOUD_NAME}.parquet',
    GCP_CLOUD_NAME: f'installed_libraries-{GCP_CLOUD_NAME}.parquet'
}

PROJECT_AUTHOR = 'Ruslan Zubtsov'
PROJECT_AUTHOR_EMAIL = 'zubtsov.r@gmail.com'
PROJECT_AUTHOR_GITHUB = 'https://github.com/zubtsov/'
PROJECT_AUTHOR_LINKEDIN = 'https://www.linkedin.com/in/zubtsov/'
PROJECT_SCM_CONNECTION = 'scm:git:git://github.com:zubtsov/databricks-runtime-dependencies.git'
PROJECT_SCM_DEVELOPER_CONNECTION = 'scm:git:ssh://github.com:zubtsov/databricks-runtime-dependencies.git'

PROJECT_INCEPTION_YEAR = '2024'

PROJECT_GROUP_ID = 'io.github.zubtsov.databricks'
PROJECT_VERSION = '0.0.2'

PROJECT_URL = f'{PROJECT_AUTHOR_GITHUB}databricks-runtime-dependencies'

ARTIFACT_PREFIX = 'runtime-bom'
ROOT_ARTIFACT_ID = 'runtime-bom-root'
LTS_ARTIFACT_ID_SUFFIX = '-lts'
ML_ARTIFACT_ID_SUFFIX = '-ml'
GPU_ARTIFACT_ID_SUFFIX = '-gpu'
CPU_ARTIFACT_ID_SUFFIX = '-cpu'

GROUP_ID_TAG = 'groupId'
ARTIFACT_ID_TAG = 'artifactId'
ARTIFACT_VERSION_TAG = 'version'

WINDOWS_OS_FAMILY = 'windows'
MAC_OS_FAMILY = 'mac'
UNIX_OS_FAMILY = 'unix'

X86_64_ARCHITECTURE_MAVEN_NAME = 'x86_64'
ARM_ARCHITECTURE_MAVEN_NAME = 'aarch64'

LINUX_OS_NAME = 'linux'
MAC_OS_NAME = 'osx'
WINDOWS_OS_NAME = 'windows'

WINDOWS_X86_64_INDICATOR = f'{WINDOWS_OS_NAME}-x86_64'
LINUX_X86_64_INDICATOR = f'{LINUX_OS_NAME}-x86_64'
MAC_OS_X86_64_INDICATOR = f'{MAC_OS_NAME}-x86_64'
LINUX_ARM_INDICATOR = f'{LINUX_OS_NAME}-aarch_64'
MAC_OS_ARM_INDICATOR = f'{MAC_OS_NAME}-aarch_64'

ROOT_POM_DESCRIPTION = 'This project (BOM) is intended to ease dependency management for projects running on Databricks.'
PROJECT_NAME_PATTERN = '${project.groupId}:${project.artifactId}'


def build_pom_skeleton():
    namespaces = {
        'xmlns': "http://maven.apache.org/POM/4.0.0",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"
    }
    root = ET.Element("project", attrib=namespaces)
    model_version = ET.SubElement(root, "modelVersion")
    model_version.text = "4.0.0"

    license = ET.SubElement(ET.SubElement(root, 'licenses'), 'license')
    ET.SubElement(license, 'name').text = 'The MIT License'
    ET.SubElement(license, 'url').text = 'https://opensource.org/licenses/MIT'

    return root


def build_artifact_id(cloud, ver, is_lts, is_ml, is_gpu_accelerated):
    artifact_id_text = f'{ARTIFACT_PREFIX}-{cloud}-{ver}'
    if is_lts:
        artifact_id_text += LTS_ARTIFACT_ID_SUFFIX
    if is_ml:
        artifact_id_text += ML_ARTIFACT_ID_SUFFIX
        if is_gpu_accelerated:
            artifact_id_text += GPU_ARTIFACT_ID_SUFFIX
        else:
            artifact_id_text += CPU_ARTIFACT_ID_SUFFIX
    return artifact_id_text


def build_pom_parent_section(cloud, release, root):
    parent = ET.SubElement(root, "parent")
    group_id = ET.SubElement(parent, GROUP_ID_TAG)
    group_id.text = PROJECT_GROUP_ID
    parent_artifact_id = ET.SubElement(parent, ARTIFACT_ID_TAG)
    if not release.is_ml:
        parent_artifact_id.text = ROOT_ARTIFACT_ID
    else:
        parent_artifact_id.text = build_artifact_id(cloud, release.version, release.is_lts, False, False)
    ET.SubElement(parent, ARTIFACT_VERSION_TAG).text = PROJECT_VERSION
    return parent


def build_pom_modules_section(root, artifact_id_text):
    modules = ET.SubElement(root, "modules")
    module1 = ET.SubElement(modules, "module")
    module1.text = f"{artifact_id_text}{ML_ARTIFACT_ID_SUFFIX}{CPU_ARTIFACT_ID_SUFFIX}"
    module2 = ET.SubElement(modules, "module")
    module2.text = f"{artifact_id_text}{ML_ARTIFACT_ID_SUFFIX}{GPU_ARTIFACT_ID_SUFFIX}"


def build_pom_properties_section(release, root):
    properties = ET.SubElement(root, "properties")
    scala_major_version = ET.SubElement(properties, "scala.major.version")
    scala_major_version_text = ".".join(release.scala_version.split(".")[:2])
    scala_major_version.text = scala_major_version_text
    scala_minor_version = ET.SubElement(properties, "scala.minor.version")
    scala_minor_version_text = release.scala_version.split(".")[-1]
    scala_minor_version.text = scala_minor_version_text
    scala_version = ET.SubElement(properties, "scala.version")
    scala_version.text = "${scala.major.version}.${scala.minor.version}"
    delta_lake_version = ET.SubElement(properties, "delta.lake.version")
    delta_lake_version.text = release.delta_lake_version
    spark_version = ET.SubElement(properties, "spark.version")
    spark_version.text = release.spark_version
    return scala_major_version_text


def add_pom_dependency(dependencies_elem, group_id, artifact_id, artifact_version, artifact_type=None,
                       artifact_scope='provided'):
    dependency = ET.SubElement(dependencies_elem, 'dependency')
    ET.SubElement(dependency, GROUP_ID_TAG).text = group_id
    ET.SubElement(dependency, ARTIFACT_ID_TAG).text = artifact_id
    ET.SubElement(dependency, ARTIFACT_VERSION_TAG).text = artifact_version

    if artifact_type is not None:
        ET.SubElement(dependency, 'type').text = artifact_type
    ET.SubElement(dependency, 'scope').text = artifact_scope


def add_developer_info(root):
    developer = ET.SubElement(ET.SubElement(root, 'developers'), 'developer')
    ET.SubElement(developer, 'id').text = PROJECT_AUTHOR_LINKEDIN
    ET.SubElement(developer, 'name').text = PROJECT_AUTHOR
    ET.SubElement(developer, 'email').text = PROJECT_AUTHOR_EMAIL
    ET.SubElement(developer, 'organization').text = PROJECT_AUTHOR
    ET.SubElement(developer, 'organizationUrl').text = PROJECT_AUTHOR_GITHUB


def add_scm_info(root):
    scm = ET.SubElement(root, 'scm')
    ET.SubElement(scm, 'connection').text = PROJECT_SCM_CONNECTION
    ET.SubElement(scm, 'developerConnection').text = PROJECT_SCM_DEVELOPER_CONNECTION
    ET.SubElement(scm, 'url').text = PROJECT_URL + '/tree/main'


# we can't depend on the previous runtime version with the 'import' scope
# because some dependencies might be missing in the newer version.
def build_pom(cloud, release, installed_libs):
    root = build_pom_skeleton()

    ET.SubElement(root, 'name').text = PROJECT_NAME_PATTERN
    ET.SubElement(root, 'description').text = 'Dependency management for ' + release.url
    ET.SubElement(root, 'url').text = PROJECT_URL

    add_developer_info(root)
    add_scm_info(root)
    build_pom_parent_section(cloud, release, root)

    root.append(ET.Comment('Source: ' + release.url))
    artifact_id = ET.SubElement(root, ARTIFACT_ID_TAG)
    artifact_id.text = build_artifact_id(
        cloud, release.version, release.is_lts, release.is_ml, release.is_gpu_accelerated
    )
    packaging = ET.SubElement(root, "packaging")
    packaging.text = "pom"

    if not release.is_ml:
        build_pom_modules_section(root, artifact_id.text)

    scala_major_version_text = build_pom_properties_section(release, root)

    profiles = ET.SubElement(root, 'profiles')

    windows_x86_64_profile = ET.SubElement(profiles, 'profile')
    ET.SubElement(windows_x86_64_profile, 'id').text = WINDOWS_X86_64_INDICATOR
    os = ET.SubElement(ET.SubElement(windows_x86_64_profile, 'activation'), 'os')
    ET.SubElement(os, 'family').text = WINDOWS_OS_FAMILY.capitalize()
    ET.SubElement(os, 'arch').text = X86_64_ARCHITECTURE_MAVEN_NAME

    windows_x86_64_profile_deps = ET.SubElement(ET.SubElement(windows_x86_64_profile, 'dependencyManagement'),
                                                'dependencies')

    linux_x86_64_profile = ET.SubElement(profiles, 'profile')
    ET.SubElement(linux_x86_64_profile, 'id').text = LINUX_X86_64_INDICATOR
    os = ET.SubElement(ET.SubElement(linux_x86_64_profile, 'activation'), 'os')
    ET.SubElement(os, 'family').text = UNIX_OS_FAMILY

    ET.SubElement(os, 'name').text = LINUX_OS_NAME.capitalize()
    ET.SubElement(os, 'arch').text = X86_64_ARCHITECTURE_MAVEN_NAME
    linux_x86_64_profile_deps = ET.SubElement(ET.SubElement(linux_x86_64_profile, 'dependencyManagement'),
                                              'dependencies')

    osx_x86_64_profile = ET.SubElement(profiles, 'profile')
    ET.SubElement(osx_x86_64_profile, 'id').text = MAC_OS_X86_64_INDICATOR
    os = ET.SubElement(ET.SubElement(osx_x86_64_profile, 'activation'), 'os')
    ET.SubElement(os, 'family').text = MAC_OS_FAMILY
    ET.SubElement(os, 'arch').text = X86_64_ARCHITECTURE_MAVEN_NAME
    osx_x86_64_profile_deps = ET.SubElement(ET.SubElement(osx_x86_64_profile, 'dependencyManagement'), 'dependencies')

    linux_aarch_64_profile = ET.SubElement(profiles, 'profile')
    ET.SubElement(linux_aarch_64_profile, 'id').text = LINUX_ARM_INDICATOR
    os = ET.SubElement(ET.SubElement(linux_aarch_64_profile, 'activation'), 'os')
    ET.SubElement(os, 'family').text = UNIX_OS_FAMILY
    ET.SubElement(os, 'name').text = LINUX_OS_NAME.capitalize()
    ET.SubElement(os, 'arch').text = 'aarch64'
    linux_aarch_64_profile_deps = ET.SubElement(ET.SubElement(linux_aarch_64_profile, 'dependencyManagement'),
                                                'dependencies')

    osx_aarch_64_profile = ET.SubElement(profiles, 'profile')
    ET.SubElement(osx_aarch_64_profile, 'id').text = MAC_OS_ARM_INDICATOR
    os = ET.SubElement(ET.SubElement(osx_aarch_64_profile, 'activation'), 'os')
    ET.SubElement(os, 'family').text = MAC_OS_FAMILY
    ET.SubElement(os, 'arch').text = ARM_ARCHITECTURE_MAVEN_NAME
    osx_aarch_64_profile_deps = ET.SubElement(ET.SubElement(osx_aarch_64_profile, 'dependencyManagement'),
                                              'dependencies')

    dependencies = ET.SubElement(ET.SubElement(root, 'dependencyManagement'), 'dependencies')
    if release.is_ml:
        library_artifact_id = f'{ARTIFACT_PREFIX}-{cloud}-{release.version}{LTS_ARTIFACT_ID_SUFFIX if release.is_lts else ""}'
        add_pom_dependency(dependencies, PROJECT_GROUP_ID, library_artifact_id, PROJECT_VERSION, 'pom', 'import')

    for ind, library in installed_libs.sort_values(by=['group_id', 'artifact_id']).iterrows():
        if library.group_id == 'com.github.fommil.netlib' and \
                library.artifact_id in {'native_ref-java', 'native_system-java'} and \
                library.artifact_version.endswith('-natives'):
            continue  # these dependencies are removed because of the version conflict: with and without -natives

        library_artifact_id = library.artifact_id.replace(f'_{scala_major_version_text}', '_${scala.major.version}')
        if 'org.scala-lang' in library.group_id and release.scala_version == library.artifact_version:
            artifact_version = '${scala.version}'
        else:
            artifact_version = library.artifact_version

        if WINDOWS_X86_64_INDICATOR in library_artifact_id or WINDOWS_X86_64_INDICATOR in artifact_version:
            add_pom_dependency(windows_x86_64_profile_deps, library.group_id, library_artifact_id, artifact_version)
        elif LINUX_X86_64_INDICATOR in library_artifact_id or LINUX_X86_64_INDICATOR in artifact_version:
            add_pom_dependency(linux_x86_64_profile_deps, library.group_id, library_artifact_id, artifact_version)
        elif MAC_OS_X86_64_INDICATOR in library_artifact_id or MAC_OS_X86_64_INDICATOR in artifact_version:
            add_pom_dependency(osx_x86_64_profile_deps, library.group_id, library_artifact_id, artifact_version)
        elif LINUX_ARM_INDICATOR in library_artifact_id or LINUX_ARM_INDICATOR in artifact_version:
            add_pom_dependency(linux_aarch_64_profile_deps, library.group_id, library_artifact_id, artifact_version)
        elif MAC_OS_ARM_INDICATOR in library_artifact_id or MAC_OS_ARM_INDICATOR in artifact_version:
            add_pom_dependency(osx_aarch_64_profile_deps, library.group_id, library_artifact_id, artifact_version)
        else:
            add_pom_dependency(dependencies, library.group_id, library_artifact_id, artifact_version)

    return ET.ElementTree(root)


def add_distribution_configuration(root):
    sr = ET.SubElement(ET.SubElement(root, 'distributionManagement'), 'snapshotRepository')
    ET.SubElement(sr, 'id').text = 'ossrh'
    ET.SubElement(sr, 'url').text = 'https://s01.oss.sonatype.org/content/repositories/snapshots/'
    plugins = ET.SubElement(ET.SubElement(root, 'build'), 'plugins')

    pl = ET.SubElement(plugins, 'plugin')
    ET.SubElement(pl, 'groupId').text = 'org.sonatype.central'
    ET.SubElement(pl, 'artifactId').text = 'central-publishing-maven-plugin'
    ET.SubElement(pl, 'version').text = '0.5.0'
    ET.SubElement(pl, 'extensions').text = 'true'
    conf = ET.SubElement(pl, 'configuration')
    ET.SubElement(conf, 'publishingServerId').text = 'central'
    ET.SubElement(conf, 'autoPublish').text = 'false'

    pl = ET.SubElement(plugins, 'plugin')
    ET.SubElement(pl, 'groupId').text = 'org.apache.maven.plugins'
    ET.SubElement(pl, 'artifactId').text = 'maven-gpg-plugin'
    ET.SubElement(pl, 'version').text = '1.5'
    exec = ET.SubElement(ET.SubElement(pl, 'executions'), 'execution')
    ET.SubElement(exec, 'id').text = 'sign-artifacts'
    ET.SubElement(exec, 'phase').text = 'verify'
    ET.SubElement(ET.SubElement(exec, 'goals'), 'goal').text = 'sign'


def build_root_pom(releases):
    root = build_pom_skeleton()

    ET.SubElement(root, 'name').text = PROJECT_NAME_PATTERN
    ET.SubElement(root, 'description').text = ROOT_POM_DESCRIPTION
    ET.SubElement(root, 'url').text = PROJECT_URL

    add_developer_info(root)
    add_scm_info(root)

    ET.SubElement(root, 'inceptionYear').text = PROJECT_INCEPTION_YEAR
    ET.SubElement(root, GROUP_ID_TAG).text = PROJECT_GROUP_ID
    ET.SubElement(root, ARTIFACT_ID_TAG).text = ROOT_ARTIFACT_ID
    ET.SubElement(root, ARTIFACT_VERSION_TAG).text = PROJECT_VERSION
    ET.SubElement(root, "packaging").text = "pom"

    props = ET.SubElement(root, "properties")
    ET.SubElement(props, "project.build.sourceEncoding").text = 'UTF-8'
    ET.SubElement(props, "scala.major.version").text = '0.0'
    ET.SubElement(props, "scala.minor.version").text = '0'
    scala_version = ET.SubElement(props, "scala.version")
    scala_version.text = "${scala.major.version}.${scala.minor.version}"
    ET.SubElement(props, "delta.lake.version").text = '0.0.0'
    ET.SubElement(props, "spark.version").text = '0.0.0'

    modules = ET.SubElement(root, "modules")

    for cloud in [AWS_CLOUD_NAME, AZURE_CLOUD_NAME, GCP_CLOUD_NAME]:
        for index, row in releases[~releases['is_ml']].iterrows():
            ET.SubElement(modules, 'module').text = build_artifact_id(
                cloud, row['version'], row['is_lts'], row['is_ml'], row['is_gpu_accelerated']
            )

    deps = ET.SubElement(ET.SubElement(root, 'dependencyManagement'), 'dependencies')
    add_pom_dependency(deps, 'io.delta', 'delta-core_${scala.major.version}', '${delta.lake.version}')
    add_pom_dependency(deps, 'org.apache.spark', 'spark-core_${scala.major.version}', '${spark.version}')
    add_pom_dependency(deps, 'org.apache.spark', 'spark-sql_${scala.major.version}', '${spark.version}')
    add_pom_dependency(deps, 'org.apache.spark', 'spark-mllib_${scala.major.version}', '${spark.version}')
    add_pom_dependency(deps, 'org.apache.spark', 'spark-streaming_${scala.major.version}', '${spark.version}')
    add_pom_dependency(deps, 'org.apache.spark', 'spark-hive_${scala.major.version}', '${spark.version}')
    add_pom_dependency(deps, 'org.apache.spark', 'spark-avro_${scala.major.version}', '${spark.version}')
    add_pom_dependency(deps, 'org.apache.spark', 'spark-graphx_${scala.major.version}', '${spark.version}')

    add_distribution_configuration(root)

    return ET.ElementTree(root)


os.makedirs(OUTPUT_DIR, exist_ok=True)

for cloud in ['aws', 'azure', 'gcp']:
    releases = pd.read_parquet(f'{INPUT_DIR}/{RELEASES_DATASET_FILE_NAME[cloud]}')
    installed_libraries = pd.read_parquet(f'{INPUT_DIR}/{INSTALLED_LIBRARIES_DATASET_FILE_NAME[cloud]}')
    # FIXME: workaround for a bug
    installed_libraries = installed_libraries[installed_libraries['artifact_id'].notnull()]

    for index, row in releases.iterrows():
        dir = f'{OUTPUT_DIR}/{row["relative_path"]}'
        os.makedirs(dir, exist_ok=True)
        il = installed_libraries[
            (installed_libraries['version'] == row.version) &
            (installed_libraries['is_ml'] == row.is_ml) &
            ((installed_libraries['is_gpu_accelerated'].isnull() & (row.is_gpu_accelerated is None)) | (
                    installed_libraries['is_gpu_accelerated'] == row.is_gpu_accelerated))]

        with open(f'{dir}/pom.xml', 'w') as f:
            tree = build_pom(cloud, row, il)
            ET.indent(tree, space="\t", level=0)
            tree.write(f, encoding='unicode')

    with open(f'{OUTPUT_DIR}/pom.xml', 'w') as f:
        tree = build_root_pom(releases)
        ET.indent(tree, space="\t", level=0)
        tree.write(f, encoding='unicode')
