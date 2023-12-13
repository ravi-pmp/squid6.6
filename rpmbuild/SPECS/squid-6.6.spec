Name:           squid
Version:        6.6
Release:        0
Summary:        Squid - Caching proxy for the Web

License:        GPLv2+
URL:            http://www.squid-cache.org/
Source0:        %{name}-%{version}.tar.gz
Source1:        squid.conf
Source2:        squid.service
Source3:        cache_swap.sh

BuildRequires:  openssl-devel, libxml2-devel, libtool-ltdl-devel
Requires:       /sbin/chkconfig, /sbin/service, shadow-utils

%description
Squid is a caching proxy for the Web supporting HTTP, HTTPS, FTP, and more.
It reduces bandwidth and improves response times by caching and reusing
frequently-requested web pages.

%prep
%setup -q

%build
./configure --prefix=/opt/squid --sysconfdir=/opt/squid/etc --localstatedir=/var
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Create necessary directory for custom script
mkdir -p $RPM_BUILD_ROOT/opt/squid/usr/libexec/squid/
mkdir -p $RPM_BUILD_ROOT/opt/squid/var/log
mkdir -p $RPM_BUILD_ROOT/opt/squid/var/cache/squid
mkdir -p $RPM_BUILD_ROOT/opt/squid/var/run

# Installing custom configuration and service files
install -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT/opt/squid/etc/squid.conf
install -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/squid.service

# Installing the cache_swap.sh script with executable permissions
install -D -m 755 %{SOURCE3} $RPM_BUILD_ROOT/opt/squid/usr/libexec/squid/cache_swap.sh

%pre
getent group dd-squid >/dev/null || groupadd -r dd-squid
getent passwd dd-squid >/dev/null || \
useradd -r -g dd-squid -d /opt/squid -s /sbin/nologin -c "Squid Proxy Server" dd-squid
exit 0

%post
/usr/bin/chown -R dd-squid:dd-squid /opt/squid
semanage fcontext -a -t squid_log_t '/opt/squid/var/log/(/.*)?'  
semanage fcontext -a -t squid_var_run_t '/opt/squid/var/run/squid' 
semanage fcontext -a -t squid_var_run_t '/opt/squid/var/run(/.*)?' 
semanage fcontext -a -t squid_var_run_t '/opt/squid/var/run/squid.*'  
semanage fcontext -a -t squid_cache_t  '/opt/squid/var/cache/squid(/.*)?'
semanage fcontext -a -t squid_exec_t '/opt/squid/sbin/squid'
semanage fcontext -a -t squid_cache_t '/opt/squid/var/cache/squid(/.*)?'
semanage fcontext -a -t squid_conf_t '/opt/squid/etc(/.*)?'
setsebool -P squid_connect_any 0
restorecon -Rv /opt/squid
systemctl daemon-reload
systemctl enable squid.service


%preun
if [ $1 -eq 0 ] ; then
    systemctl --no-reload disable squid.service
fi

%postun
systemctl daemon-reload

%files
%defattr(-,root,root,-)
/opt/squid
%config(noreplace) /opt/squid/etc/squid.conf
%{_unitdir}/squid.service
/opt/squid/usr/libexec/squid/cache_swap.sh

%changelog
* Mon Dec 11 2023 Ravi ravi@opensource.com.sg - 6.6
- Initial package.

