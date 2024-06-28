import json
import os
from constants import *

from jinja2 import Environment, FileSystemLoader

POM_FILE_NAME = 'pom.xml'
ROOT_POM_TEMPLATE_NAME = 'root_pom.xml.jinja'
REGULAR_POM_TEMPLATE_NAME = 'pom.xml.jinja'

TEMPLATES_FOLDER = os.path.join(os.path.pardir, 'templates')
SCRAPED_FOLDER = os.path.join(os.path.pardir, os.path.pardir, '.scraped')
OUTPUT_FOLDER = os.path.join(os.path.pardir, os.path.pardir)


def render_root_pom(runtimes_info, jinja_env):
    modules_names_list = list(
        [
            f'{ARTIFACT_NAME_PREFIX}-{ri["cloud_name"]}-{ri["runtime_version"]}{LTS_ARTIFACT_ID_SUFFIX if ri["is_lts"] else ""}'
            for ri in runtimes_info if ri['is_gpu_accelerated'] is None
        ])

    modules_names_list.sort(key=lambda mn: (mn.split('-')[2], float(mn.split('-')[3])))

    context = {
        "modules": modules_names_list,
        **COMMON_JINJA_CONTEXT
    }

    template = jinja_env.get_template(ROOT_POM_TEMPLATE_NAME)
    rendered_root_pom = template.render(context)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    with open(os.path.join(OUTPUT_FOLDER, POM_FILE_NAME), 'w') as root_pom_file:
        root_pom_file.write(rendered_root_pom)


def render_pom(rel_info, scala_vers_map, jinja_env):
    pom_relative_path = build_relative_path(runtime_info['cloud_name'], runtime_info['runtime_version'],
                                            runtime_info['is_lts'], runtime_info['is_ml'],
                                            runtime_info['is_gpu_accelerated'])
    pom_path = os.path.join(OUTPUT_FOLDER,
                            pom_relative_path)
    os.makedirs(pom_path, exist_ok=True)

    template = jinja_env.get_template(REGULAR_POM_TEMPLATE_NAME)

    extra_context = build_extra_context(rel_info, scala_vers_map)

    context = {**COMMON_JINJA_CONTEXT, **rel_info, **extra_context}
    rendered_root_pom = template.render(context)
    os.makedirs(pom_path, exist_ok=True)

    with open(os.path.join(pom_path, POM_FILE_NAME), 'w') as pom_file:
        pom_file.write(rendered_root_pom)


