Name: org.osgi.dto
Version: 1.1.0
Release: 1
Group: Development/Java
Summary: An implementation of the org.osgi.dto API
Source0: https://repo1.maven.org/maven2/org/osgi/org.osgi.dto/%{version}/org.osgi.dto-%{version}-sources.jar
Source1: https://repo1.maven.org/maven2/org/osgi/org.osgi.dto/%{version}/org.osgi.dto-%{version}.pom
License: BSD
BuildRequires: jdk-current
BuildRequires: javapackages-local
BuildArch: noarch
BuildRequires: jmod(org.osgi.annotation.versioning)

%description
OSGi Companion Code for org.osgi.dto

%package javadoc
Summary: Javadoc documentation for org.osgi.dto
Group: Development/Java

%description javadoc
Javadoc documentation for org.osgi.dto

%prep
%autosetup -p1 -c %{name}-%{version}

%build
. %{_sysconfdir}/profile.d/90java.sh
export PATH=$JAVA_HOME/bin:$PATH

cat >module-info.java <<'EOF'
module org.osgi.dto {
	exports org.osgi.dto;
	requires org.osgi.annotation.versioning;
}
EOF
find . -name "*.java" |xargs javac -p %{_javadir}/modules
find . -name "*.class" -o -name "*.properties" |xargs jar cf org.osgi.dto-%{version}.jar META-INF
# OSGi must be using a different version of javadoc...
sed -i -e 's,@NotThreadSafe,,' org/osgi/dto/DTO.java
javadoc -p %{_javadir}/modules -d docs -sourcepath . org.osgi.dto
cp %{S:1} .

%install
mkdir -p %{buildroot}%{_javadir}/modules %{buildroot}%{_mavenpomdir} %{buildroot}%{_javadocdir}
cp org.osgi.dto-%{version}.jar %{buildroot}%{_javadir}
cp *.pom %{buildroot}%{_mavenpomdir}/
%add_maven_depmap org.osgi.dto-%{version}.pom org.osgi.dto-%{version}.jar
cp -a docs %{buildroot}%{_javadocdir}/%{name}
mv %{buildroot}%{_javadir}/*.jar %{buildroot}%{_javadir}/modules/
ln -s modules/org.osgi.dto-%{version}.jar %{buildroot}%{_javadir}
ln -s modules/org.osgi.dto-%{version}.jar %{buildroot}%{_javadir}/org.osgi.dto.jar

%files -f .mfiles
%{_javadir}/*.jar
%{_javadir}/modules/*.jar

%files javadoc
%{_javadocdir}/%{name}
