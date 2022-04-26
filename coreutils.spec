# (tpg) optimize size a bit
%ifnarch riscv64
%global optflags %{optflags} -Oz -fno-strict-aliasing -fpic -Dlint --rtlib=compiler-rt
%endif

# do not make coreutils-single depend on /usr/bin/coreutils
%global __requires_exclude ^%{_bindir}/coreutils$

Summary:	The GNU core utilities: a set of tools commonly used in shell scripts
Name:		coreutils
Version:	9.1
Release:	1
License:	GPLv3+
Group:		System/Base
Url:		http://www.gnu.org/software/coreutils/
Source0:	http://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source1:	coreutils-colorls.sh
Source2:	coreutils-colorls.csh
Patch0:		coreutils-9.0-clang.patch

# Make simple backups in correct dir; broken in 9.1            
Patch1:	gnulib-simple-backup-fix.patch
					
# disable the test-lock gnulib test prone to deadlock
Patch100:	coreutils-8.26-test-lock.patch

# downstream changes to default DIR_COLORS
Patch102:	coreutils-8.32-DIR_COLORS.patch

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
Patch800:	coreutils-i18n.patch

#getgrouplist() patch from Ulrich Drepper.
Patch908:	coreutils-getgrouplist.patch

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
	DEFAULT_POSIX2_VERSION=200112 alternative=199209

%make_build


%install
%make_install

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p %{buildroot}{/bin,%{_bindir},%{_sbindir}}

# chroot was in /usr/sbin :
ln -sf %{_bindir}/coreutils %{buildroot}%{_sbindir}/chroot

# (tpg) keep compat symlinks
for f in $(ls %{buildroot}%{_bindir}); do
    ln -sf %{_bindir}/$f %{buildroot}/bin/$f ;
done

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
/bin/*
%{_bindir}/*
%{_sbindir}/chroot
%dir %{_libexecdir}/coreutils
%{_libexecdir}/coreutils/libstdbuf.so

%files doc
%doc ABOUT-NLS ChangeLog.xz NEWS THANKS TODO README
%{_infodir}/coreutils*
%{_mandir}/man*/*
