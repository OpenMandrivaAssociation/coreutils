%bcond_with	crosscompile

Summary:	The GNU core utilities: a set of tools commonly used in shell scripts
Name:		coreutils
Version:	8.22
Release:	2
License:	GPLv3+
Group:		System/Base
Url:		http://www.gnu.org/software/coreutils/
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source2:	coreutils-DIR_COLORS.256color
Source3:	coreutils-colorls.sh
Source4:	coreutils-colorls.csh

# From upstream
Patch1:		coreutils-8.22-cp-selinux.patch
Patch2:		coreutils-8.22-datetzcrash.patch
Patch3:		coreutils-8.22-dd-sparsetest-xfsspeculativeprealloc.patch

# fileutils
Patch101:	coreutils-8.2-spacedir.patch
Patch1155:	coreutils-8.20-force-option--override--interactive-option.patch
Patch118:	fileutils-4.1-ls_h.patch
Patch500:	coreutils-8.3-mem.patch

# sh-utils

#add info about TZ envvar to date manpage
Patch703:	coreutils-8.21-dateman.patch
Patch713:	coreutils-4.5.3-langinfo.patch

# (sb) lin18nux/lsb compliance - normally from here:
# http://www.openi18n.org/subgroups/utildev/patch/
# this one is actually a merger of 5.2 and 5.3, as join segfaults
# compiled with gcc4 and the 5.1/5.2 patch
# fwang: we often get this patch from fedora
Patch800:	coreutils-i18n.patch

Patch909:	coreutils-5.1.0-64bit-fixes.patch

# https://qa.mandriva.com/show_bug.cgi?id=38577
Patch911:	coreutils-8.3-groupfix.patch

Patch1011:	coreutils-8.22-DIR_COLORS-mdkconf.patch
#(peroyvind): add missing header includes
Patch1015:	coreutils-8.22-include-missing-headers.patch

# fedora patches
#add note about no difference between binary/text mode on Linux - md5sum manpage
Patch2101:	coreutils-8.22-manpages.patch
#temporarily workaround probable kernel issue with TCSADRAIN(#504798)
Patch2102:	coreutils-8.19-sttytcsadrain.patch
#do display processor type for uname -p/-i based on uname(2) syscall
Patch2103:	coreutils-8.2-uname-processortype.patch
#df --direct
Patch2104:	coreutils-8.22-df-direct.patch
#add note about mkdir --mode behaviour into info documentation(#610559)
Patch2107:	coreutils-8.4-mkdir-modenote.patch

#getgrouplist() patch from Ulrich Drepper.
Patch2908:	coreutils-8.14-getgrouplist.patch
#Prevent buffer overflow in who(1) (bug #158405).
Patch2912:	coreutils-overflow.patch
#Temporarily disable df symlink test, failing
Patch2913:	coreutils-8.22-temporarytestoff.patch

Patch3001:	dummy_help2man.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gettext
BuildRequires:	strace
BuildRequires:	texinfo >= 4.3
BuildRequires:	acl-devel
BuildRequires:	attr-devel
BuildRequires:	gmp-devel
BuildRequires:	cap-devel
BuildRequires:	pkgconfig(openssl)

%rename		mktemp
Provides:	stat = %{version}
Provides:	%{_bindir}/env
Provides:	/bin/env
Provides:	%{_bindir}/tr
Obsoletes:	base64
Suggests:	coreutils-doc
Conflicts:	util-linux < 2.23.1-2

%description
This package is the union of the old GNU fileutils, sh-utils, and 
textutils packages.

These tools are the GNU versions of common useful and popular
file & text utilities which are used for:
- file management
- shell scripts
- modifying text file (spliting, joining, comparing, modifying, ...)

Most of these programs have significant advantages over their Unix
counterparts, such as greater speed, additional options, and fewer
arbitrary limits.

%package	doc
Summary:	Coreutils documentation in info format
Group:		Books/Computer books
Requires:	coreutils
BuildArch:	noarch
Conflicts:	util-linux < 2.23.1-2

%description	doc
This package contains coreutils documentation in GNU info format.

%prep
%setup -q

# From upstream
%patch1 -p1 -b .nullcontext~
%patch2 -p1 -b .tzcrash~
%patch3 -p1 -b .xfs~

