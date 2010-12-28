Summary:	The GNU core utilities: a set of tools commonly used in shell scripts
Name:		coreutils
Version:	8.8
Release:	%mkrel 1
License:	GPLv3
Group:		System/Base
Url:		http://www.gnu.org/software/coreutils/
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source200:	su.pamd
Source201:	help2man
Source202:	su-l.pamd

# fileutils
Patch101:	coreutils-8.2-spacedir.patch
Patch1155:	coreutils-8.2-force-option--override--interactive-option.patch
Patch118:	fileutils-4.1-ls_h.patch
Patch500:	coreutils-8.3-mem.patch

# sh-utils
Patch703:	coreutils-6.11-dateman.patch
Patch704:	sh-utils-1.16-paths.patch
# RMS will never accept the PAM patch because it removes his historical
# rant about Twenex and the wheel group, so we'll continue to maintain
# it here indefinitely.
Patch706:	coreutils-8.7-pam.patch
Patch711:	sh-utils-2.0.12-hname.patch

# (sb) lin18nux/lsb compliance - normally from here:
# http://www.openi18n.org/subgroups/utildev/patch/
# this one is actually a merger of 5.2 and 5.3, as join segfaults
# compiled with gcc4 and the 5.1/5.2 patch
# fwang: we often get this patch from fedora
Patch800:	coreutils-8.8-new-i18n.patch
# small pt_BR fix
Patch801:	coreutils-5.2.1-ptbrfix.patch

Patch904:	coreutils-5.0.91-allow_old_options.patch
Patch909:	coreutils-5.1.0-64bit-fixes.patch
Patch910:	coreutils-8.2-uname-processortype.patch

# https://qa.mandriva.com/show_bug.cgi?id=38577
Patch911:	coreutils-8.3-groupfix.patch

Patch1011:	coreutils-8.2-DIR_COLORS-mdkconf.patch
#(peroyvind): add back always red blinking on broken symlinks
Patch1013:	coreutils-8.2-always-blinking-colors-on-broken-symlinks.patch

BuildRequires:	locales-fr
BuildRequires:	locales-ja
BuildRequires:	locales-zh
BuildRequires:	locales-tr
BuildRequires:	gettext
BuildRequires:	termcap-devel
BuildRequires:	pam-devel
BuildRequires:	texinfo >= 4.3
# We need automake which supports the dist-xz target
BuildRequires:	automake >= 1.10.2-2
# And tar which supports xz automagically since rpm.org seems to rely on this(..?)
BuildRequires:	tar >= 1.21-2
BuildRequires:	libacl-devel
BuildRequires:	libattr-devel
BuildRequires:	libgmp-devel
BuildRequires:	libcap-devel
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	strace
Requires:	pam >= 0.66-12

Provides:	fileutils = %{version}
Obsoletes:	fileutils < %{version}
Provides:	sh-utils = %{version}
Obsoletes:	sh-utils < %{version}
Provides:	textutils = %{version}
Obsoletes:	textutils  < %{version}
Provides:	mktemp = %{version}
Obsoletes:	mktemp < %{version}

Provides:	stat = %{version}
Provides:	%{_bindir}/env
Provides:	/bin/env
Obsoletes:	base64
Conflicts:	tetex < 1.0.7-49mdk
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

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
Requires:	coreutils >= 4.5.4-2mdk
Requires(post,preun):	info-install
BuildArch: noarch

%description	doc
This package contains coreutils documentation in GNU info format.

%prep
%setup -q

# fileutils
%patch101 -p1 -b .space
%patch1155 -p1 -b .override
%patch118 -p1

# textutils
%patch500 -p1

# sh-utils
%patch703 -p1 -b .dateman
%patch704 -p1 -b .paths
%patch706 -p1 -b .pam

# li18nux/lsb
%patch800 -p1 -b .i18n
#%patch801 -p0 -b .ptbr

#%patch904 -p1 -b .old-options
%patch909 -p1 -b .64bit
%patch910 -p1 -b .cpu
%patch911 -p1 -b .groups

%patch1011 -p1 -b .colors_mdkconf
%patch1013 -p1 -b .broken_blink

cp %SOURCE201 man/help2man
chmod a+x tests/misc/sort-mb-tests
chmod a+x tests/misc/id-context
chmod +x man/help2man
chmod +w ./src/dircolors.h
./src/dcgen ./src/dircolors.hin > ./src/dircolors.h

