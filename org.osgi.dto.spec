Name:		org.osgi.dto
Version:	1.1.1
Release:	1
Summary:	OSGi Data Transfer Object API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.dto/%{version}/org.osgi.dto-%{version}-sources.jar
# The sources jar does not ship a license file. The headers are Apache-2.0.
Source1:	org.osgi.dto-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi DTO 1.1.1. DTO.toString prints public fields for debugging, and
strings longer than 100 characters are compressed. The package version
annotation is 1.1.1. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

root = Path("src/main/java/org/osgi/dto")
names = sorted(path.name for path in root.glob("*.java"))
if names != ["DTO.java", "package-info.java"]:
    raise SystemExit("java files " + " ".join(names))
text = (root / "package-info.java").read_text(encoding="utf-8")
if '@Version("1.1.1")' not in text:
    raise SystemExit("package version annotation")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.dto</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.dto</name>
  <description>OSGi Data Transfer Object 1.1.1.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.dto</artifactId>",
    "<artifactId>osgi.annotation</artifactId>",
    "<version>8.1.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in (
    "junit",
    "SNAPSHOT",
    "<source>",
    "<target>",
    "<parent>",
    "felix",
    "maven-bundle-plugin",
    "osgi.framework",
):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.dto-%{version}.jar --describe-module org.osgi.dto > module-describe.txt
grep -q '^org.osgi.dto' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
JAR=%{buildroot}%{_javadir}/org.osgi.dto.jar
test -s "$JAR"
javap -v -classpath "$JAR" org.osgi.dto.DTO | grep -F -q 'major version: 52'
mkdir -p check
cat > check/Smoke.java << 'EOF'
import org.osgi.dto.DTO;

public class Smoke extends DTO {
    public String name = "dto";
    public int value = 2;

    public static void main(String[] args) {
        String text = new Smoke().toString();
        if (!text.contains("\"name\"") || !text.contains("\"dto\"") || !text.contains("\"value\"")) {
            throw new AssertionError(text);
        }
        System.out.println("dto_ok " + text);
    }
}
EOF
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none -cp "$JAR" -d check check/Smoke.java
java -cp "check:$JAR" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'dto_ok' check/out.txt

%files -f .mfiles
%doc LICENSE
