%global nspr_version 4.35.0

# The upstream omits the trailing ".0", while we need it for
# consistency with the pkg-config version:
# https://bugzilla.redhat.com/show_bug.cgi?id=1578106
%{lua:
rpm.define(string.format("nspr_archive_version %s",
           string.gsub(rpm.expand("%nspr_version"), "(.*)%.0$", "%1")))
}

Summary:        Netscape Portable Runtime
Name:           nspr
Version:        %{nspr_version}+git1
Release:        1
License:        MPLv2.0
URL:            http://www.mozilla.org/projects/nspr/

# Sources available at ftp://ftp.mozilla.org/pub/mozilla.org/nspr/releases/
# When hg tag based snapshots are being used, refer to hg documentation on
# mozilla.org and check out subdirectory mozilla/nsprpub.
Source0:        %{name}-%{nspr_archive_version}.tar.gz

Patch1:         nspr-config-pc.patch
Patch2:         nspr-gcc-atomics.patch

BuildRequires:  perl

%description
NSPR provides platform independence for non-GUI operating system
facilities. These facilities include threads, thread synchronization,
normal file and network I/O, interval timing and calendar time, basic
memory management (malloc and free) and shared library linking.

%package devel
Summary:        Development libraries for the Netscape Portable Runtime
Requires:       nspr = %{version}-%{release}

%description devel
Header files for doing development with the Netscape Portable Runtime.

%prep
%setup -q -n %{name}-%{nspr_archive_version}

# Original nspr-config is not suitable for our distribution,
# because on different platforms it contains different dynamic content.
# Therefore we produce an adjusted copy of nspr-config that will be
# identical on all platforms.
# However, we need to use original nspr-config to produce some variables
# that go into nspr.pc for pkg-config.

cp ./nspr/config/nspr-config.in ./nspr/config/nspr-config-pc.in
%patch1 -p0 -b .flags
pushd nspr
%patch2 -p1 -b .gcc-atomics
popd

%build
# set buildtime to "last-modification-time"
BUILD_STRING="$(date -u -d "@${SOURCE_DATE_EPOCH}" "+%%F %%T")"
BUILD_TIME="$(date -u -d "@${SOURCE_DATE_EPOCH}" "+%%s000000")"
./nspr/configure \
                 --prefix=%{_prefix} \
                 --libdir=%{_libdir} \
                 --includedir=%{_includedir}/nspr4 \
%ifnarch noarch
%if 0%{__isa_bits} == 64
                 --enable-64bit \
%endif
%endif
%ifarch armv7l armv7hl armv7nhl
                 --enable-thumb2 \
%endif
                 --enable-optimize="$RPM_OPT_FLAGS" \
                 --disable-debug

%make_build SH_DATE="$BUILD_STRING" SH_NOW="$BUILD_TIME"

%check
# Run test suite.
perl ./nspr/pr/tests/runtests.pl 2>&1 | tee output.log

TEST_FAILURES=`grep -c FAILED ./output.log` || :
if [ $TEST_FAILURES -ne 0 ]; then
  echo "error: test suite returned failure(s)"
  exit 1
fi
echo "test suite completed"

%install
%{__rm} -Rf %{buildroot}
%make_install

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%license nspr/LICENSE
%{_libdir}/libnspr4.so
%{_libdir}/libplc4.so
%{_libdir}/libplds4.so

%files devel
%defattr(-,root,root,-)
%{_includedir}/nspr4
%{_libdir}/pkgconfig/nspr.pc
%{_datadir}/aclocal/nspr.m4
%{_bindir}/nspr-config
%exclude %{_bindir}/compile-et.pl
%exclude %{_bindir}/prerr.properties
