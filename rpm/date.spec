# Upstream suggests to pick bugfixes directly from master
# as they're not planning to tag any more releases
%global date    20210322
%global commit  77bd6b92a4f7f6a1bbbc44952e6502a3448376b0

%global shortcommit  %(c=%{commit}; echo ${c:0:7})
%global gitrel  %{?date:.%{date}git%{shortcommit}}
%global gitver  %{?date:-%{date}git%{shortcommit}}

Name:           date
Version:        3.0.0
Release:        4%{?gitrel}%{?dist}
Summary:        Date and time library based on the C++11/14/17 <chrono> header

License:        MIT
URL:            https://github.com/HowardHinnant/date
Source0:        %{name}-%{version}.tar.gz
# add pkg-config support to make the package compatible with meson
# https://github.com/HowardHinnant/date/pull/538
Patch0:         output-date-pc-for-pkg-config.patch

BuildRequires:  cmake >= 3.7
BuildRequires:  gcc-c++
BuildRequires:  make
# required for test suite
BuildRequires:  tzdata

%global _description %{expand:
This is actually several separate C++11/C++14/C++17 libraries:
 - "date.h" is a header-only library which builds upon <chrono>.
   It adds some new duration types, and new time_point types. It
   also adds "field" types such as year_month_day which is a
   struct {year, month, day}. And it provides convenient means
   to convert between the "field" types and the time_point types.
 - "tz.h" / "tz.cpp" are a timezone library built on top of the
   "date.h" library. This timezone library is a complete parser
   of the IANA timezone database. It provides for an easy way to
   access all of the data in this database, using the types from
   "date.h" and <chrono>. The IANA database also includes data
   on leap seconds, and this library provides utilities to compute
   with that information as well.
Slightly modified versions of "date.h" and "tz.h" were voted into
the C++20 working draft.}

%description 
%{_description}

Categories:
  - Library

# only timezone libary has binary part
%package -n     libdate-tz
Summary:        Timezone library built on top of the date library
Requires:       tzdata

%description -n libdate-tz
Timezone library built on top of the date library. This timezone library
is a complete parser of the IANA timezone database. It provides for
an easy way to access all of the data in this database, using the types
from "date.h" and <chrono>. The IANA database also includes data on leap
seconds, and this library provides utilities to compute with that
information as well.


%package        devel
Summary:        Date and time library based on the C++11/14/17 <chrono> header
Requires:       libdate-tz%{?_isa} = %{version}-%{release}
# virtual Provide for header-only parts of the library
Provides:       %{name}-static = %{version}-%{release}

%description    devel %{_description}

%prep
%setup -q -n %{name}-%{version}/date
%patch0 -p1
# remove broken tests
# fails due to gcc std::locale bugs (gcc#86976, HowardHinnant/date#388)
rm -f test/date_test/parse.pass.cpp
# fails in fedora-rawhide-i386 due to missing timezone configuration
rm -f test/tz_test/zoned_time_deduction.pass.cpp
# one more test that depends on localtime. we don't even install this header
rm -rf test/solar_hijri_test/


%build
%cmake \
    -DBUILD_TZ_LIB=ON     \
    -DUSE_SYSTEM_TZ_DB=ON \
    -DENABLE_DATE_TESTING=ON
%{__make} %{?_smp_mflags}


%install
%{__rm} -rf %{buildroot}
%{__make} install DESTDIR=%{buildroot}


%post -n libdate-tz -p /sbin/ldconfig

%postun -n libdate-tz -p /sbin/ldconfig

%files -n libdate-tz
%{_libdir}/libdate-tz.so.*

%files devel
%{_includedir}/%{name}/
%{_libdir}/libdate-tz.so
%{_libdir}/cmake/%{name}/
%{_libdir}/pkgconfig/%{name}.pc


%changelog
* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.0-4.20200708git6952fb5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.0-3.20200708git6952fb5
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.0-2.20200708git6952fb5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 08 2020 Aleksei Bavshin <alebastr89@gmail.com> - 3.0.0-1
- Upstream release 3.0.0 (+4 commits from git master)
- Rename libtz subpackage to libdate-tz according to upstream change
- Use new cmake_build macros with out-of-tree build

* Fri Feb 07 2020 Aleksei Bavshin <alebastr89@gmail.com> - 2.4.1-1.20200207git9a0ee254
- Initial import (#1801013)
