%bcond_with crosscompile

# (tpg) build coreutils as a single binary
%bcond_without single

# (tpg) optimize size a bit
%ifnarch riscv64
%global optflags %{optflags} -Oz -fPIE -D_GNU_SOURCE=1 --rtlib=compiler-rt
%endif

# do not make coreutils-single depend on /usr/bin/coreutils
%global __requires_exclude ^/%{_bin}/coreutils$

Summary:	The GNU core utilities: a set of tools commonly used in shell scripts
Name:		coreutils
Version:	8.32
Release:	1
License:	GPLv3+
Group:		System/Base
Url:		http://www.gnu.org/software/coreutils/
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source2:	coreutils-DIR_COLORS.256color
Source3:	coreutils-colorls.sh
Source4:	coreutils-colorls.csh

# fileutils
Patch1155:	coreutils-8.24-force-option--override--interactive-option.patch
Patch118:	fileutils-4.1-ls_h.patch
Patch500:	coreutils-8.3-mem.patch

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

Patch1011:	coreutils-8.26-DIR_COLORS-mdkconf.patch
#(peroyvind): fix a test that fails to compile with -Werror=format-security
Patch1014:	coreutils-8.22-check-string-format.patch
#(peroyvind): add missing header includes
Patch1015:	coreutils-8.24-include-missing-headers.patch
# https://github.com/coreutils/coreutils/issues/11
Patch1016:	coreutils-8.28-check-for-__builtin_mul_overflow_p.patch
Patch1017:	coreutils-8.28-inline.patch

# fedora patches
#add note about no difference between binary/text mode on Linux - md5sum manpage
Patch2101:	coreutils-6.10-manpages.patch
#do display processor type for uname -p/-i based on uname(2) syscall
Patch2103:	coreutils-8.2-uname-processortype.patch
#df --direct
Patch2104:	coreutils-8.24-df-direct.patch
#add note about mkdir --mode behaviour into info documentation(#610559)
Patch2107:	coreutils-8.4-mkdir-modenote.patch
# (sb) lin18nux/lsb compliance - expand/unexpand
Patch2108:	coreutils-i18n-expand-unexpand.patch
# i18n patch for cut - old version - used
Patch2109:	coreutils-i18n-cut-old.patch
# The unexpand patch above is not correct. Sent to the patch authors
Patch2110:	coreutils-i18n-fix-unexpand.patch
#(un)expand - allow multiple files on input - broken by patch 801
Patch2111:	coreutils-i18n-fix2-expand-unexpand.patch
#(un)expand - test BOM headers
Patch2112:	coreutils-i18n-un-expand-BOM.patch
# make 'sort -h' work for arbitrary column even when using UTF-8 locales
Patch2113:	coreutils-i18n-sort-human.patch
# fold: preserve new-lines in mutlibyte text (#1418505)
Patch2114:	coreutils-i18n-fold-newline.patch
# do not use IF_LINT for initialization of scalar variables
Patch2115:	https://src.fedoraproject.org/rpms/coreutils/raw/master/f/coreutils-8.32-if-lint.patch
# ls: restore 8.31 behavior on removed directories
Patch2116:	https://src.fedoraproject.org/rpms/coreutils/raw/master/f/coreutils-8.32-ls-removed-dir.patch

#getgrouplist() patch from Ulrich Drepper.
Patch2908:	coreutils-8.14-getgrouplist.patch

%if %{with crosscompile}
Patch3001:	dummy_help2man.patch
%endif

BuildRequires:	locales-fr
BuildRequires:	locales-ja
BuildRequires:	locales-zh
BuildRequires:	locales-tr
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gettext
BuildRequires:	strace
BuildRequires:	texinfo >= 4.3
BuildRequires:	acl-devel
BuildRequires:	attr-devel
BuildRequires:	cap-devel
BuildRequires:	hostname
%if !%{with single}
# disabled when build as single binary
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(openssl)
%endif

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

%package doc
Summary:	Coreutils documentation in info format
Group:		Books/Computer books
Requires:	coreutils
BuildArch:	noarch
Conflicts:	util-linux < 2.23.1-2

%description doc
This package contains coreutils documentation in GNU info format.

%prep
%autosetup -p1

chmod a+x tests/misc/sort-mb-tests.sh tests/df/direct.sh tests/cp/no-ctx.sh
chmod +w ./src/dircolors.h
./src/dcgen ./src/dircolors.hin > ./src/dircolors.h

export DEFAULT_POSIX2_VERSION=200112
aclocal -I m4 --dont-fix
automake --gnits --add-missing
autoconf --force

# XXX docs should say /var/run/[uw]tmp not /etc/[uw]tmp
sed -e 's,/etc/utmp,/var/run/utmp,g;s,/etc/wtmp,/var/run/wtmp,g' -i doc/coreutils.texi

%build
# disabled when build as single binary:
# openssl
# gmp

%configure \
	--enable-largefile \
	--enable-no-install-program=hostname,uptime,kill \
	--enable-install-program=arch \
	--without-selinux \
	--with-packager="%{packager}" \
	--with-packager-version="%{version}-%{release}" \
	--with-packager-bug-reports="%{bugurl}" \
%if %{with single}
	--enable-single-binary=symlinks \
	--without-openssl \
	--without-gmp \
%else
	--disable-single-binary \
	--with-openssl \
	--with-gmp \
%endif
	--with-tty-group

# Regenerate manpages
touch man/*.x

%make_build

#check
#make check

%install
%make_install

# man pages are not installed with make install
make mandir=%{buildroot}%{_mandir} install-man

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p %{buildroot}{/bin,%{_bindir},%{_sbindir}}
for f in basename arch cat chgrp chmod chown coreutils cp cut date dd df echo env expr false id link ln ls mkdir mknod mktemp mv nice pwd rm rmdir sleep sort stat stty sync touch true uname unlink tac
do
    mv %{buildroot}{%{_bindir},/bin}/$f || :
done

# chroot was in /usr/sbin :
mv %{buildroot}{%{_bindir},%{_sbindir}}/chroot
# {cat,sort,cut} were previously moved from bin to /usr/bin and linked into
for f in cut env expr tac true; do
    ln -s /bin/$f %{buildroot}%{_bindir}/$f
done

install -p -m644 src/dircolors.hin -D %{buildroot}%{_sysconfdir}/DIR_COLORS
install -p -m644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/DIR_COLORS.256color
install -p -m644 %{SOURCE3} -D %{buildroot}%{_sysconfdir}/profile.d/90_colorls.sh
install -p -m644 %{SOURCE4} -D %{buildroot}%{_sysconfdir}/profile.d/90_colorls.csh

#TV# find_lang look for LC_MESSAGES, not LC_TIME:
find %{buildroot}%{_datadir}/locale/ -name coreutils.mo | grep LC_TIME | xargs rm -f

%if %{with single}
# Coreutils lives in /bin, not /usr/bin
for i in %{_bindir} %{_sbindir}; do
    cd %{buildroot}$i
	for i in *; do
	    rm $i
	    ln -sf ../../bin/coreutils $i
	done
    cd -
done
%endif

# (tpg) compress these files
xz --text ChangeLog

%find_lang %{name}

%files -f %{name}.lang
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
%doc ABOUT-NLS ChangeLog.xz NEWS THANKS TODO README
%{_infodir}/coreutils*
%{_mandir}/man*/*
