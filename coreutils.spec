# for sh-utils :
%define optflags $RPM_OPT_FLAGS -D_GNU_SOURCE=1

Summary: The GNU core utilities: a set of tools commonly used in shell scripts
Name:    coreutils
Version: 6.9
Release: %mkrel 2
License: GPL
Group:   System/Base
Url:     http://www.gnu.org/software/coreutils/

Source0: http://ftp.gnu.org/gnu/%name/%name-%version.tar.bz2
Source200:  su.pamd
Source201:  help2man

# fileutils
Patch101: coreutils-5.93-spacedir.patch
Patch1155: coreutils-6.9-force-option--override--interactive-option.patch
Patch118: fileutils-4.1-ls_h.patch
Patch152: coreutils-4.5.7-touch_errno.patch
Patch500: textutils-2.0.17-mem.patch

# sh-utils
Patch703: coreutils-5.93-dateman.patch
Patch704: sh-utils-1.16-paths.patch
# RMS will never accept the PAM patch because it removes his historical
# rant about Twenex and the wheel group, so we'll continue to maintain
# it here indefinitely.
Patch706: coreutils-6.9-pam.patch
Patch711: sh-utils-2.0.12-hname.patch

# (sb) lin18nux/lsb compliance - normally from here:
# http://www.openi18n.org/subgroups/utildev/patch/
# this one is actually a merger of 5.2 and 5.3, as join segfaults
# compiled with gcc4 and the 5.1/5.2 patch
Patch800: coreutils-6.9-new-i18n.patch
# small pt_BR fix
Patch801: coreutils-5.2.1-ptbrfix.patch

Patch904: coreutils-5.0.91-allow_old_options.patch
Patch909: coreutils-5.1.0-64bit-fixes.patch
Patch910: coreutils-5.2.1-uname.patch

#(peroyvind): adds coloring for lzma compressed files just like for .gz etc.
Patch1010: coreutils-6.9-lzma-ls-coloring.patch
Patch1011: coreutils-6.9-DIR_COLORS-mdkconf.patch
#(fwang): From fedora, fix ls -x
Patch1012: coreutils-6.9-ls-x.patch
#(peroyvind): add back always red blinking on broken symlinks
Patch1013: coreutils-6.9-always-blinking-colors-on-broken-symlinks.patch

BuildRoot: %_tmppath/%{name}-root
BuildRequires:	gettext termcap-devel pam-devel texinfo >= 4.3
BuildRequires:	automake == 1.10
BuildRequires:	libacl-devel libattr-devel
Requires:   pam >= 0.66-12

Provides:	fileutils = %version, sh-utils = %version, stat, textutils = %version
Obsoletes:	fileutils sh-utils stat textutils

Conflicts:  tetex < 1.0.7-49mdk
Obsoletes:  base64

%description
These are the GNU core utilities.  This package is the union of
the old GNU fileutils, sh-utils, and textutils packages.

These tools are the GNU versions of common useful and popular
file & text utilities which are used for:
- file management
- shell scripts
- modifying text file (spliting, joining, comparing, modifying, ...)

Most of these programs have significant advantages over their Unix
counterparts, such as greater speed, additional options, and fewer
arbitrary limits.

The following tools are included:

  base64 basename cat chgrp chmod chown chroot cksum comm cp csplit
  cut cut date dd df dir dircolors dirname du echo env env expand
  expr expr factor false fmt fold groups head hostid id install
  join kill link ln logname ls md5sum mkdir mkfifo mknod mv nice nl
  nohup od paste pathchk pinky pr printenv printf ptx pwd readlink
  rm rmdir seq sha1sum sha224sum sha256sum sha384sum sha512sum
  shred shuf sleep sort split stat stty su sum sync tac tail tee
  test touch tr true tsort tty uname unexpand uniq unlink users
  vdir wc who whoami yes

%package doc
Summary: Coreutils documentation in info format
Group: Books/Computer books
Requires: coreutils >= 4.5.4-2mdk
Requires(pre): /sbin/install-info

%description doc
This package contains coreutils documentation in GNU info format.

%prep
%setup -q

# fileutils
%patch101 -p1 -b .space
%patch1155 -p0 -b .override
%patch118 -p1
%patch152 -p1

# textutils
%patch500 -p1

# sh-utils
%patch703 -p1 -b .dateman
%patch704 -p1 -b .paths
%patch706 -p1 -b .pam

# li18nux/lsb
%patch800 -p1 -b .i18n
%patch801 -p0 -b .ptbr