# fileutils
# (tpg) seems to be fixed
#patch101 -p1 -b .space~
%patch1155 -p1 -b .override~
%patch118 -p1 -b .lsh~

# textutils
%patch500 -p1

# sh-utils
%patch703 -p1 -b .dateman~
%patch713 -p1 -b .langinfo~

# li18nux/lsb
%patch800 -p1 -b .i18n~

%patch909 -p1 -b .64bit~
%patch911 -p1 -b .groups~

%patch1011 -p1 -b .colors_mdkconf~
%patch1015 -p1 -b .hdrs~

# From upstream
%patch2101 -p1 -b .manpages~
%patch2102 -p1 -b .tcsadrain~
%patch2103 -p1 -b .sysinfo~
%patch2104 -p1 -b .dfdirect~
%patch2107 -p1 -b .mkdirmode~

%patch2908 -p1 -b .getgrouplist~
%patch2912 -p1 -b .overflow~
%patch2913 -p1 -b .testoff~

%if %{with crosscompile}
%patch3001 -p1 -b .help2man~
%endif

chmod a+x tests/misc/sort-mb-tests.sh tests/df/direct.sh tests/cp/no-ctx.sh
chmod +w ./src/dircolors.h
./src/dcgen ./src/dircolors.hin > ./src/dircolors.h

export DEFAULT_POSIX2_VERSION=199209
aclocal -I m4 --dont-fix
automake --gnits --add-missing
autoconf
bzip2 -9 ChangeLog

# XXX docs should say /var/run/[uw]tmp not /etc/[uw]tmp
sed -e 's,/etc/utmp,/var/run/utmp,g;s,/etc/wtmp,/var/run/wtmp,g' -i doc/coreutils.texi

#fix typos/mistakes in localized documentation(rhbz#439410, rhbz#440056)
find ./po/ -name "*.p*" | xargs \
 sed -i \
 -e 's/-dpR/-cdpR/'

# Regenerate manpages
touch man/*.x

%build
%global optflags %{optflags} -Os
%configure2_5x \
	--enable-largefile \
	--enable-no-install-program=hostname,uptime,kill \
	--enable-install-program=arch \
	--without-selinux \
	--with-packager="%{packager}" \
	--with-packager-version="%{version}-%{release}" \
	--with-packager-bug-reports="%{bugurl}" \
	--with-tty-group \
	--with-openssl

%make

%check
#make check

%install
%makeinstall_std

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p %{buildroot}{/bin,%{_bindir},%{_sbindir}}
for f in basename arch cat chgrp chmod chown cp cut date dd df echo env expr false id link ln ls mkdir mknod mktemp mv nice pwd rm rmdir sleep sort stat stty sync touch true uname unlink tac
do
	mv %{buildroot}{%{_bindir},/bin}/$f
done

# chroot was in /usr/sbin :
mv %{buildroot}{%{_bindir},%{_sbindir}}/chroot
# {cat,sort,cut} were previously moved from bin to /usr/bin and linked into 
for f in cut env expr tac; do
	ln -s /bin/$f %{buildroot}%{_bindir}/$f
done

install -p -m644 src/dircolors.hin -D %{buildroot}%{_sysconfdir}/DIR_COLORS
install -p -m644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/DIR_COLORS.256color
install -p -m644 %{SOURCE3} -D %{buildroot}%{_sysconfdir}/profile.d/90_colorls.sh
install -p -m644 %{SOURCE4} -D %{buildroot}%{_sysconfdir}/profile.d/90_colorls.csh

#TV# find_lang look for LC_MESSAGES, not LC_TIME:
find %{buildroot}%{_datadir}/locale/ -name coreutils.mo | grep LC_TIME | xargs rm -f
%find_lang %{name}

%files -f %{name}.lang
%doc README
%config(noreplace) %{_sysconfdir}/DIR_COLORS
%config(noreplace) %{_sysconfdir}/DIR_COLORS.256color
%{_sysconfdir}/profile.d/90_colorls.sh
%{_sysconfdir}/profile.d/90_colorls.csh
/bin/*
%{_bindir}/*
%{_sbindir}/chroot
%dir %{_libexecdir}/coreutils
%{_libexecdir}/coreutils/libstdbuf.so

%files doc
%doc ABOUT-NLS ChangeLog.bz2 NEWS THANKS TODO
%{_infodir}/coreutils*
%{_mandir}/man*/*

