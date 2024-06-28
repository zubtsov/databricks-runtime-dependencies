# Usage: .\scrape.ps1 > log.txt 2>&1

$outputDirectoryPath = "../.scraped"

if (Test-Path -Path $outputDirectoryPath) {
    Remove-Item -Path $outputDirectoryPath -Recurse -Force
}

New-Item -Path $outputDirectoryPath -ItemType Directory

scrapy crawl databricks_runtimes -s CLOUD_NAME='aws' -o $outputDirectoryPath/aws_runtimes_info.json
scrapy crawl databricks_runtimes -s CLOUD_NAME='azure' -o $outputDirectoryPath/azure_runtimes_info.json
scrapy crawl databricks_runtimes -s CLOUD_NAME='gcp' -o $outputDirectoryPath/gcp_runtimes_info.json
