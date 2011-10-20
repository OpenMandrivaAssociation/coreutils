Summary:	The GNU core utilities: a set of tools commonly used in shell scripts
Name:		coreutils
Version:	8.14
Release:	1
License:	GPLv3+
Group:		System/Base
Url:		http://www.gnu.org/software/coreutils/
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source1:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz.sig
Source200:	su.pamd
Source202:	su-l.pamd

# fileutils
Patch101:	coreutils-8.2-spacedir.patch
Patch1155:	coreutils-8.2-force-option--override--interactive-option.patch
Patch118:	fileutils-4.1-ls_h.patch
Patch500:	coreutils-8.3-mem.patch

# sh-utils

#add info about TZ envvar to date manpage
Patch703:	coreutils-6.11-dateman.patch
#set paths for su explicitly, don't get influenced by paths.h
Patch704:	sh-utils-1.16-paths.patch
# RMS will never accept the PAM patch because it removes his historical
# rant about Twenex and the wheel group, so we'll continue to maintain
# it here indefinitely.
Patch706:	coreutils-8.7-pam.patch
Patch713:	coreutils-4.5.3-langinfo.patch

# (sb) lin18nux/lsb compliance - normally from here:
# http://www.openi18n.org/subgroups/utildev/patch/
# this one is actually a merger of 5.2 and 5.3, as join segfaults
# compiled with gcc4 and the 5.1/5.2 patch
# fwang: we often get this patch from fedora
Patch800:	coreutils-8.14-new-i18n.patch

Patch909:	coreutils-5.1.0-64bit-fixes.patch

# https://qa.mandriva.com/show_bug.cgi?id=38577
Patch911:	coreutils-8.3-groupfix.patch

Patch1011:	coreutils-8.14-DIR_COLORS-mdkconf.patch
#(peroyvind): add back always red blinking on broken symlinks
Patch1013:	coreutils-8.2-always-blinking-colors-on-broken-symlinks.patch
#(peroyvind): fix a test that fails to compile with -Werror=format-security
Patch1014:	coreutils-8.8-check-string-format.patch

# fedora patches
#add note about no difference between binary/text mode on Linux - md5sum manpage
Patch2101:	coreutils-8.9-manpages.patch
#temporarily workaround probable kernel issue with TCSADRAIN(#504798)
Patch2102:	coreutils-8.14-sttytcsadrain.patch
#do display processor type for uname -p/-i based on uname(2) syscall
Patch2103:	coreutils-8.2-uname-processortype.patch
#df --direct
Patch2104:	coreutils-8.9-df-direct.patch
#Fix mkstemp on sparc64
Patch2105:	coreutils-mkstemp.patch

#Call setsid() in su under some circumstances (bug #173008).
Patch2900:	coreutils-setsid.patch
#make runuser binary based on su.c
Patch2907:	coreutils-8.7-runuser.patch
#getgrouplist() patch from Ulrich Drepper.
Patch2908:	coreutils-8.14-getgrouplist.patch
#Prevent buffer overflow in who(1) (bug #158405).
Patch2912:	coreutils-overflow.patch
#compile su with pie flag and RELRO protection
Patch2917:	coreutils-8.4-su-pie.patch

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

%rename		mktemp

Provides:	stat = %{version}
Provides:	%{_bindir}/env
Provides:	/bin/env
Provides:	%{_bindir}/tr
Obsoletes:	base64
Conflicts:	tetex < 1.0.7-49mdk

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
BuildArch:	noarch

%description	doc
This package contains coreutils documentation in GNU info format.

%prep
%setup -q

# fileutils
# (tpg) seems to be fixed
#%patch101 -p1 -b .space~
%patch1155 -p1 -b .override~
%patch118 -p1

# textutils
%patch500 -p1

# sh-utils
%patch703 -p1 -b .dateman~
%patch704 -p1 -b .paths~
%patch706 -p1 -b .pam~
%patch713 -p1 -b .langinfo~

# li18nux/lsb
%patch800 -p1 -b .i18n~

%patch909 -p1 -b .64bit~
%patch911 -p1 -b .groups~

%patch1011 -p1 -b .colors_mdkconf~
%patch1013 -p1 -b .broken_blink~
%patch1014 -p1 -b .str_fmt~

%patch2101 -p1 -b .manpages~
%patch2102 -p1 -b .tcsadrain~
%patch2103 -p1 -b .sysinfo~
# (tpg) not needed for now
#%patch2104 -p1 -b .dfdirect~

%ifnarch %arm
%patch2105 -p1 -b .sparc~
%endif

%patch2900 -p1 -b .setsid~
%patch2907 -p1 -b .runuser~
%patch2908 -p1 -b .getgrouplist~
%patch2912 -p1 -b .overflow~
%patch2917 -p1 -b .pie~

chmod a+x tests/misc/sort-mb-tests tests/misc/id-context
chmod +w ./src/dircolors.h
./src/dcgen ./src/dircolors.hin > ./src/dircolors.h

export DEFAULT_POSIX2_VERSION=199209
aclocal -I m4
automake --gnits --add-missing
autoconf
bzip2 -9 ChangeLog

%build
export CFLAGS="%{optflags} -fPIC -D_GNU_SOURCE=1"

%configure2_5x \
	--enable-largefile \
	--enable-pam \
	--enable-install-program=su \
	--enable-no-install-program=arch,hostname,uptime,kill \
	--without-selinux \
	--disable-rpath \
	--disable-silent-rules

%make

%check
%make check

%install
%makeinstall_std

# man pages are not installed with make install
make mandir=%{buildroot}%{_mandir} install-man

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p %{buildroot}{/bin,%{_bindir},%{_sbindir},%{_sysconfdir}/pam.d}
for f in basename cat chgrp chmod chown cp cut date dd df echo env expr false id link ln ls mkdir mknod mktemp mv nice pwd rm rmdir sleep sort stat stty sync touch true uname unlink tac
do
	mv %{buildroot}/{%{_bindir},bin}/$f
done

# chroot was in /usr/sbin :
mv %{buildroot}/{%{_bindir},%{_sbindir}}/chroot
# {cat,sort,cut} were previously moved from bin to /usr/bin and linked into 
for f in cut env expr tac; do
	ln -s /bin/$f %{buildroot}%{_bindir}/$f
done

install -m644 src/dircolors.hin -D %{buildroot}%{_sysconfdir}/DIR_COLORS

# su
install -m 4755 src/su %{buildroot}/bin

install -m 644 %{SOURCE200} %{buildroot}%{_sysconfdir}/pam.d/su
install -m 644 %{SOURCE202} %{buildroot}%{_sysconfdir}/pam.d/su-l

#TV# find_lang look for LC_MESSAGES, not LC_TIME:
find %{buildroot}%{_datadir}/locale/ -name coreutils.mo | fgrep LC_TIME | xargs rm -f
%find_lang %{name}

%preun doc
%_remove_install_info %{name}.info

%post doc
%_install_info %{name}.info
# The next true is needed: else, if there's a problem, the 
# package'll be installed 2 times because of trigger faillure
true

%files -f %{name}.lang
%config(noreplace) %{_sysconfdir}/D*
%config(noreplace) %{_sysconfdir}/pam.d/su
%config(noreplace) %{_sysconfdir}/pam.d/su-l
%doc README
/bin/*
%{_bindir}/*
%{_sbindir}/chroot
%dir %{_libdir}/coreutils
%{_libdir}/coreutils/libstdbuf.so

%files doc
%doc ABOUT-NLS ChangeLog.bz2 NEWS THANKS TODO
%{_infodir}/coreutils*
%{_mandir}/man*/*