#%patch904 -p1 -b .old-options
%patch909 -p1 -b .64bit
%patch910 -p0 -b .cpu

%patch1010 -p1 -b .lzma_colors
%patch1011 -p1 -b .colors_mdkconf
%patch1012 -p1 -b .ls-x
%patch1013 -p1 -b .broken_blink

cp %SOURCE201 man/help2man
chmod +x man/help2man

%build
export DEFAULT_POSIX2_VERSION=199209
aclocal-1.10 -I m4
automake-1.10 --gnits --add-missing
autoconf
%configure2_5x --enable-largefile --enable-pam
%make HELP2MAN=$PWD/man/help2man

# XXX docs should say /var/run/[uw]tmp not /etc/[uw]tmp
perl -pi -e 's,/etc/utmp,/var/run/utmp,g;s,/etc/wtmp,/var/run/wtmp,g' doc/coreutils.texi

%check
# Fix the test suite:
chmod a+x tests/sort/sort-mb-tests
chmod a+x tests/ls/x-option
# Run the test suite:
%make check

%install
[[ -f ChangeLog ]] && bzip2 -9f ChangeLog
# for help2man:
export PATH=$PATH:RPM_BUILD_ROOT/man

rm -rf $RPM_BUILD_ROOT
%makeinstall_std

# man pages are not installed with make install
make mandir=$RPM_BUILD_ROOT%{_mandir} install-man

# fix japanese catalog file
if [ -d $RPM_BUILD_ROOT/%{_datadir}/locale/ja_JP.EUC/LC_MESSAGES ]; then
   mkdir -p $RPM_BUILD_ROOT/%{_datadir}/locale/ja/LC_MESSAGES
   mv $RPM_BUILD_ROOT/%{_datadir}/locale/ja_JP.EUC/LC_MESSAGES/*mo \
		$RPM_BUILD_ROOT/%{_datadir}/locale/ja/LC_MESSAGES
   rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale/ja_JP.EUC
fi

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p $RPM_BUILD_ROOT{/bin,%_bindir,%_sbindir,%_sysconfdir/pam.d}
for f in basename cat chgrp chmod chown cp cut date dd df echo env expr false id link ln ls mkdir mknod mv nice pwd rm rmdir sleep sort stat stty sync touch true uname unlink
do
	mv $RPM_BUILD_ROOT/{%_bindir,bin}/$f 
done

ln -sf ../../bin/expr $RPM_BUILD_ROOT%_bindir/

# chroot was in /usr/sbin :
mv $RPM_BUILD_ROOT/{%_bindir,%_sbindir}/chroot
# {cat,sort,cut} were previously moved from bin to /usr/bin and linked into 
for i in env cut; do ln -sf ../../bin/$i $RPM_BUILD_ROOT/usr/bin; done

install -m644 src/dircolors.hin -D %{buildroot}%{_sysconfdir}/DIR_COLORS

# su
install -m 4755 src/su $RPM_BUILD_ROOT/bin

# These come from util-linux and/or procps.
for i in hostname uptime ; do
	rm -f $RPM_BUILD_ROOT{%_bindir/$i,%_mandir/man1/${i}.1}
done

install -m 644 %SOURCE200 $RPM_BUILD_ROOT%_sysconfdir/pam.d/su

bzip2 -9f old/*/C* || :

# fix conflict with util-linux:
rm -f $RPM_BUILD_ROOT%_mandir/man1/kill.1

#TV# find_lang look for LC_MESSAGES, not LC_TIME:
#TV(cd $RPM_BUILD_ROOT; find .%_datadir/locale/ -name coreutils.mo | fgrep LC_TIME | \
#TV	sed -e "s!^.*/share/locale/\([^/]*\)/!%lang(\1) %_datadir/locale/\1/!") >> %name.lang
find $RPM_BUILD_ROOT%_datadir/locale/ -name coreutils.mo | fgrep LC_TIME | xargs rm -f

%find_lang %name

# (sb) Deal with Installed (but unpackaged) file(s) found
rm -f $RPM_BUILD_ROOT%{_datadir}/info/dir

%clean
rm -rf $RPM_BUILD_ROOT

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
%doc README
/bin/*
%_bindir/*
%_sbindir/chroot

%files doc
%defattr(-,root,root)
%doc ABOUT-NLS ChangeLog.bz2 NEWS THANKS TODO old/*
%_infodir/coreutils*
%_mandir/man*/*
