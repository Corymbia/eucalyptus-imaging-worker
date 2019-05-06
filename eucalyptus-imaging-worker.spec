%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

Name:           eucalyptus-imaging-worker
Version:        0.2.2
Release:        1%{?build_id:.%build_id}%{?dist}
Summary:        Configuration tool for the Eucalyptus Imaging Service

Group:          Applications/System
License:        GPLv3
URL:            http://www.eucalyptus.com
Source0:        %{tarball_basedir}.tar.xz

BuildArch:      noarch

BuildRequires:  python%{?__python_ver}-devel
BuildRequires:  python%{?__python_ver}-setuptools

Requires:       eucalyptus-imaging-toolkit
Requires:       python%{?__python_ver}
Requires:       python%{?__python_ver}-boto
Requires:       python%{?__python_ver}-httplib2
Requires:       python-requests
Requires:       python-m2ext
Requires:       python-defusedxml
Requires:       sudo
Requires:       ntp
Requires:       ntpdate
Requires:       qemu-img
Requires(pre):  %{_sbindir}/useradd
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts

%description
Configuration tool for the Eucalyptus Imaging Service

%prep
%setup -q -n %{tarball_basedir}

%build
# Build CLI tools
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT

# Install CLI tools
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
sed --in-place '1s/python /python2 /' $RPM_BUILD_ROOT/usr/bin/eucalyptus-imaging-worker

#
# There is no extension on the installed sudoers file for a reason
# It will only be read by sudo if there is *no* extension
#
install -p -m 0440 -D scripts/imaging-worker-sudo.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sudoers.d/imaging-worker
install -p -m 755 -D scripts/imaging-worker-init $RPM_BUILD_ROOT/%{_initddir}/%{name}
install -p -m 755 -D scripts/worker-ntp-update $RPM_BUILD_ROOT%{_libexecdir}/%{name}/ntp-update
install -m 6700 -d $RPM_BUILD_ROOT/%{_var}/{run,lib,log}/%{name}

install -p -m 0750 -D scripts/imaging-worker.cron $RPM_BUILD_ROOT%{_sysconfdir}/cron.d/imaging-worker
chmod 0640 $RPM_BUILD_ROOT%{_sysconfdir}/cron.d/imaging-worker

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group eucalyptus >/dev/null || groupadd -r eucalyptus
getent passwd imaging-worker >/dev/null || \
    useradd -d %{_var}/lib/imaging-worker \
    -M -s /sbin/nologin imaging-worker -G eucalyptus

# Stop running services for upgrade
if [ "$1" = "2" ]; then
    /sbin/service %{name} stop 2>/dev/null || :
fi

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%files
%defattr(-,root,root,-)
%doc README.md LICENSE
%{python_sitelib}/*
%{_bindir}/%{name}
%{_sysconfdir}/sudoers.d/imaging-worker
%{_initddir}/%{name}
%{_libexecdir}/%{name}
%config(noreplace) %{_sysconfdir}/cron.d/imaging-worker

%defattr(-,imaging-worker,imaging-worker,-)
%dir %{_sysconfdir}/%{name}
%dir %{_var}/run/%{name}
%dir %{_var}/log/%{name}
%dir %{_var}/lib/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/boto.cfg

%changelog
* Fri Jul 22 2016 Garrett Holmstrom <gholms@hpe.com> - 0.2.2
- Version bump (0.2.2)

* Tue Dec 16 2014 Eucalyptus Release Engineering <support@eucalyptus.com> - 0.0.1
- Added chkconfig changes

* Tue Jul 22 2014 Eucalyptus Release Engineering <support@eucalyptus.com> - 0.0.1
- Switched to monolithic source tarball naming
- Switched to xz compression

* Sat Feb 22 2014 Eucalyptus Release Engineering <support@eucalyptus.com> - 0.0.1
- Initial build
