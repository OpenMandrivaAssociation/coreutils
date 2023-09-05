# (tpg) optimize size a bit
%ifnarch riscv64
%global optflags %{optflags} -Oz -fno-strict-aliasing -fpic -Dlint --rtlib=compiler-rt
%endif

# do not make coreutils-single depend on /usr/bin/coreutils
%global __requires_exclude ^%{_bindir}/coreutils$

Summary:	The GNU core utilities: a set of tools commonly used in shell scripts
Name:		coreutils
Version:	9.4
Release:	1
License:	GPLv3+
Group:		System/Base
Url:		http://www.gnu.org/software/coreutils/
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source1:	coreutils-colorls.sh
Source2:	coreutils-colorls.csh
Patch0:		coreutils-9.0-clang.patch

# disable the test-lock gnulib test prone to deadlock
Patch100:	coreutils-8.26-test-lock.patch

# downstream changes to default DIR_COLORS
Patch102:	https://src.fedoraproject.org/rpms/coreutils/raw/rawhide/f/coreutils-8.32-DIR_COLORS.patch

#do display processor type for uname -p/-i based on uname(2) syscall
Patch103:	coreutils-8.2-uname-processortype.patch

#df --direct
Patch104:	coreutils-df-direct.patch
#add note about mkdir --mode behaviour into info documentation(#610559)
Patch107:	coreutils-8.4-mkdir-modenote.patch

# sh-utils
#add info about TZ envvar to date manpage
Patch703:	sh-utils-2.0.11-dateman.patch

# (sb) lin18nux/lsb compliance - multibyte functionality patch
Patch800:	https://www.linuxfromscratch.org/patches/downloads/coreutils/coreutils-9.4-i18n-1.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gettext
BuildRequires:	strace
BuildRequires:	texinfo >= 4.3
BuildRequires:	pkgconfig(libacl)
BuildRequires:	pkgconfig(libattr)
BuildRequires:	pkgconfig(libcap)
BuildRequires:	hostname
BuildRequires:	gettext-devel

%rename		mktemp
Provides:	stat = %{version}
Provides:	%{_bindir}/env
Provides:	/bin/env
Provides:	%{_bindir}/tr
Provides:	/bin/false
Provides:	/bin/true
Obsoletes:	base64 < 9.0
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
%autosetup -N

# will be regenerated in the build directories
rm -f src/fs.h

# will be further modified by coreutils-8.32-DIR_COLORS.patch
sed src/dircolors.hin \
        -e 's| 00;36$| 01;36|' \
        > DIR_COLORS
sed src/dircolors.hin \
        -e 's| 01;31$| 00;31|' \
        -e 's| 01;35$| 00;35|' \
        > DIR_COLORS.lightbgcolor

# apply all patches
%autopatch -p1

(echo ">>> Fixing permissions on tests") 2>/dev/null
find tests -name '*.sh' -perm 0644 -print -exec chmod 0755 '{}' '+'
(echo "<<< done") 2>/dev/null

autoreconf -fiv

%build
export ac_cv_func_lchmod="no"

%configure \
	--enable-largefile \
	--enable-no-install-program=hostname,uptime,kill \
	--enable-install-program=arch \
	--without-selinux \
	--with-packager="%{packager}" \
	--with-packager-version="%{version}-%{release}" \
	--with-packager-bug-reports="%{bugurl}" \
	--enable-single-binary=symlinks \
	--without-openssl \
	--with-tty-group \
	--enable-systemd \
	DEFAULT_POSIX2_VERSION=200112 alternative=199209

%make_build


%install
%make_install

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -p -c -m644 DIR_COLORS{,.lightbgcolor} %{buildroot}%{_sysconfdir}
install -p -c -m644 %{SOURCE1} %{buildroot}%{_sysconfdir}/profile.d/colorls.sh
install -p -c -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d/colorls.csh

# (tpg) compress these files
xz --text ChangeLog

# Fix conflicts with glibc
rm -rf %{buildroot}%{_datadir}/locale/*/LC_TIME

%find_lang %{name}

%files -f %{name}.lang
%config(noreplace) %{_sysconfdir}/DIR_COLORS*
%config(noreplace) %{_sysconfdir}/profile.d/*
%{_bindir}/*
%dir %{_libexecdir}/coreutils
%{_libexecdir}/coreutils/libstdbuf.so

%files doc
%doc ABOUT-NLS ChangeLog.xz NEWS THANKS TODO README
%{_infodir}/coreutils*
%{_mandir}/man*/*

%post
# FIXME this is a temporary workaround to keep
# /bin/rm hardcodes etc. working during the
# usrmerge transition.
# This has to go as soon as we can be reasonably
# sure /bin is a symlink.
# We can't just package the symlinks as we usually
# would because that will wreak havoc on systems
# where /bin already is a symlink (owning 2 conflicting
# files)
if test -d /bin -a ! -h /bin; then
	sln /usr/bin/coreutils /bin/coreutils
	for i in cat chgrp chmod chown chroot cp cut date echo expr false head id install ln ls mkdir mknod mktemp mv readlink realpath rm rmdir sleep sort stat tail tee test touch tr true uname uniq unlink yes; do
		sln /bin/coreutils /bin/$i
	done
fi

%posttrans
# Needed here again, in case our newly placed (in %%post)
# symlinks were removed again by uninstalling the
# previous version of coreutils
# (which owned those files)
if test -d /bin -a ! -h /bin; then
	sln /usr/bin/coreutils /bin/coreutils
	for i in cat chgrp chmod chown chroot cp cut date echo expr false head id install ln ls mkdir mknod mktemp mv readlink realpath rm rmdir sleep sort stat tail tee test touch tr true uname uniq unlink yes; do
		sln /bin/coreutils /bin/$i
	done
fi
