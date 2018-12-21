Summary:        Netscape Portable Runtime
Name:           nspr
Version:        4.20
Release:        1
License:        MPLv1.1 or GPLv2+ or LGPLv2+
URL:            http://www.mozilla.org/projects/nspr/
Group:          System/Libraries
Source0:        https://ftp.mozilla.org/pub/mozilla.org/nspr/releases/v%{version}/src/%{name}-%{version}.tar.gz

Patch1:         nspr-config-pc.patch
Patch2:         nspr-4.9-arm-dont-guess-thumb.patch
Patch3:         nspr-4.8.8-notimestamping.patch

%description
NSPR provides platform independence for non-GUI operating system
facilities. These facilities include threads, thread synchronization,
normal file and network I/O, interval timing and calendar time, basic
memory management (malloc and free) and shared library linking.

%package devel
Summary:        Development libraries for the Netscape Portable Runtime
Group:          Development/Libraries
Requires:       nspr = %{version}-%{release}

%description devel
Header files for doing development with the Netscape Portable Runtime.

%prep
%setup -q

# Original nspr-config is not suitable for our distribution,
# because on different platforms it contains different dynamic content.
# Therefore we produce an adjusted copy of nspr-config that will be
# identical on all platforms.
# However, we need to use original nspr-config to produce some variables
# that go into nspr.pc for pkg-config.

cp ./nspr/config/nspr-config.in ./nspr/config/nspr-config-pc.in
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
./nspr/configure \
                 --prefix=%{_prefix} \
                 --libdir=%{_libdir} \
                 --includedir=%{_includedir}/nspr4 \
%ifarch x86_64 ppc64 ia64 s390x sparc64 aarch64
                 --enable-64bit \
%endif
%ifarch armv7thl armv7tnhl
                 --enable-thumb2 \
%endif
                 --enable-optimize="$RPM_OPT_FLAGS" \
                 --disable-debug

make

%install
%{__rm} -Rf $RPM_BUILD_ROOT

%make_install

# Get rid of the things we don't want installed (per upstream)
%{__rm} -r \
   $RPM_BUILD_ROOT/%{_bindir}/compile-et.pl \
   $RPM_BUILD_ROOT/%{_bindir}/prerr.properties \
   $RPM_BUILD_ROOT/%{_datadir}/aclocal/nspr.m4 \
   $RPM_BUILD_ROOT/%{_includedir}/nspr4/md

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so

%files devel
%defattr(-, root, root)
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so
%{_includedir}/nspr4
%{_libdir}/pkgconfig/nspr.pc
%{_bindir}/nspr-config
