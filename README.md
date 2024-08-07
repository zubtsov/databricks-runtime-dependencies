# Databricks Runtime Dependencies

## Description

The goal of this project is to simplify dependency management for projects running on Databricks. It documents all
libraries installed on each Databricks runtime (DBR) version, so you can easily reference pre-installed dependencies
without needing to specify their versions. It's easier to use the provided libraries than to replace them with different
versions from those installed on a cluster.

# Usage

## Maven

There are POM files for each Databricks runtime version and configuration. You have two options for using this project
listed below.

### Inheritance

Specify the chosen POM as a parent in your project's POM file. With this option, you'll also inherit
properties such as Apache Spark, Scala, Delta Lake, and other versions information.

Example:

```xml

<project>
    <parent>
        <groupId>io.github.zubtsov.databricks</groupId>
        <artifactId>runtime-bom-aws-14.3-lts</artifactId>
        <version>0.0.4</version>
    </parent>
    ...
</project>
```

### Dependency declaration

Declare the POM file as a dependency with type "POM" and scope "import".

Example:

```xml

<project>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>io.github.zubtsov.databricks</groupId>
                <artifactId>runtime-bom-aws-14.3-lts</artifactId>
                <version>0.0.4</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    ...
</project>
```

All packages can be found [here](https://central.sonatype.com/namespace/io.github.zubtsov.databricks).
Please use artifacts containing the acronym "bom" in their **artifactId**.

## Choosing a proper artifact

**artifactId** has the following format:

```
runtime-bom-<cloud provider>-<runtime version>
```

where

- cloud provider - "aws", "azure" or "gcp"
- runtime version - version of your Databricks runtime

Please select the latest version.

[Packages in Maven central](https://central.sonatype.com/namespace/io.github.zubtsov.databricks)

[Script for POMs and dependencies validation](validate_poms.ps1)