export DEFAULT_POSIX2_VERSION=199209
aclocal -I m4
automake --gnits --add-missing
autoconf
bzip2 -9 ChangeLog

%build
export CFLAGS="%{optflags} -D_GNU_SOURCE=1"

%configure2_5x \
	--enable-largefile \
	--enable-pam \
	--enable-install-program=su \
	--enable-no-install-program=arch,hostname,uptime \
	--without-selinux \
	--disable-rpath \
	--disable-silent-rules

%make HELP2MAN=$PWD/man/help2man

%check
%define Werror_cflags %nil
# Run the test suite:
%make check CFLAGS="%{optflags} -D_GNU_SOURCE=1"

%install
# for help2man:
export PATH=$PATH:RPM_BUILD_ROOT/man

rm -rf %{buildroot}
%makeinstall_std

# man pages are not installed with make install
make mandir=%{buildroot}%{_mandir} install-man

# fix japanese catalog file
if [ -d %{buildroot}%{_datadir}/locale/ja_JP.EUC/LC_MESSAGES ]; then
   mkdir -p %{buildroot}%{_datadir}/locale/ja/LC_MESSAGES
   mv %{buildroot}%{_datadir}/locale/ja_JP.EUC/LC_MESSAGES/*mo \
		%{buildroot}%{_datadir}/locale/ja/LC_MESSAGES
   rm -rf %{buildroot}%{_datadir}/locale/ja_JP.EUC
fi

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p %{buildroot}{/bin,%{_bindir},%{_sbindir},%{_sysconfdir}/pam.d}
for f in basename cat chgrp chmod chown cp cut date dd df echo env expr false id link ln ls mkdir mknod mktemp mv nice pwd rm rmdir sleep sort stat stty sync touch true uname unlink tac
do
	mv %{buildroot}/{%{_bindir},bin}/$f
done

ln -sf ../../bin/expr %{buildroot}%{_bindir}/
ln -sf ../../bin/tac %{buildroot}%{_bindir}/

# chroot was in /usr/sbin :
mv %{buildroot}/{%{_bindir},%{_sbindir}}/chroot
# {cat,sort,cut} were previously moved from bin to /usr/bin and linked into 
for i in env cut; do ln -sf ../../bin/$i %{buildroot}/usr/bin; done

install -m644 src/dircolors.hin -D %{buildroot}%{_sysconfdir}/DIR_COLORS

# su
install -m 4755 src/su %{buildroot}/bin

install -m 644 %{SOURCE200} %{buildroot}%{_sysconfdir}/pam.d/su
install -m 644 %{SOURCE202} %{buildroot}%{_sysconfdir}/pam.d/su-l


# fix conflict with util-linux:
rm -f %{buildroot}%{_mandir}/man1/kill.1

#TV# find_lang look for LC_MESSAGES, not LC_TIME:
#TV(cd %{buildroot}; find .%_datadir/locale/ -name coreutils.mo | fgrep LC_TIME | \
#TV	sed -e "s!^.*/share/locale/\([^/]*\)/!%lang(\1) %_datadir/locale/\1/!") >> %name.lang
find %{buildroot}%{_datadir}/locale/ -name coreutils.mo | fgrep LC_TIME | xargs rm -f

%find_lang %{name}

%clean
rm -rf %{buildroot}

%pre doc
# We must desinstall theses info files since they're merged in
# coreutils.info. else their postun'll be runned too last
# and install-info'll faill badly because of doubles
for file in sh-utils.info textutils.info fileutils.info; do
	if [ -f /usr/share/info/$file.bz2 ]; then
		/sbin/install-info /usr/share/info/$file.bz2 --dir=/usr/share/info/dir --remove &> /dev/null
	fi
done

%preun doc
%_remove_install_info %name.info

%post doc
%_install_info %name.info
# The next true is needed: else, if there's a problem, the 
# package'll be installed 2 times because of trigger faillure
true

%files -f %{name}.lang
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/D*
%config(noreplace) %{_sysconfdir}/pam.d/su
%config(noreplace) %{_sysconfdir}/pam.d/su-l
%doc README
/bin/*
%{_bindir}/*
%{_sbindir}/chroot
%{_libdir}/coreutils/libstdbuf.so

%files doc
%defattr(-,root,root)
%doc ABOUT-NLS ChangeLog.bz2 NEWS THANKS TODO
%{_infodir}/coreutils*
%{_mandir}/man*/*
