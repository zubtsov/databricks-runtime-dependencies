mvn validate -e

mvn dependency:resolve -P add-all-dependencies
mvn dependency:resolve -P windows-x86_64
mvn dependency:resolve -P linux-x86_64
mvn dependency:resolve -P osx-x86_64
mvn dependency:resolve -P linux-aarch_64
mvn dependency:resolve -P osx-aarch_64