def build_extra_context(rel_info, scala_vers_map):
    rel_scala_version = scala_vers_map[(rel_info['cloud_name'], rel_info['runtime_version'])]
    scala_major_version = '.'.join(rel_scala_version.split('.')[:2])
    scala_minor_version = rel_scala_version.split('.')[2]

    extra_context = {
        "artifact_id": build_artifact_id(rel_info['cloud_name'], runtime_info['runtime_version'],
                                         runtime_info['is_lts'], runtime_info['is_ml'],
                                         runtime_info['is_gpu_accelerated'])
    }
    if not rel_info['is_ml']:
        extra_context['scala_major_version'] = scala_major_version
        extra_context['scala_minor_version'] = scala_minor_version
        extra_context['parent_artifact_id'] = ROOT_ARTIFACT_ID
    else:
        extra_context['parent_artifact_id'] = build_artifact_id(rel_info['cloud_name'], runtime_info['runtime_version'],
                                                                runtime_info['is_lts'], False, None)

    platform_independent_libraries = []
    profiles = {
        WINDOWS_X86_64_INDICATOR: {
            "activation": {
                'family': WINDOWS_OS_FAMILY.capitalize(),
                'arch': X86_64_ARCHITECTURE_MAVEN_NAME
            },
            "libraries": []
        },
        LINUX_X86_64_INDICATOR: {
            "activation": {
                'family': UNIX_OS_FAMILY,
                'name': LINUX_OS_NAME.capitalize(),
                'arch': X86_64_ARCHITECTURE_MAVEN_NAME
            },
            "libraries": []
        },
        MAC_OS_X86_64_INDICATOR: {
            "activation": {
                'family': MAC_OS_FAMILY,
                'arch': X86_64_ARCHITECTURE_MAVEN_NAME
            },
            "libraries": []
        },
        LINUX_ARM_INDICATOR: {
            "activation": {
                'family': UNIX_OS_FAMILY,
                'name': LINUX_OS_NAME.capitalize(),
                'arch': ARM_ARCHITECTURE_MAVEN_NAME
            },
            "libraries": []
        },
        MAC_OS_ARM_INDICATOR: {
            "activation": {
                'family': MAC_OS_FAMILY,
                'arch': ARM_ARCHITECTURE_MAVEN_NAME
            },
            "libraries": []
        }
    }

    for ri_lib in rel_info['installed_libraries']:
        if ri_lib['group_id'] == 'com.github.fommil.netlib' and \
                ri_lib['artifact_id'] in {'native_ref-java', 'native_system-java'} and \
                ri_lib['artifact_version'].endswith('-natives'):
            continue  # these dependencies are removed because of the version conflict: with and without -natives

        # TODO: replace only suffix
        ri_lib['artifact_id'] = ri_lib['artifact_id'].replace(f'_{scala_major_version}',
                                                              '_${scala.major.version}')
        if 'org.scala-lang' in ri_lib['group_id'] and rel_scala_version == ri_lib['artifact_version']:
            ri_lib['artifact_version'] = '${scala.version}'

        if WINDOWS_X86_64_INDICATOR in ri_lib['artifact_id'] or WINDOWS_X86_64_INDICATOR in ri_lib['artifact_version']:
            profiles[WINDOWS_X86_64_INDICATOR]['libraries'].append(ri_lib)
        elif LINUX_X86_64_INDICATOR in ri_lib['artifact_id'] or LINUX_X86_64_INDICATOR in ri_lib['artifact_version']:
            profiles[LINUX_X86_64_INDICATOR]['libraries'].append(ri_lib)
        elif MAC_OS_X86_64_INDICATOR in ri_lib['artifact_id'] or MAC_OS_X86_64_INDICATOR in ri_lib['artifact_version']:
            profiles[MAC_OS_X86_64_INDICATOR]['libraries'].append(ri_lib)
        elif LINUX_ARM_INDICATOR in ri_lib['artifact_id'] or LINUX_ARM_INDICATOR in ri_lib['artifact_version']:
            profiles[LINUX_ARM_INDICATOR]['libraries'].append(ri_lib)
        elif MAC_OS_ARM_INDICATOR in ri_lib['artifact_id'] or MAC_OS_ARM_INDICATOR in ri_lib['artifact_version']:
            profiles[MAC_OS_ARM_INDICATOR]['libraries'].append(ri_lib)
        else:
            platform_independent_libraries.append(ri_lib)

    extra_context['platform_independent_libraries'] = platform_independent_libraries
    extra_context['profiles'] = profiles

    if not rel_info['is_ml']:
        extra_context['modules'] = [
            build_artifact_id(rel_info['cloud_name'], rel_info['runtime_version'], rel_info['is_lts'], True, is_gpu)
            for is_gpu in [False, True]
        ]

    return extra_context


def build_artifact_id(cloud_name, runtime_version, is_lts, is_ml, is_gpu_accelerated):
    artifact_id_text = f'{ARTIFACT_NAME_PREFIX}-{cloud_name}-{runtime_version}'
    if is_lts:
        artifact_id_text += LTS_ARTIFACT_ID_SUFFIX
    if is_ml:
        artifact_id_text += ML_ARTIFACT_ID_SUFFIX
        if is_gpu_accelerated:
            artifact_id_text += GPU_ARTIFACT_ID_SUFFIX
        else:
            artifact_id_text += CPU_ARTIFACT_ID_SUFFIX
    return artifact_id_text


def build_relative_path(cloud_name, runtime_version, is_lts, is_ml, is_gpu_accelerated):
    artifact_id = build_artifact_id(cloud_name, runtime_version, is_lts, is_ml, is_gpu_accelerated)

    if is_ml:
        return os.path.join(
            f'{ARTIFACT_NAME_PREFIX}-{cloud_name}-{runtime_version}{LTS_ARTIFACT_ID_SUFFIX if is_lts else ""}',
            artifact_id
        )
    else:
        return artifact_id


def set_cloud_name_for_each_release(rel_info, c_name):
    for i in range(len(rel_info)):
        runtime_info[i]['cloud_name'] = c_name


def get_scala_versions(run_info):
    return dict([((ri['cloud_name'], ri['runtime_version']), ri['scala_version'])
                 for ri in run_info if 'scala_version' in ri])


if __name__ == '__main__':
    runtimes_info = []
    for cloud_name in [AWS_CLOUD_NAME, AZURE_CLOUD_NAME, GCP_CLOUD_NAME]:
        with open(os.path.join(SCRAPED_FOLDER, f'{cloud_name}_runtimes_info.json'), 'r') as f:
            runtime_info = json.load(f)
            set_cloud_name_for_each_release(runtime_info, cloud_name)
            runtimes_info += runtime_info

    scala_versions = get_scala_versions(runtimes_info)

    file_loader = FileSystemLoader(TEMPLATES_FOLDER)
    jinja_environment = Environment(loader=file_loader)

    render_root_pom(runtimes_info, jinja_environment)
    for runtime_info in runtimes_info:
        render_pom(runtime_info, scala_versions, jinja_environment)
