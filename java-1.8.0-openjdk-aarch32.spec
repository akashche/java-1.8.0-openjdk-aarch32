# note, parametrised macros are order-senisitve (unlike not-parametrized) even with normal macros
# also necessary when passing it as parameter other macros. If not macro, then it is considered as switch
%global debug_suffix_unquoted -debug
# quoted one for shell operations
%global debug_suffix "%{debug_suffix_unquoted}"
%global normal_suffix ""

#if you wont only debug build, but providing java, build only normal build, but  set normalbuild_parameter
%global debugbuild_parameter  slowdebug
%global normalbuild_parameter release
%global debug_warning This package have full debug on. Install only in need, and remove asap.
%global debug_on with full debug on
%global for_debug for packages with debug on

# by default we build normal build always.
%global include_normal_build 1
%if %{include_normal_build}
%global build_loop1 %{normal_suffix}
%else
%global build_loop1 %{nil}
%endif

%global aarch64         aarch64 arm64 armv8
# sometimes we need to distinguish big and little endian PPC64
%global ppc64le         ppc64le
%global ppc64be         ppc64 ppc64p7
%global multilib_arches %{power64} sparc64 x86_64
%global jit_arches      %{ix86} x86_64 sparcv9 sparc64 %{aarch64} %{power64} %{arm}

# By default, we build a debug build during main build on JIT architectures
# do not ever sync {arm}  to main packages, unles whole this package is merged.
%ifarch %{jit_arches}
%global include_debug_build 1
%else
%global include_debug_build 0
%endif

# On x86_64 and AArch64, we use the Shenandoah HotSpot
%ifarch x86_64 %{aarch64}
%global use_shenandoah_hotspot 1
%else
%global use_shenandoah_hotspot 0
%endif

%if %{include_debug_build}
%global build_loop2 %{debug_suffix}
%else
%global build_loop2 %{nil}
%endif

# if you disable both builds, then build fails
%global build_loop  %{build_loop1} %{build_loop2}
# note, that order  normal_suffix debug_suffix, in case of both enabled,
# is expected in one single case at the end of build
%global rev_build_loop  %{build_loop2} %{build_loop1}

%ifarch %{jit_arches}
%global bootstrap_build 1
%else
%global bootstrap_build 1
%endif

%if %{bootstrap_build}
%global targets bootcycle-images docs
%else
%global targets all
%endif

%ifnarch %{jit_arches}
# Disable hardened build on non-jit arches. Work-around for RHBZ#1290936.
%undefine _hardened_build
%global ourcppflags %{nil}
%global ourldflags %{nil}
%else
%ifarch %{aarch64}
# Disable hardened build on AArch64 as it didn't bootcycle
%undefine _hardened_build
%global ourcppflags "-fstack-protector-strong"
%global ourldflags %{nil}
%else
# Filter out flags from the optflags macro that cause problems with the OpenJDK build
# We filter out -O flags so that the optimisation of HotSpot is not lowered from O3 to O2
# We filter out -Wall which will otherwise cause HotSpot to produce hundreds of thousands of warnings (100+mb logs)
# We replace it with -Wformat (required by -Werror=format-security) and -Wno-cpp to avoid FORTIFY_SOURCE warnings
# We filter out -fexceptions as the HotSpot build explicitly does -fno-exceptions and it's otherwise the default for C++
%global ourflags %(echo %optflags | sed -e 's|-Wall|-Wformat -Wno-cpp|' | sed -r -e 's|-O[0-9]*||')
%global ourcppflags %(echo %ourflags | sed -e 's|-fexceptions||')
%global ourldflags %{__global_ldflags}
%endif
%endif
%ifarch %{arm}
# Disable hardened build on aarch32. Work-around for RHBZ#1290936.
%undefine _hardened_build
%global ourcppflags %{nil}
%global ourldflags %{nil}
%endif

# With diabled nss is NSS deactivated, so in NSS_LIBDIR can be wrong path
# the initialisation must be here. LAter the pkg-connfig have bugy behaviour
#looks liekopenjdk RPM specific bug
# Always set this so the nss.cfg file is not broken
%global NSS_LIBDIR %(pkg-config --variable=libdir nss)
%global NSS_LIBS %(pkg-config --libs nss)
%global NSS_CFLAGS %(pkg-config --cflags nss-softokn)
# see https://bugzilla.redhat.com/show_bug.cgi?id=1332456
%global NSSSOFTOKN_BUILDTIME_NUMBER %(pkg-config --modversion nss-softokn || : )
%global NSS_BUILDTIME_NUMBER %(pkg-config --modversion nss || : )
#this is worakround for processing of requires during srpm creation
%global NSSSOFTOKN_BUILDTIME_VERSION %(if [ "x%{NSSSOFTOKN_BUILDTIME_NUMBER}" == "x" ] ; then echo "" ;else echo ">= %{NSSSOFTOKN_BUILDTIME_NUMBER}" ;fi)
%global NSS_BUILDTIME_VERSION %(if [ "x%{NSS_BUILDTIME_NUMBER}" == "x" ] ; then echo "" ;else echo ">= %{NSS_BUILDTIME_NUMBER}" ;fi)


# fix for https://bugzilla.redhat.com/show_bug.cgi?id=1111349
%global _privatelibs libmawt[.]so.*
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$

# In some cases, the arch used by the JDK does
# not match _arch.
# Also, in some cases, the machine name used by SystemTap
# does not match that given by _build_cpu
%ifarch x86_64
%global archinstall amd64
%global stapinstall x86_64
%endif
%ifarch ppc
%global archinstall ppc
%global stapinstall powerpc
%endif
%ifarch %{ppc64be}
%global archinstall ppc64
%global stapinstall powerpc
%endif
%ifarch %{ppc64le}
%global archinstall ppc64le
%global stapinstall powerpc
%endif
%ifarch %{ix86}
%global archinstall i386
%global stapinstall i386
%endif
%ifarch ia64
%global archinstall ia64
%global stapinstall ia64
%endif
%ifarch s390
%global archinstall s390
%global stapinstall s390
%endif
%ifarch s390x
%global archinstall s390x
%global stapinstall s390
%endif
%ifarch %{arm}
%global archinstall arm
%global stapinstall arm
%endif
%ifarch %{aarch64}
%global archinstall aarch64
%global stapinstall arm64
%endif
# 32 bit sparc, optimized for v9
%ifarch sparcv9
%global archinstall sparc
%global stapinstall %{_build_cpu}
%endif
# 64 bit sparc
%ifarch sparc64
%global archinstall sparcv9
%global stapinstall %{_build_cpu}
%endif
%ifnarch %{jit_arches}
%global archinstall %{_arch}
%endif

%ifarch %{jit_arches}
%global with_systemtap 0
%else
%global with_systemtap 0
%endif

%ifarch %{ix86} x86_64
%global with_openjfx_binding 0
%global openjfx_path %{_jvmdir}/openjfx
# links src directories
%global jfx_jre_libs_dir %{openjfx_path}/rt/lib
%global jfx_jre_native_dir %{jfx_jre_libs_dir}/%{archinstall}
%global jfx_sdk_libs_dir %{openjfx_path}/lib
%global jfx_sdk_bins_dir %{openjfx_path}/bin
%global jfx_jre_exts_dir %{jfx_jre_libs_dir}/ext
# links src files
# maybe depend on jfx and generate the lists in build time? Yes, bad idea to inlcude cyclic depndenci, but this list is aweful
%global jfx_jre_libs jfxswt.jar javafx.properties
%global jfx_jre_native libprism_es2.so libprism_common.so libjavafx_font.so libdecora_sse.so libjavafx_font_freetype.so libprism_sw.so libjavafx_font_pango.so libglass.so libjavafx_iio.so
%global jfx_sdk_libs javafx-mx.jar packager.jar ant-javafx.jar
%global jfx_sdk_bins javafxpackager javapackager
%global jfx_jre_exts jfxrt.jar
%else
%global with_openjfx_binding 0
%endif

# Convert an absolute path to a relative path.  Each symbolic link is
# specified relative to the directory in which it is installed so that
# it will resolve properly within chrooted installations.
%global script 'use File::Spec; print File::Spec->abs2rel($ARGV[0], $ARGV[1])'
%global abs2rel %{__perl} -e %{script}


# Standard JPackage naming and versioning defines.
%global origin          openjdk
# note, following three variables are sedded from update_sources if used correctly. Hardcode them rather there.
%global project         aarch32-port
%global repo            jdk8u
%global revision        jdk8u144-b01-aarch32-170809
# eg # jdk8u60-b27 -> jdk8u60 or # aarch64-jdk8u60-b27 -> aarch64-jdk8u60  (dont forget spec escape % by %%)
%global whole_update    %(VERSION=%{revision}; echo ${VERSION%%-*})
# eg  jdk8u60 -> 60 or aarch64-jdk8u60 -> 60
%global updatever       %(VERSION=%{whole_update}; echo ${VERSION##*u} | sed s/-.*//)
# eg jdk8u60-b27 -> b27
%global buildver        %(VERSION=%{revision}; echo ${VERSION##*-})
# priority must be 7 digits in total. The expression is workarounding tip
%global priority        %(TIP=1800%{updatever};  echo ${TIP/tip/999})

%global javaver         1.8.0

# parametrized macros are order-sensitive
%global fullversion     %{name}-%{version}-%{release}
#images stub
%global j2sdkimage       j2sdk-image
# output dir stub
%define buildoutputdir() %{expand:openjdk/build/jdk8.build%{?1}}
#we can copy the javadoc to not arched dir, or made it not noarch
%define uniquejavadocdir()    %{expand:%{fullversion}%{?1}}
#main id and dir of this jdk
%define uniquesuffix()        %{expand:%{fullversion}.%{_arch}%{?1}}

# Standard JPackage directories and symbolic links.
%define sdkdir()        %{expand:%{uniquesuffix -- %{?1}}}
%define jrelnk()        %{expand:jre-%{javaver}-%{origin}-%{version}-%{release}.%{_arch}%{?1}}

%define jredir()        %{expand:%{sdkdir -- %{?1}}/jre}
%define sdkbindir()     %{expand:%{_jvmdir}/%{sdkdir -- %{?1}}/bin}
%define jrebindir()     %{expand:%{_jvmdir}/%{jredir -- %{?1}}/bin}

%global rpm_state_dir %{_localstatedir}/lib/rpm-state/

%if %{with_systemtap}
# Where to install systemtap tapset (links)
# We would like these to be in a package specific subdir,
# but currently systemtap doesn't support that, so we have to
# use the root tapset dir for now. To distinquish between 64
# and 32 bit architectures we place the tapsets under the arch
# specific dir (note that systemtap will only pickup the tapset
# for the primary arch for now). Systemtap uses the machine name
# aka build_cpu as architecture specific directory name.
%global tapsetroot /usr/share/systemtap
%global tapsetdir %{tapsetroot}/tapset/%{stapinstall}
%endif

# not-duplicated scriplets for normal/debug packages
%global update_desktop_icons /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%define post_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
exit 0
}


%define post_headless() %{expand:
%ifarch %{jit_arches}
# MetaspaceShared::generate_vtable_methods not implemented for PPC JIT
%ifnarch %{power64}
%ifnarch %{arm}
#see https://bugzilla.redhat.com/show_bug.cgi?id=513605
%{jrebindir -- %{?1}}/java -Xshare:dump >/dev/null 2>/dev/null
%endif
%endif
%endif

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

ext=.gz
alternatives \\
  --install %{_bindir}/java java %{jrebindir -- %{?1}}/java $PRIORITY  --family %{name}.%{_arch} \\
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{jredir -- %{?1}} \\
  --slave %{_bindir}/jjs jjs %{jrebindir -- %{?1}}/jjs \\
  --slave %{_bindir}/keytool keytool %{jrebindir -- %{?1}}/keytool \\
  --slave %{_bindir}/orbd orbd %{jrebindir -- %{?1}}/orbd \\
  --slave %{_bindir}/pack200 pack200 %{jrebindir -- %{?1}}/pack200 \\
  --slave %{_bindir}/rmid rmid %{jrebindir -- %{?1}}/rmid \\
  --slave %{_bindir}/rmiregistry rmiregistry %{jrebindir -- %{?1}}/rmiregistry \\
  --slave %{_bindir}/servertool servertool %{jrebindir -- %{?1}}/servertool \\
  --slave %{_bindir}/tnameserv tnameserv %{jrebindir -- %{?1}}/tnameserv \\
  --slave %{_bindir}/policytool policytool %{jrebindir -- %{?1}}/policytool \\
  --slave %{_bindir}/unpack200 unpack200 %{jrebindir -- %{?1}}/unpack200 \\
  --slave %{_mandir}/man1/java.1$ext java.1$ext \\
  %{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jjs.1$ext jjs.1$ext \\
  %{_mandir}/man1/jjs-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/keytool.1$ext keytool.1$ext \\
  %{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/orbd.1$ext orbd.1$ext \\
  %{_mandir}/man1/orbd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/pack200.1$ext pack200.1$ext \\
  %{_mandir}/man1/pack200-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/rmid.1$ext rmid.1$ext \\
  %{_mandir}/man1/rmid-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/rmiregistry.1$ext rmiregistry.1$ext \\
  %{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/servertool.1$ext servertool.1$ext \\
  %{_mandir}/man1/servertool-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/tnameserv.1$ext tnameserv.1$ext \\
  %{_mandir}/man1/tnameserv-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/policytool.1$ext policytool.1$ext \\
  %{_mandir}/man1/policytool-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/unpack200.1$ext unpack200.1$ext \\
  %{_mandir}/man1/unpack200-%{uniquesuffix -- %{?1}}.1$ext

for X in %{origin} %{javaver} ; do
  alternatives --install %{_jvmdir}/jre-"$X" jre_"$X" %{_jvmdir}/%{jredir -- %{?1}} $PRIORITY --family %{name}.%{_arch}
done

update-alternatives --install %{_jvmdir}/jre-%{javaver}-%{origin} jre_%{javaver}_%{origin} %{_jvmdir}/%{jrelnk -- %{?1}} $PRIORITY  --family %{name}.%{_arch}


update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

# see pretrans where this file is declared
# also see that pretrans is only for nondebug
if [ ! "%{?1}" == %{debug_suffix} ]; then
  if [ -f %{_libexecdir}/copy_jdk_configs_fixFiles.sh ] ; then
    sh  %{_libexecdir}/copy_jdk_configs_fixFiles.sh %{rpm_state_dir}/%{name}.%{_arch}  %{_jvmdir}/%{sdkdir -- %{?1}}
  fi
fi

exit 0
}

%define postun_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
exit 0
}


%define postun_headless() %{expand:
  alternatives --remove java %{jrebindir -- %{?1}}/java
  alternatives --remove jre_%{origin} %{_jvmdir}/%{jredir -- %{?1}}
  alternatives --remove jre_%{javaver} %{_jvmdir}/%{jredir -- %{?1}}
  alternatives --remove jre_%{javaver}_%{origin} %{_jvmdir}/%{jrelnk -- %{?1}}
}

%define posttrans_script() %{expand:
%{update_desktop_icons}
}

%define post_devel() %{expand:

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

ext=.gz
alternatives \\
  --install %{_bindir}/javac javac %{sdkbindir -- %{?1}}/javac $PRIORITY  --family %{name}.%{_arch} \\
  --slave %{_jvmdir}/java java_sdk %{_jvmdir}/%{sdkdir -- %{?1}} \\
  --slave %{_bindir}/appletviewer appletviewer %{sdkbindir -- %{?1}}/appletviewer \\
  --slave %{_bindir}/extcheck extcheck %{sdkbindir -- %{?1}}/extcheck \\
  --slave %{_bindir}/idlj idlj %{sdkbindir -- %{?1}}/idlj \\
  --slave %{_bindir}/jar jar %{sdkbindir -- %{?1}}/jar \\
  --slave %{_bindir}/jarsigner jarsigner %{sdkbindir -- %{?1}}/jarsigner \\
  --slave %{_bindir}/javadoc javadoc %{sdkbindir -- %{?1}}/javadoc \\
  --slave %{_bindir}/javah javah %{sdkbindir -- %{?1}}/javah \\
  --slave %{_bindir}/javap javap %{sdkbindir -- %{?1}}/javap \\
  --slave %{_bindir}/jcmd jcmd %{sdkbindir -- %{?1}}/jcmd \\
  --slave %{_bindir}/jconsole jconsole %{sdkbindir -- %{?1}}/jconsole \\
  --slave %{_bindir}/jdb jdb %{sdkbindir -- %{?1}}/jdb \\
  --slave %{_bindir}/jdeps jdeps %{sdkbindir -- %{?1}}/jdeps \\
  --slave %{_bindir}/jhat jhat %{sdkbindir -- %{?1}}/jhat \\
  --slave %{_bindir}/jinfo jinfo %{sdkbindir -- %{?1}}/jinfo \\
  --slave %{_bindir}/jmap jmap %{sdkbindir -- %{?1}}/jmap \\
  --slave %{_bindir}/jps jps %{sdkbindir -- %{?1}}/jps \\
  --slave %{_bindir}/jrunscript jrunscript %{sdkbindir -- %{?1}}/jrunscript \\
  --slave %{_bindir}/jsadebugd jsadebugd %{sdkbindir -- %{?1}}/jsadebugd \\
  --slave %{_bindir}/jstack jstack %{sdkbindir -- %{?1}}/jstack \\
  --slave %{_bindir}/jstat jstat %{sdkbindir -- %{?1}}/jstat \\
  --slave %{_bindir}/jstatd jstatd %{sdkbindir -- %{?1}}/jstatd \\
  --slave %{_bindir}/native2ascii native2ascii %{sdkbindir -- %{?1}}/native2ascii \\
  --slave %{_bindir}/rmic rmic %{sdkbindir -- %{?1}}/rmic \\
  --slave %{_bindir}/schemagen schemagen %{sdkbindir -- %{?1}}/schemagen \\
  --slave %{_bindir}/serialver serialver %{sdkbindir -- %{?1}}/serialver \\
  --slave %{_bindir}/wsgen wsgen %{sdkbindir -- %{?1}}/wsgen \\
  --slave %{_bindir}/wsimport wsimport %{sdkbindir -- %{?1}}/wsimport \\
  --slave %{_bindir}/xjc xjc %{sdkbindir -- %{?1}}/xjc \\
  --slave %{_mandir}/man1/appletviewer.1$ext appletviewer.1$ext \\
  %{_mandir}/man1/appletviewer-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/extcheck.1$ext extcheck.1$ext \\
  %{_mandir}/man1/extcheck-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/idlj.1$ext idlj.1$ext \\
  %{_mandir}/man1/idlj-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jar.1$ext jar.1$ext \\
  %{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jarsigner.1$ext jarsigner.1$ext \\
  %{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javac.1$ext javac.1$ext \\
  %{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javadoc.1$ext javadoc.1$ext \\
  %{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javah.1$ext javah.1$ext \\
  %{_mandir}/man1/javah-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javap.1$ext javap.1$ext \\
  %{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jcmd.1$ext jcmd.1$ext \\
  %{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jconsole.1$ext jconsole.1$ext \\
  %{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jdb.1$ext jdb.1$ext \\
  %{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jdeps.1$ext jdeps.1$ext \\
  %{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jhat.1$ext jhat.1$ext \\
  %{_mandir}/man1/jhat-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jinfo.1$ext jinfo.1$ext \\
  %{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jmap.1$ext jmap.1$ext \\
  %{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jps.1$ext jps.1$ext \\
  %{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jrunscript.1$ext jrunscript.1$ext \\
  %{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jsadebugd.1$ext jsadebugd.1$ext \\
  %{_mandir}/man1/jsadebugd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstack.1$ext jstack.1$ext \\
  %{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstat.1$ext jstat.1$ext \\
  %{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstatd.1$ext jstatd.1$ext \\
  %{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/native2ascii.1$ext native2ascii.1$ext \\
  %{_mandir}/man1/native2ascii-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/rmic.1$ext rmic.1$ext \\
  %{_mandir}/man1/rmic-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/schemagen.1$ext schemagen.1$ext \\
  %{_mandir}/man1/schemagen-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/serialver.1$ext serialver.1$ext \\
  %{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/wsgen.1$ext wsgen.1$ext \\
  %{_mandir}/man1/wsgen-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/wsimport.1$ext wsimport.1$ext \\
  %{_mandir}/man1/wsimport-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/xjc.1$ext xjc.1$ext \\
  %{_mandir}/man1/xjc-%{uniquesuffix -- %{?1}}.1$ext

for X in %{origin} %{javaver} ; do
  alternatives \\
    --install %{_jvmdir}/java-"$X" java_sdk_"$X" %{_jvmdir}/%{sdkdir -- %{?1}} $PRIORITY  --family %{name}.%{_arch}
done

update-alternatives --install %{_jvmdir}/java-%{javaver}-%{origin} java_sdk_%{javaver}_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} $PRIORITY  --family %{name}.%{_arch} \\

update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

exit 0
}

%define postun_devel() %{expand:
  alternatives --remove javac %{sdkbindir -- %{?1}}/javac
  alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}}
  alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}}
  alternatives --remove java_sdk_%{javaver}_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}}

update-desktop-database %{_datadir}/applications &> /dev/null || :

if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
exit 0
}

%define posttrans_devel() %{expand:
%{update_desktop_icons}
}

%define post_javadoc() %{expand:

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

alternatives \\
  --install %{_javadocdir}/java javadocdir %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api \\
  $PRIORITY  --family %{name}
exit 0
}

%define postun_javadoc() %{expand:
  alternatives --remove javadocdir %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api
exit 0
}

%define post_javadoc_zip() %{expand:

PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

alternatives \\
  --install %{_javadocdir}/java-zip javadoczip %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip \\
  $PRIORITY  --family %{name}
exit 0
}

%define postun_javadoc_zip() %{expand:
  alternatives --remove javadoczip %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
exit 0
}

%define files_jre() %{expand:
%{_datadir}/icons/hicolor/*x*/apps/java-%{javaver}.png
%{_datadir}/applications/*policytool%{?1}.desktop
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libjsoundalsa.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libsplashscreen.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libawt_xawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/%{archinstall}/libjawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/aarch32/libjsoundalsa.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/aarch32/libsplashscreen.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/aarch32/libawt_xawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/lib/aarch32/libjawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/jre/bin/policytool
}


%define files_jre_headless() %{expand:
%defattr(-,root,root,-)
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/jre/ASSEMBLY_EXCEPTION
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/jre/LICENSE
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/jre/THIRD_PARTY_README
%dir %{_jvmdir}/%{sdkdir -- %{?1}}
%{_jvmdir}/%{jrelnk -- %{?1}}
%{_jvmprivdir}/*
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/security
%{_jvmdir}/%{jredir -- %{?1}}/lib/security/cacerts
%dir %{_jvmdir}/%{jredir -- %{?1}}
%dir %{_jvmdir}/%{jredir -- %{?1}}/bin
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib
%{_jvmdir}/%{jredir -- %{?1}}/bin/java
%{_jvmdir}/%{jredir -- %{?1}}/bin/jjs
%{_jvmdir}/%{jredir -- %{?1}}/bin/keytool
%{_jvmdir}/%{jredir -- %{?1}}/bin/orbd
%{_jvmdir}/%{jredir -- %{?1}}/bin/pack200
%{_jvmdir}/%{jredir -- %{?1}}/bin/rmid
%{_jvmdir}/%{jredir -- %{?1}}/bin/rmiregistry
%{_jvmdir}/%{jredir -- %{?1}}/bin/servertool
%{_jvmdir}/%{jredir -- %{?1}}/bin/tnameserv
%{_jvmdir}/%{jredir -- %{?1}}/bin/unpack200
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/US_export_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/local_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/java.policy
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/java.security
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/blacklisted.certs
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/logging.properties
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/calendars.properties
%{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jjs-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/orbd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/pack200-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmid-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/servertool-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/tnameserv-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/unpack200-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/policytool-%{uniquesuffix -- %{?1}}.1*
%config(noreplace) %{_jvmdir}/%{jredir -- %{?1}}/lib/security/nss.cfg
%ifarch %{jit_arches}
%ifnarch %{power64}
%attr(664, root, root) %ghost %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/server/classes.jsa
%attr(664, root, root) %ghost %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/client/classes.jsa
%endif
%endif
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/server/
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/client/
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/jli
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/jli/libjli.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/jvm.cfg
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libattach.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libawt.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libawt_headless.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libdt_socket.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libfontmanager.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libhprof.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libinstrument.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libj2gss.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libj2pcsc.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libj2pkcs11.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjaas_unix.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjava.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjava_crw_demo.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjavajpeg.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjdwp.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjsdt.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjsig.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libjsound.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/liblcms.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libmanagement.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libmlib_image.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libnet.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libnio.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libnpt.so
%ifarch x86_64  %{ix86} %{aarch64}
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libsaproc.so
%endif
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libsctp.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libsunec.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libunpack.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libverify.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libzip.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/client/
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/jli
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/jli/libjli.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/jvm.cfg
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libattach.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libawt.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libawt_headless.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libdt_socket.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libfontmanager.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libhprof.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libinstrument.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libj2gss.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libj2pcsc.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libj2pkcs11.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjaas_unix.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjava.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjava_crw_demo.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjavajpeg.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjdwp.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjsdt.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjsig.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libjsound.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/liblcms.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libmanagement.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libmlib_image.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libnet.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libnio.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libnpt.so
%ifarch x86_64  %{ix86} %{aarch64}
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libsaproc.so
%endif
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libsctp.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libsunec.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libunpack.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libverify.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libzip.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/charsets.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/classlist
%{_jvmdir}/%{jredir -- %{?1}}/lib/content-types.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/currency.data
%{_jvmdir}/%{jredir -- %{?1}}/lib/flavormap.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/hijrah-config-umalqura.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/images/cursors/*
%{_jvmdir}/%{jredir -- %{?1}}/lib/jce.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/jexec
%{_jvmdir}/%{jredir -- %{?1}}/lib/jsse.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/jvm.hprof.txt
%{_jvmdir}/%{jredir -- %{?1}}/lib/meta-index
%{_jvmdir}/%{jredir -- %{?1}}/lib/net.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/psfont.properties.ja
%{_jvmdir}/%{jredir -- %{?1}}/lib/psfontj2d.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/resources.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/rt.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/sound.properties
%{_jvmdir}/%{jredir -- %{?1}}/lib/tzdb.dat
%{_jvmdir}/%{jredir -- %{?1}}/lib/management-agent.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/management/*
%{_jvmdir}/%{jredir -- %{?1}}/lib/cmm/*
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/*
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/images
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/images/cursors
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/management
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/cmm
%dir %{_jvmdir}/%{jredir -- %{?1}}/lib/ext
}

%define files_devel() %{expand:
%defattr(-,root,root,-)
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/ASSEMBLY_EXCEPTION
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/LICENSE
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/THIRD_PARTY_README
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/bin
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/include
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/appletviewer
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/extcheck
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/idlj
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jar
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jarsigner
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/java
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javac
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javadoc
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javah
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/java-rmi.cgi
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jcmd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jconsole
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdb
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdeps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jhat
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jinfo
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jjs
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jmap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jrunscript
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jsadebugd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstack
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstat
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstatd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/keytool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/native2ascii
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/orbd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/pack200
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/policytool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmic
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmid
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmiregistry
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/schemagen
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/serialver
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/servertool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/tnameserv
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/unpack200
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/wsgen
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/wsimport
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/xjc
%{_jvmdir}/%{sdkdir -- %{?1}}/include/*
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{archinstall}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/aarch32
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/ct.sym
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/ir.idl
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jconsole.jar
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/orb.idl
%ifarch x86_64  %{ix86}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/sa-jdi.jar
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/dt.jar
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jexec
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/tools.jar
%{_datadir}/applications/*jconsole%{?1}.desktop
%{_mandir}/man1/appletviewer-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/extcheck-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/idlj-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javah-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jhat-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jsadebugd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/native2ascii-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmic-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/schemagen-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/wsgen-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/wsimport-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/xjc-%{uniquesuffix -- %{?1}}.1*
%if %{with_systemtap}
%dir %{tapsetroot}
%dir %{tapsetdir}
%{tapsetdir}/*%{version}-%{release}.%{_arch}%{?1}.stp
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/tapset
%{_jvmdir}/%{sdkdir -- %{?1}}/tapset/*.stp
%endif
}

%define files_demo() %{expand:
%defattr(-,root,root,-)
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/jre/LICENSE
}

%define files_src() %{expand:
%defattr(-,root,root,-)
%doc README.src
%{_jvmdir}/%{sdkdir -- %{?1}}/src.zip
}

%define files_javadoc() %{expand:
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/jre/LICENSE
}

%define files_javadoc_zip() %{expand:
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
%license %{buildoutputdir -- %{?1}}/images/%{j2sdkimage}/jre/LICENSE
}

%define files_accessibility() %{expand:
%{_jvmdir}/%{jredir -- %{?1}}/lib/%{archinstall}/libatk-wrapper.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/aarch32/libatk-wrapper.so
%{_jvmdir}/%{jredir -- %{?1}}/lib/ext/java-atk-wrapper.jar
%{_jvmdir}/%{jredir -- %{?1}}/lib/accessibility.properties
}

# not-duplicated requires/provides/obsolate for normal/debug packages
%define java_rpo() %{expand:
Requires: fontconfig%{?_isa}
Requires: xorg-x11-fonts-Type1

# Requires rest of java
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}


# Standard JPackage base provides.
#Provides: jre-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}
#Provides: jre-%{origin}%{?1} = %{epoch}:%{version}-%{release}
#Provides: jre-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
#Provides: java-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
#Provides: jre = %{javaver}%{?1}
#Provides: java-%{origin}%{?1} = %{epoch}:%{version}-%{release}
#Provides: java%{?1} = %{epoch}:%{javaver}
# Standard JPackage extensions provides.
#Provides: java-fonts%{?1} = %{epoch}:%{version}

Obsoletes: java-1.7.0-openjdk%{?1}
Obsoletes: java-1.5.0-gcj%{?1}
Obsoletes: sinjdoc
}

%define java_headless_rpo() %{expand:
# Require /etc/pki/java/cacerts.
Requires: ca-certificates
# Require javapackages-tools for ownership of /usr/lib/jvm/
Requires: javapackages-tools
# Require zoneinfo data provided by tzdata-java subpackage.
Requires: tzdata-java >= 2015d
# libsctp.so.1 is being `dlopen`ed on demand
Requires: lksctp-tools%{?_isa}
# there is a need to depend on the exact version of NSS
Requires: nss%{?_isa} %{NSS_BUILDTIME_VERSION}
Requires: nss-softokn%{?_isa} %{NSSSOFTOKN_BUILDTIME_VERSION}
# tool to copy jdk's configs - should be Recommends only, but then only dnf/yum eforce it, not rpm transaction and so no configs are persisted when pure rpm -u is run. I t may be consiedered as regression
Requires:	copy-jdk-configs >= 2.2
OrderWithRequires: copy-jdk-configs
# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(post):   chkconfig >= 1.7
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(postun):   chkconfig >= 1.7

# Standard JPackage base provides.
#Provides: jre-%{javaver}-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
#Provides: jre-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
#Provides: jre-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
#Provides: java-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
#Provides: jre-headless%{?1} = %{epoch}:%{javaver}
#Provides: java-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
#Provides: java-headless%{?1} = %{epoch}:%{javaver}
# Standard JPackage extensions provides.
#Provides: jndi%{?1} = %{epoch}:%{version}
#Provides: jndi-ldap%{?1} = %{epoch}:%{version}
#Provides: jndi-cos%{?1} = %{epoch}:%{version}
#Provides: jndi-rmi%{?1} = %{epoch}:%{version}
#Provides: jndi-dns%{?1} = %{epoch}:%{version}
#Provides: jaas%{?1} = %{epoch}:%{version}
#Provides: jsse%{?1} = %{epoch}:%{version}
#Provides: jce%{?1} = %{epoch}:%{version}
#Provides: jdbc-stdext%{?1} = 4.1
#Provides: java-sasl%{?1} = %{epoch}:%{version}

#https://bugzilla.redhat.com/show_bug.cgi?id=1312019
#Provides: /usr/bin/jjs

Obsoletes: java-1.7.0-openjdk-headless%{?1}
}

%define java_devel_rpo() %{expand:
# Require base package.
Requires:         %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(post):   chkconfig >= 1.7
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(postun):   chkconfig >= 1.7

# Standard JPackage devel provides.
#Provides: java-sdk-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}
#Provides: java-sdk-%{javaver}%{?1} = %{epoch}:%{version}
#Provides: java-sdk-%{origin}%{?1} = %{epoch}:%{version}
#Provides: java-sdk%{?1} = %{epoch}:%{javaver}
#Provides: java-%{javaver}-devel%{?1} = %{epoch}:%{version}
#Provides: java-devel-%{origin}%{?1} = %{epoch}:%{version}
#Provides: java-devel%{?1} = %{epoch}:%{javaver}

Obsoletes: java-1.7.0-openjdk-devel%{?1}
Obsoletes: java-1.5.0-gcj-devel%{?1}
}


%define java_demo_rpo() %{expand:
Requires: %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

#Provides: java-%{javaver}-%{origin}-demo = %{epoch}:%{version}-%{release}

Obsoletes: java-1.7.0-openjdk-demo%{?1}
}

%define java_javadoc_rpo() %{expand:
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install javadoc alternative.
Requires(post):   %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(post):   chkconfig >= 1.7
# Postun requires alternatives to uninstall javadoc alternative.
Requires(postun): %{_sbindir}/alternatives
# in version 1.7 and higher for --family switch
Requires(postun):   chkconfig >= 1.7

# Standard JPackage javadoc provides.
#Provides: java-javadoc%{?1} = %{epoch}:%{version}-%{release}
#Provides: java-%{javaver}-javadoc%{?1} = %{epoch}:%{version}-%{release}
#Provides: java-%{javaver}-%{origin}-javadoc = %{epoch}:%{version}-%{release}

Obsoletes: java-1.7.0-openjdk-javadoc%{?1}

}

%define java_src_rpo() %{expand:
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

# Standard JPackage javadoc provides.
#Provides: java-src%{?1} = %{epoch}:%{version}-%{release}
#Provides: java-%{javaver}-src%{?1} = %{epoch}:%{version}-%{release}
#Provides: java-%{javaver}-%{origin}-src = %{epoch}:%{version}-%{release}
Obsoletes: java-1.7.0-openjdk-src%{?1}
}

%define java_accessibility_rpo() %{expand:
Requires: java-atk-wrapper%{?_isa}
Requires: %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

#Provides: java-%{javaver}-%{origin}-accessibility = %{epoch}:%{version}-%{release}

Obsoletes: java-1.7.0-openjdk-accessibility%{?1}
}

# Prevent brp-java-repack-jars from being run.
%global __jar_repack 0

Name:    java-%{javaver}-%{origin}-aarch32
Version: %{javaver}.%{updatever}
Release: 2.%{buildver}%{?dist}
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons,
# and this change was brought into RHEL-4.  java-1.5.0-ibm packages
# also included the epoch in their virtual provides.  This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0".  In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0.  So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages.  Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".

Epoch:   1
Summary: OpenJDK Runtime Environment in a preview of the OpenJDK AArch32 project
Group:   Development/Languages

License:  ASL 1.1 and ASL 2.0 and GPL+ and GPLv2 and GPLv2 with exceptions and LGPL+ and LGPLv2 and MPLv1.0 and MPLv1.1 and Public Domain and W3C
URL:      http://openjdk.java.net/

# aarch64-port now contains integration forest of both aarch64 and normal jdk
# Source from upstream OpenJDK8 project. To regenerate, use
# VERSION=%%{revision} FILE_NAME_ROOT=%%{project}-%%{repo}-${VERSION}
# REPO_ROOT=<path to checked-out repository> generate_source_tarball.sh
# where the source is obtained from http://hg.openjdk.java.net/%%{project}/%%{repo}
Source0: %{project}-%{repo}-%{revision}.tar.xz

# Shenandoah HotSpot
#Source1: aarch64-port-jdk8u-shenandoah-aarch64-shenandoah-jdk8u141-b16.tar.xz

# Custom README for -src subpackage
Source2:  README.src

# Use 'generate_tarballs.sh' to generate the following tarballs
# They are based on code contained in the IcedTea7 project.

# Systemtap tapsets. Zipped up to keep it small.
Source8: systemtap-tapset-3.4.0pre01.tar.xz

# Desktop files. Adapated from IcedTea.
Source9: jconsole.desktop.in
Source10: policytool.desktop.in

# nss configuration file
Source11: nss.cfg.in

# Removed libraries that we link instead
Source12: java-1.8.0-openjdk-remove-intree-libraries.sh

# Ensure we aren't using the limited crypto policy
Source13: TestCryptoLevel.java

# Ensure ECDSA is working
Source14: TestECDSA.java

Source20: repackReproduciblePolycies.sh

# New versions of config files with aarch64 support. This is not upstream yet.
Source100: config.guess
Source101: config.sub

# RPM/distribution specific patches

# Accessibility patches
# Ignore AWTError when assistive technologies are loaded 
Patch1:   java-1.8.0-openjdk-accessible-toolkit.patch
# Restrict access to java-atk-wrapper classes
Patch3: java-atk-wrapper-security.patch

# Upstreamable patches
# PR2737: Allow multiple initialization of PKCS11 libraries
Patch5: multiple-pkcs11-library-init.patch
# PR2095, RH1163501: 2048-bit DH upper bound too small for Fedora infrastructure (sync with IcedTea 2.x)
Patch504: rh1163501.patch
# S4890063, PR2304, RH1214835: HPROF: default text truncated when using doe=n option
Patch511: rh1214835.patch
# Turn off strict overflow on IndicRearrangementProcessor{,2}.cpp following 8140543: Arrange font actions
Patch512: no_strict_overflow.patch
# Support for building the SunEC provider with the system NSS installation
# PR1983: Support using the system installation of NSS with the SunEC provider
# PR2127: SunEC provider crashes when built using system NSS
# PR2815: Race condition in SunEC provider with system NSS
# PR2899: Don't use WithSeed versions of NSS functions as they don't fully process the seed
# PR2934: SunEC provider throwing KeyException with current NSS
Patch513: pr1983-jdk.patch
Patch514: pr1983-root.patch
Patch515: pr2127.patch
Patch516: pr2815.patch
Patch517: pr2899.patch
Patch518: pr2934.patch
# S8150954, RH1176206, PR2866: Taking screenshots on x11 composite desktop produces wrong result
# In progress: http://mail.openjdk.java.net/pipermail/awt-dev/2016-March/010742.html
Patch508: rh1176206-jdk.patch
Patch509: rh1176206-root.patch
# RH1337583, PR2974: PKCS#10 certificate requests now use CRLF line endings rather than system line endings
Patch523: pr2974-rh1337583.patch
# PR3083, RH1346460: Regression in SSL debug output without an ECC provider
Patch528: pr3083-rh1346460.patch
# Patches 204 and 205 stop the build adding .gnu_debuglink sections to unstripped files
Patch204: hotspot-remove-debuglink.patch
Patch205: dont-add-unnecessary-debug-links.patch
# Enable debug information for assembly code files
Patch206: hotspot-assembler-debuginfo.patch

# Arch-specific upstreamable patches
# PR2415: JVM -Xmx requirement is too high on s390
#Patch100: java-1.8.0-openjk-s390-java-opts.patch
# Type fixing for s390
#Patch102: java-1.8.0-openjk-size_t.patch
# Use "%z" for size_t on s390 as size_t != intptr_t
#Patch103: s390-size_t_format_flags.patch

# Patches which need backporting to 8u
# S8073139, RH1191652; fix name of ppc64le architecture
#Patch601: java-1.8.0-openjk-rh1191652-root.patch
#Patch602: java-1.8.0-openjk-rh1191652-jdk.patch
#Patch603: java-1.8.0-openjk-rh1191652-hotspot-aarch64.patch
# Include all sources in src.zip
Patch7: include-all-srcs.patch
# 8035341: Allow using a system installed libpng
Patch202: system-libpng.patch
# 8042159: Allow using a system-installed lcms2
Patch203: system-lcms.patch
# PR2462: Backport "8074839: Resolve disabled warnings for libunpack and the unpack200 binary"
# This fixes printf warnings that lead to build failure with -Werror=format-security from optflags
Patch502: pr2462.patch
# S8148351, PR2842: Only display resolved symlink for compiler, do not change path
Patch506: pr2842-01.patch
Patch507: pr2842-02.patch
# S8154313: Generated javadoc scattered all over the place
Patch400: 8154313.patch
# S6260348, PR3066: GTK+ L&F JTextComponent not respecting desktop caret blink rate
Patch526: 6260348-pr3066.patch
# 8061305, PR3335, RH1423421: Javadoc crashes when method name ends with "Property"
Patch538: 8061305-pr3335-rh1423421.patch
# 8181055, PR3394, RH1448880: PPC64: "mbind: Invalid argument" still seen after 8175813
#Patch551: 8181055-pr3394-rh1448880.patch
# 8181419, PR3413, RH1463144: Race in jdwp invoker handling may lead to crashes or invalid results
Patch553: 8181419-pr3413-rh1463144.patch

# Patches upstream and appearing in 8u152
# 8153711, PR3313, RH1284948: [REDO] JDWP: Memory Leak: GlobalRefs never deleted when processing invokeMethod command
Patch535: 8153711-pr3313-rh1284948.patch
# 8162384, PR3122, RH1358661: Performance regression: bimorphic inlining may be bypassed by type speculation
Patch532: 8162384-pr3122-rh1358661.patch
# 8173941, PR3326: SA does not work if executable is DSO
Patch547: 8173941-pr3326.patch
# 8175813, PR3394, RH1448880: PPC64: "mbind: Invalid argument" when -XX:+UseNUMA is used
#Patch550: 8175813-pr3394-rh1448880.patch
# 8179084, PR3409, RH1455694: HotSpot VM fails to start when AggressiveHeap is set
Patch552: 8179084-pr3409-rh1455694.patch
# 8175887, PR3415: C1 value numbering handling of Unsafe.get*Volatile is incorrect
Patch554: 8175887-pr3415.patch

# Patches upstream and appearing in 8u161
# 8164293, PR3412, RH1459641: HotSpot leaking memory in long-running requests
Patch555: 8164293-pr3412-rh1459641.patch

# Patches ineligible for 8u
# 8043805: Allow using a system-installed libjpeg
Patch201: system-libjpeg.patch
# custom securities
Patch207: PR3183.patch
#Patch208: aarch64BuildFailure.patch

# Local fixes
# PR1834, RH1022017: Reduce curves reported by SSL to those in NSS
Patch525: pr1834-rh1022017.patch
# RH1367357: lcms2: Out-of-bounds read in Type_MLU_Read()
Patch533: rh1367357.patch
# Turn on AssumeMP by default on RHEL systems
#Patch534: always_assumemp.patch
# PR2888: OpenJDK should check for system cacerts database (e.g. /etc/pki/java/cacerts)
Patch539: pr2888.patch

# Non-OpenJDK fixes
Patch1000: enableCommentedOutSystemNss.patch

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: alsa-lib-devel
BuildRequires: binutils
BuildRequires: cups-devel
BuildRequires: desktop-file-utils
BuildRequires: elfutils
BuildRequires: fontconfig
BuildRequires: freetype-devel
BuildRequires: giflib-devel
BuildRequires: gcc-c++
BuildRequires: gdb
BuildRequires: gtk2-devel
BuildRequires: lcms2-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: libxslt
BuildRequires: libX11-devel
BuildRequires: libXi-devel
BuildRequires: libXinerama-devel
BuildRequires: libXt-devel
BuildRequires: libXtst-devel
# Requirements for setting up the nss.cfg
BuildRequires: nss-devel
BuildRequires: pkgconfig
BuildRequires: xorg-x11-proto-devel
BuildRequires: zip
# Use OpenJDK 7 where available (on RHEL) to avoid
# having to use the rhel-7.x-java-unsafe-candidate hack
%if 0%{?rhel}
BuildRequires: java-1.7.0-openjdk-devel
%else
BuildRequires: java-1.8.0-openjdk-aarch32-devel
%endif
# Zero-assembler build requirement.
%ifnarch %{jit_arches}
BuildRequires: libffi-devel
%endif
BuildRequires: tzdata-java >= 2015d
# Earlier versions have a bug in tree vectorization on PPC
BuildRequires: gcc >= 4.8.3-8
# Build requirements for SunEC system NSS support
BuildRequires: nss-softokn-freebl-devel >= 3.16.1

%if %{with_systemtap}
BuildRequires: systemtap-sdt-devel
%endif

# this is built always, also during debug-only build
# when it is built in debug-only, then this package is just placeholder
%{java_rpo %{nil}}

ExclusiveArch: %{arm}

%description
A preview release of the upstream OpenJDK AArch32 porting project.
The OpenJDK runtime environment.

%if %{include_debug_build}
%package debug
Summary: OpenJDK Runtime Environment %{debug_on}
Group:   Development/Languages

%{java_rpo -- %{debug_suffix_unquoted}}
%description debug
The OpenJDK runtime environment.
%{debug_warning}
%endif

%if %{include_normal_build}
%package headless
Summary: OpenJDK Runtime Environment
Group:   Development/Languages

%{java_headless_rpo %{nil}}

%description headless
The OpenJDK runtime environment without audio and video support.
%endif

%if %{include_debug_build}
%package headless-debug
Summary: OpenJDK Runtime Environment %{debug_on}
Group:   Development/Languages

%{java_headless_rpo -- %{debug_suffix_unquoted}}

%description headless-debug
The OpenJDK runtime environment without audio and video support.
%{debug_warning}
%endif

%if %{include_normal_build}
%package devel
Summary: OpenJDK Development Environment
Group:   Development/Tools

%{java_devel_rpo %{nil}}

%description devel
The OpenJDK development tools.
%endif

%if %{include_debug_build}
%package devel-debug
Summary: OpenJDK Development Environment %{debug_on}
Group:   Development/Tools

%{java_devel_rpo -- %{debug_suffix_unquoted}}

%description devel-debug
The OpenJDK development tools.
%{debug_warning}
%endif

%if %{include_normal_build}
%package demo
Summary: OpenJDK Demos
Group:   Development/Languages

%{java_demo_rpo %{nil}}

%description demo
The OpenJDK demos.
%endif

%if %{include_debug_build}
%package demo-debug
Summary: OpenJDK Demos %{debug_on}
Group:   Development/Languages

%{java_demo_rpo -- %{debug_suffix_unquoted}}

%description demo-debug
The OpenJDK demos.
%{debug_warning}
%endif

%if %{include_normal_build}
%package src
Summary: OpenJDK Source Bundle
Group:   Development/Languages

%{java_src_rpo %{nil}}

%description src
The OpenJDK source bundle.
%endif

%if %{include_debug_build}
%package src-debug
Summary: OpenJDK Source Bundle %{for_debug}
Group:   Development/Languages

%{java_src_rpo -- %{debug_suffix_unquoted}}

%description src-debug
The OpenJDK source bundle %{for_debug}.
%endif

%if %{include_normal_build}
%package javadoc
Summary: OpenJDK API Documentation
Group:   Documentation
Requires: javapackages-tools
BuildArch: noarch

%{java_javadoc_rpo %{nil}}

%description javadoc
The OpenJDK API documentation.
%endif

%if %{include_normal_build}
%package javadoc-zip
Summary: OpenJDK API Documentation compressed in single archive
Group:   Documentation
Requires: javapackages-tools
BuildArch: noarch

%{java_javadoc_rpo %{nil}}

%description javadoc-zip
The OpenJDK API documentation compressed in single archive.
%endif

%if %{include_debug_build}
%package javadoc-debug
Summary: OpenJDK API Documentation %{for_debug}
Group:   Documentation
Requires: javapackages-tools
BuildArch: noarch

%{java_javadoc_rpo -- %{debug_suffix_unquoted}}

%description javadoc-debug
The OpenJDK API documentation %{for_debug}.
%endif

%if %{include_debug_build}
%package javadoc-zip-debug
Summary: OpenJDK API Documentation compressed in single archive %{for_debug}
Group:   Documentation
Requires: javapackages-tools
BuildArch: noarch

%{java_javadoc_rpo -- %{debug_suffix_unquoted}}

%description javadoc-zip-debug
The OpenJDK API documentation compressed in single archive %{for_debug}.
%endif


%if %{include_normal_build}
%package accessibility
Summary: OpenJDK accessibility connector

%{java_accessibility_rpo %{nil}}

%description accessibility
Enables accessibility support in OpenJDK by using java-atk-wrapper. This allows
compatible at-spi2 based accessibility programs to work for AWT and Swing-based
programs.

Please note, the java-atk-wrapper is still in beta, and OpenJDK itself is still
being tuned to be working with accessibility features. There are known issues
with accessibility on, so please do not install this package unless you really
need to.
%endif

%if %{include_debug_build}
%package accessibility-debug
Summary: OpenJDK accessibility connector %{for_debug}

%{java_accessibility_rpo -- %{debug_suffix_unquoted}}

%description accessibility-debug
See normal java-%{version}-openjdk-accessibility description.
%endif


%if %{with_openjfx_binding}
%package openjfx
Summary: OpenJDK x OpenJFX connector. This package adds symliks finishing Java FX integration to %{name}
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: openjfx%{?_isa}
Provides: javafx  = %{epoch}:%{version}-%{release}
%description openjfx
Set of links from OpenJDK (jre) to OpenJFX

%package openjfx-devel
Summary: OpenJDK x OpenJFX connector for FX developers. This package adds symliks finishing Java FX integration to %{name}-devel
Requires: %{name}-devel%{?_isa} = %{epoch}:%{version}-%{release}
Requires: openjfx-devel%{?_isa}
Provides: javafx-devel = %{epoch}:%{version}-%{release}
%description openjfx-devel
Set of links from OpenJDK (sdk) to OpenJFX

%if %{include_debug_build}
%package openjfx-debug
Summary: OpenJDK x OpenJFX connector %{for_debug}. his package adds symliks finishing Java FX integration to %{name}-debug
Requires: %{name}-debug%{?_isa} = %{epoch}:%{version}-%{release}
Requires: openjfx%{?_isa}
Provides: javafx-debug = %{epoch}:%{version}-%{release}
%description openjfx-debug
Set of links from OpenJDK-debug (jre) to normal OpenJFX. OpenJFX do not support debug buuilds of itself

%package openjfx-devel-debug
Summary: OpenJDK x OpenJFX connector for FX developers %{for_debug}. This package adds symliks finishing Java FX integration to %{name}-devel-debug
Requires: %{name}-devel-debug%{?_isa} = %{epoch}:%{version}-%{release}
Requires: openjfx-devel%{?_isa}
Provides: javafx-devel-debug = %{epoch}:%{version}-%{release}
%description openjfx-devel-debug
Set of links from OpenJDK-debug (sdk) to normal OpenJFX. OpenJFX do not support debug buuilds of itself
%endif
%endif

%prep
if [ %{include_normal_build} -eq 0 -o  %{include_normal_build} -eq 1 ] ; then
  echo "include_normal_build is %{include_normal_build}"
else
  echo "include_normal_build is %{include_normal_build}, thats invalid. Use 1 for yes or 0 for no"
  exit 11
fi
if [ %{include_debug_build} -eq 0 -o  %{include_debug_build} -eq 1 ] ; then
  echo "include_debug_build is %{include_debug_build}"
else
  echo "include_debug_build is %{include_debug_build}, thats invalid. Use 1 for yes or 0 for no"
  exit 12
fi
if [ %{include_debug_build} -eq 0 -a  %{include_normal_build} -eq 0 ] ; then
  echo "you have disabled both include_debug_build and include_debug_build. no go."
  exit 13
fi
%setup -q -c -n %{uniquesuffix ""} -T -a 0
# https://bugzilla.redhat.com/show_bug.cgi?id=1189084
prioritylength=`expr length %{priority}`
if [ $prioritylength -ne 7 ] ; then
 echo "priority must be 7 digits in total, violated"
 exit 14
fi
# For old patches
ln -s openjdk jdk8
%if %{use_shenandoah_hotspot}
# On Shenandoah-supported architectures, replace HotSpot with
# the Shenandoah version
pushd openjdk
tar -xf %{SOURCE1}
rm -rf hotspot
mv openjdk/hotspot .
rm -rf openjdk
popd
%endif

cp %{SOURCE2} .

# replace outdated configure guess script
#
# the configure macro will do this too, but it also passes a few flags not
# supported by openjdk configure script
cp %{SOURCE100} openjdk/common/autoconf/build-aux/
cp %{SOURCE101} openjdk/common/autoconf/build-aux/

# OpenJDK patches

# Remove libraries that are linked
sh %{SOURCE12}

# System library fixes
%patch201
%patch202
%patch203

# Debugging fixes
%patch204
%patch205
%patch206
%patch207
#%patch208

%patch1
%patch3
%patch5
%patch7

# s390 build fixes
#%patch100
#%patch102
#%patch103

# ppc64le fixes

#%patch603
#%patch601
#%patch602

# Zero fixes.

# Upstreamable fixes
%patch502
%patch504
%patch506
%patch507
%patch508
%patch509
%patch511
%patch512
%patch513
%patch514
%patch515
%patch516
%patch517
%patch518
%patch400
%patch523
%patch526
%patch528
%patch532
%patch535
%patch538
%patch547
#%patch550
#%patch551
%patch552
%patch553
%patch555

# RPM-only fixes
%patch525
%patch533
%patch539

# RHEL-only patches
%if 0%{?rhel}
%patch534
%endif

# 8175887 was added to the Shenandoah HotSpot ahead of time
%if %{use_shenandoah_hotspot}
%else
%patch554
%endif

%patch1000

# Extract systemtap tapsets
%if %{with_systemtap}
tar -x -I xz -f %{SOURCE8}
%if %{include_debug_build}
cp -r tapset tapset%{debug_suffix}
%endif


for suffix in %{build_loop} ; do
  for file in "tapset"$suffix/*.in; do
    OUTPUT_FILE=`echo $file | sed -e s:%{javaver}\.stp\.in$:%{version}-%{release}.%{_arch}.stp:g`
    sed -e s:@ABS_SERVER_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/jre/lib/%{archinstall}/server/libjvm.so:g $file > $file.1
# TODO find out which architectures other than i686 have a client vm
%ifarch %{ix86}
    sed -e s:@ABS_CLIENT_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/jre/lib/%{archinstall}/client/libjvm.so:g $file.1 > $OUTPUT_FILE
%else
    sed -e '/@ABS_CLIENT_LIBJVM_SO@/d' $file.1 > $OUTPUT_FILE
%endif
    sed -i -e s:@ABS_JAVA_HOME_DIR@:%{_jvmdir}/%{sdkdir -- $suffix}:g $OUTPUT_FILE
    sed -i -e s:@INSTALL_ARCH_DIR@:%{archinstall}:g $OUTPUT_FILE
    sed -i -e s:@prefix@:%{_jvmdir}/%{sdkdir -- $suffix}/:g $OUTPUT_FILE
  done
done
# systemtap tapsets ends
%endif

# Prepare desktop files
for suffix in %{build_loop} ; do
for file in %{SOURCE9} %{SOURCE10} ; do
    FILE=`basename $file | sed -e s:\.in$::g`
    EXT="${FILE##*.}"
    NAME="${FILE%.*}"
    OUTPUT_FILE=$NAME$suffix.$EXT
    sed -e s:#JAVA_HOME#:%{sdkbindir -- $suffix}:g $file > $OUTPUT_FILE
    sed -i -e  s:#JRE_HOME#:%{jrebindir -- $suffix}:g $OUTPUT_FILE
    sed -i -e  s:#ARCH#:%{version}-%{release}.%{_arch}$suffix:g $OUTPUT_FILE
done
done

# Setup nss.cfg
sed -e s:@NSS_LIBDIR@:%{NSS_LIBDIR}:g %{SOURCE11} > nss.cfg


%build
# How many cpu's do we have?
export NUM_PROC=%(/usr/bin/getconf _NPROCESSORS_ONLN 2> /dev/null || :)
export NUM_PROC=${NUM_PROC:-1}
%if 0%{?_smp_ncpus_max}
# Honor %%_smp_ncpus_max
[ ${NUM_PROC} -gt %{?_smp_ncpus_max} ] && export NUM_PROC=%{?_smp_ncpus_max}
%endif

# Build IcedTea and OpenJDK.
%ifarch s390x sparc64 alpha %{power64} %{aarch64}
export ARCH_DATA_MODEL=64
%endif
%ifarch alpha
export CFLAGS="$CFLAGS -mieee"
%endif

# We use ourcppflags because the OpenJDK build seems to
# pass EXTRA_CFLAGS to the HotSpot C++ compiler...
# Explicitly set the C++ standard as the default has changed on GCC >= 6
EXTRA_CFLAGS="%ourcppflags -std=gnu++98 -Wno-error -fno-delete-null-pointer-checks -fno-lifetime-dse"
EXTRA_CPP_FLAGS="%ourcppflags -std=gnu++98 -fno-delete-null-pointer-checks -fno-lifetime-dse"
%ifarch %{power64} ppc
# fix rpmlint warnings
EXTRA_CFLAGS="$EXTRA_CFLAGS -fno-strict-aliasing"
%endif
export EXTRA_CFLAGS

(cd openjdk/common/autoconf
 bash ./autogen.sh
)

for suffix in %{build_loop} ; do
if [ "$suffix" = "%{debug_suffix}" ] ; then
debugbuild=%{debugbuild_parameter}
else
debugbuild=%{normalbuild_parameter}
fi

mkdir -p %{buildoutputdir -- $suffix}
pushd %{buildoutputdir -- $suffix}

NSS_LIBS="%{NSS_LIBS} -lfreebl" \
NSS_CFLAGS="%{NSS_CFLAGS}" \
bash ../../configure \
    --with-jvm-variants=client \
    --disable-zip-debug-info \
    --with-milestone="fcs" \
    --with-update-version=%{updatever} \
    --with-build-number=%{buildver} \
    --with-boot-jdk=$(echo /usr/lib/jvm/java-1.8.0-openjdk-aarch32-*) \
    --with-debug-level=$debugbuild \
    --enable-unlimited-crypto \
    --enable-system-nss \
    --with-zlib=system \
    --with-libjpeg=system \
    --with-giflib=system \
    --with-libpng=system \
    --with-lcms=bundled \
    --with-stdc++lib=dynamic \
    --with-extra-cxxflags="$EXTRA_CPP_FLAGS" \
    --with-extra-cflags="$EXTRA_CFLAGS" \
    --with-extra-ldflags="%{ourldflags}" \
    --with-num-cores="$NUM_PROC"

cat spec.gmk
cat hotspot-spec.gmk

# The combination of FULL_DEBUG_SYMBOLS=0 and ALT_OBJCOPY=/does_not_exist
# disables FDS for all build configs and reverts to pre-FDS make logic.
# STRIP_POLICY=none says don't do any stripping. DEBUG_BINARIES=true says
# ignore all the other logic about which debug options and just do '-g'.

make \
    DEBUG_BINARIES=true \
    JAVAC_FLAGS=-g \
    STRIP_POLICY=no_strip \
    POST_STRIP_CMD="" \
    LOG=trace \
    SCTP_WERROR= \
    %{targets}

make zip-docs

# the build (erroneously) removes read permissions from some jars
# this is a regression in OpenJDK 7 (our compiler):
# http://icedtea.classpath.org/bugzilla/show_bug.cgi?id=1437
find images/%{j2sdkimage} -iname '*.jar' -exec chmod ugo+r {} \;
chmod ugo+r images/%{j2sdkimage}/lib/ct.sym

# remove redundant *diz and *debuginfo files
find images/%{j2sdkimage} -iname '*.diz' -exec rm {} \;
find images/%{j2sdkimage} -iname '*.debuginfo' -exec rm {} \;

popd >& /dev/null

# Install nss.cfg right away as we will be using the JRE above
export JAVA_HOME=$(pwd)/%{buildoutputdir -- $suffix}/images/%{j2sdkimage}

# Install nss.cfg right away as we will be using the JRE above
install -m 644 nss.cfg $JAVA_HOME/jre/lib/security/

# Use system-wide tzdata
rm $JAVA_HOME/jre/lib/tzdb.dat
ln -s %{_datadir}/javazi-1.8/tzdb.dat $JAVA_HOME/jre/lib/tzdb.dat

#build cycles
done

%check

# We test debug first as it will give better diagnostics on a crash
for suffix in %{rev_build_loop} ; do

export JAVA_HOME=$(pwd)/%{buildoutputdir -- $suffix}/images/%{j2sdkimage}

# Check unlimited policy has been used
$JAVA_HOME/bin/javac -d . %{SOURCE13}
$JAVA_HOME/bin/java TestCryptoLevel

# Check ECC is working
$JAVA_HOME/bin/javac -d . %{SOURCE14}
$JAVA_HOME/bin/java $(echo $(basename %{SOURCE14})|sed "s|\.java||")

# Check debug symbols are present and can identify code
find "$JAVA_HOME" -iname '*.so' -print0 | while read -d $'\0' lib
do
  if [ -f "$lib" ] ; then
    echo "Testing $lib for debug symbols"
    # All these tests rely on RPM failing the build if the exit code of any set
    # of piped commands is non-zero.

    # Test for .debug_* sections in the shared object. This is the  main test.
    # Stripped objects will not contain these.
    eu-readelf -S "$lib" | grep "] .debug_"
    test $(eu-readelf -S "$lib" | grep -E "\]\ .debug_(info|abbrev)" | wc --lines) == 2

    # Test FILE symbols. These will most likely be removed by anyting that
    # manipulates symbol tables because it's generally useless. So a nice test
    # that nothing has messed with symbols.
    old_IFS="$IFS"
    IFS=$'\n'
    for line in $(eu-readelf -s "$lib" | grep "00000000      0 FILE    LOCAL  DEFAULT")
    do
     # We expect to see .cpp files, except for architectures like aarch64 and
     # s390 where we expect .o and .oS files
      echo "$line" | grep -E "ABS ((.*/)?[-_a-zA-Z0-9]+\.(c|cc|cpp|cxx|o|oS))?$"
    done
    IFS="$old_IFS"

    # If this is the JVM, look for javaCalls.(cpp|o) in FILEs, for extra sanity checking.
    if [ "`basename $lib`" = "libjvm.so" ]; then
      eu-readelf -s "$lib" | \
        grep -E "00000000      0 FILE    LOCAL  DEFAULT      ABS javaCalls.(cpp|o)$"
    fi

    # Test that there are no .gnu_debuglink sections pointing to another
    # debuginfo file. There shouldn't be any debuginfo files, so the link makes
    # no sense either.
    eu-readelf -S "$lib" | grep 'gnu'
    if eu-readelf -S "$lib" | grep '] .gnu_debuglink' | grep PROGBITS; then
      echo "bad .gnu_debuglink section."
      eu-readelf -x .gnu_debuglink "$lib"
      false
    fi
  fi
done

# Make sure gdb can do a backtrace based on line numbers on libjvm.so
gdb -q "$JAVA_HOME/bin/java" <<EOF | tee gdb.out
handle SIGSEGV pass nostop noprint
handle SIGILL pass nostop noprint
set breakpoint pending on
break javaCalls.cpp:1
commands 1
backtrace
quit
end
run -version
EOF
grep 'JavaCallWrapper::JavaCallWrapper' gdb.out

# Check src.zip has all sources. See RHBZ#1130490
jar -tf $JAVA_HOME/src.zip | grep 'sun.misc.Unsafe'

# Check class files include useful debugging information
$JAVA_HOME/bin/javap -l java.lang.Object | grep "Compiled from"
$JAVA_HOME/bin/javap -l java.lang.Object | grep LineNumberTable
$JAVA_HOME/bin/javap -l java.lang.Object | grep LocalVariableTable

# Check generated class files include useful debugging information
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep "Compiled from"
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep LineNumberTable
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep LocalVariableTable

#build cycles check
done

%install
STRIP_KEEP_SYMTAB=libjvm*

for suffix in %{build_loop} ; do

pushd %{buildoutputdir -- $suffix}/images/%{j2sdkimage}

#install jsa directories so we can owe them
mkdir -p $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/server/
mkdir -p $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/client/

  # Install main files.
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}
  cp -a bin include lib src.zip $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}
  cp -a jre/bin jre/lib $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}

%if %{with_systemtap}
  # Install systemtap support files.
  install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset
  # note, that uniquesuffix  is in BUILD dir in this case
  cp -a $RPM_BUILD_DIR/%{uniquesuffix ""}/tapset$suffix/*.stp $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
  pushd  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
   tapsetFiles=`ls *.stp`
  popd
  install -d -m 755 $RPM_BUILD_ROOT%{tapsetdir}
  pushd $RPM_BUILD_ROOT%{tapsetdir}
    RELATIVE=$(%{abs2rel} %{_jvmdir}/%{sdkdir -- $suffix}/tapset %{tapsetdir})
    for name in $tapsetFiles ; do
      targetName=`echo $name | sed "s/.stp/$suffix.stp/"`
      ln -sf $RELATIVE/$name $targetName
    done
  popd
%endif

  # Remove empty cacerts database.
  rm -f $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/security/cacerts
  # Install cacerts symlink needed by some apps which hardcode the path.
  pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/security
    RELATIVE=$(%{abs2rel} %{_sysconfdir}/pki/java \
      %{_jvmdir}/%{jredir -- $suffix}/lib/security)
    ln -sf $RELATIVE/cacerts .
  popd

  # Install JCE policy symlinks.
  install -d -m 755 $RPM_BUILD_ROOT%{_jvmprivdir}/%{uniquesuffix -- $suffix}/jce/vanilla

  # Install versioned symlinks.
  pushd $RPM_BUILD_ROOT%{_jvmdir}
    ln -sf %{jredir -- $suffix} %{jrelnk -- $suffix}
  popd

  # Remove javaws man page
  rm -f man/man1/javaws*

  # Install man pages.
  install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
  for manpage in man/man1/*
  do
    # Convert man pages to UTF8 encoding.
    iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
    mv -f $manpage.tmp $manpage
    install -m 644 -p $manpage $RPM_BUILD_ROOT%{_mandir}/man1/$(basename \
      $manpage .1)-%{uniquesuffix -- $suffix}.1
  done

  # Install demos and samples.
  cp -a demo $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}
  mkdir -p sample/rmi
  if [ ! -e sample/rmi/java-rmi.cgi ] ; then 
    # hack to allow --short-circuit on install
    mv bin/java-rmi.cgi sample/rmi
  fi
  cp -a sample $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}

popd


# Install Javadoc documentation.
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}
cp -a %{buildoutputdir -- $suffix}/docs $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}
cp -a %{buildoutputdir -- $suffix}/bundles/jdk-%{javaver}_%{updatever}$suffix-%{buildver}-docs.zip  $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}.zip

# Install icons and menu entries.
for s in 16 24 32 48 ; do
  install -D -p -m 644 \
    openjdk/jdk/src/solaris/classes/sun/awt/X11/java-icon${s}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps/java-%{javaver}.png
done

# Install desktop files.
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
for e in jconsole$suffix policytool$suffix ; do
    desktop-file-install --vendor=%{uniquesuffix -- $suffix} --mode=644 \
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications $e.desktop
done

# Install /etc/.java/.systemPrefs/ directory
# See https://bugzilla.redhat.com/show_bug.cgi?id=741821
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/.java/.systemPrefs

# FIXME: remove SONAME entries from demo DSOs.  See
# https://bugzilla.redhat.com/show_bug.cgi?id=436497

# Find non-documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/sample \
  -type f -o -type l | sort \
  | grep -v README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  >> %{name}-demo.files"$suffix"
# Find documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/sample \
  -type f -o -type l | sort \
  | grep README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  | sed 's|^|%doc |' \
  >> %{name}-demo.files"$suffix"

# Create links which leads to separately installed java-atk-bridge and allow configuration
# links points to java-atk-wrapper - an dependence
  pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}
    ln -s %{_libdir}/java-atk-wrapper/libatk-wrapper.so.0 libatk-wrapper.so
  popd
  pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/aarch32
    ln -s %{_libdir}/java-atk-wrapper/libatk-wrapper.so.0 libatk-wrapper.so
  popd
  pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/ext
     ln -s %{_libdir}/java-atk-wrapper/java-atk-wrapper.jar  java-atk-wrapper.jar
  popd
  pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/
    echo "#Config file to  enable java-atk-wrapper" > accessibility.properties
    echo "" >> accessibility.properties
    echo "assistive_technologies=org.GNOME.Accessibility.AtkWrapper" >> accessibility.properties
    echo "" >> accessibility.properties
  popd

# RHBZ#1412953
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/client/
    ln -sf ../../aarch32/client/libjvm.so
popd
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/
    for lib in \
        libattach.so \
        libawt_headless.so \
        libawt.so \
        libawt_xawt.so \
        libdt_socket.so \
        libfontmanager.so \
        libhprof.so \
        libinstrument.so \
        libj2gss.so \
        libj2pcsc.so \
        libj2pkcs11.so \
        libjaas_unix.so \
        libjava_crw_demo.so \
        libjavajpeg.so \
        libjava.so \
        libjawt.so \
        libjdwp.so \
        libjsdt.so \
        libjsig.so \
        libjsoundalsa.so \
        libjsound.so \
        liblcms.so \
        libmanagement.so \
        libmlib_image.so \
        libnet.so \
        libnio.so \
        libnpt.so \
        libsctp.so \
        libsplashscreen.so \
        libsunec.so \
        libunpack.so \
        libverify.so \
        libzip.so \
        jvm.cfg \
        ; do ln -sf ../aarch32/$lib ; done
        mkdir -p jli
popd
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/jli
    ln -sf ../../aarch32/jli/libjli.so
popd
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/
    mkdir -p %{archinstall}
popd
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/%{archinstall}
    ln -sf ../aarch32/libjawt.so
    mkdir -p jli
popd
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/%{archinstall}/jli
    ln -sf ../../aarch32/jli/libjli.so
popd

# intentionally after all else, fx links  with redirections on its own
%if %{with_openjfx_binding}
  FXSDK_FILES=%{name}-openjfx-devel.files"$suffix"
  FXJRE_FILES=%{name}-openjfx.files"$suffix"
  echo -n "" > $FXJRE_FILES
  echo -n "" > $FXSDK_FILES
  for file in  %{jfx_jre_libs} ; do
    srcfile=%{jfx_jre_libs_dir}/$file
    targetfile=%{_jvmdir}/%{jredir -- $suffix}/lib/$file
    ln -s $srcfile $RPM_BUILD_ROOT/$targetfile
    echo $targetfile >> $FXJRE_FILES
  done
  for file in  %{jfx_jre_native} ; do
    srcfile=%{jfx_jre_native_dir}/$file
    targetfile=%{_jvmdir}/%{jredir -- $suffix}/lib/%{archinstall}/$file
    ln -s $srcfile $RPM_BUILD_ROOT/$targetfile
    echo $targetfile >> $FXJRE_FILES
  done
  for file in  %{jfx_jre_exts} ; do
    srcfile=%{jfx_jre_exts_dir}/$file
    targetfile=%{_jvmdir}/%{jredir -- $suffix}/lib/ext/$file
    ln -s $srcfile $RPM_BUILD_ROOT/$targetfile
    echo $targetfile >> $FXJRE_FILES
  done
  for file in  %{jfx_sdk_libs} ; do
    srcfile=%{jfx_sdk_libs_dir}/$file
    targetfile=%{_jvmdir}/%{sdkdir -- $suffix}/lib/$file
    ln -s $srcfile $RPM_BUILD_ROOT/$targetfile
    echo $targetfile >> $FXSDK_FILES
  done
  for file in  %{jfx_sdk_bins} ; do
    srcfile=%{jfx_sdk_bins_dir}/$file
    targetfile=%{_jvmdir}/%{sdkdir -- $suffix}/bin/$file
    ln -s $srcfile $RPM_BUILD_ROOT/$targetfile
    echo $targetfile >> $FXSDK_FILES
  done
%endif

bash %{SOURCE20} $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix} %{javaver}
# https://bugzilla.redhat.com/show_bug.cgi?id=1183793
touch -t 201401010000 $RPM_BUILD_ROOT/%{_jvmdir}/%{jredir -- $suffix}/lib/security/java.security

# end, dual install
done

%if %{include_normal_build} 
# intentioanlly only for non-debug
%pretrans headless -p <lua>
-- see https://bugzilla.redhat.com/show_bug.cgi?id=1038092 for whole issue
-- see https://bugzilla.redhat.com/show_bug.cgi?id=1290388 for pretrans over pre
-- if copy-jdk-configs is in transaction, it installs in pretrans to temp
-- if copy_jdk_configs is in temp, then it means that copy-jdk-configs is in tranasction  and so is
-- preferred over one in %%{_libexecdir}. If it is not in transaction, then depends 
-- whether copy-jdk-configs is installed or not. If so, then configs are copied
-- (copy_jdk_configs from %%{_libexecdir} used) or not copied at all
local posix = require "posix"
local debug = false

SOURCE1 = "%{rpm_state_dir}/copy_jdk_configs.lua"
SOURCE2 = "%{_libexecdir}/copy_jdk_configs.lua"

local stat1 = posix.stat(SOURCE1, "type");
local stat2 = posix.stat(SOURCE2, "type");

  if (stat1 ~= nil) then
  if (debug) then
    print(SOURCE1 .." exists - copy-jdk-configs in transaction, using this one.")
  end;
  package.path = package.path .. ";" .. SOURCE1
else 
  if (stat2 ~= nil) then
  if (debug) then
    print(SOURCE2 .." exists - copy-jdk-configs alrady installed and NOT in transation. Using.")
  end;
  package.path = package.path .. ";" .. SOURCE2
  else
    if (debug) then
      print(SOURCE1 .." does NOT exists")
      print(SOURCE2 .." does NOT exists")
      print("No config files will be copied")
    end
  return
  end
end
-- run contetn of included file with fake args
arg = {"--currentjvm", "%{uniquesuffix %{nil}}", "--jvmdir", "%{_jvmdir %{nil}}", "--origname", "%{name}", "--origjavaver", "%{javaver}", "--arch", "%{_arch}", "--temp", "%{rpm_state_dir}/%{name}.%{_arch}"}
require "copy_jdk_configs.lua"

%post 
%{post_script %{nil}}

%post headless
%{post_headless %{nil}}

%postun
%{postun_script %{nil}}

%postun headless
%{postun_headless %{nil}}

%posttrans
%{posttrans_script %{nil}}

%post devel
%{post_devel %{nil}}

%postun devel
%{postun_devel %{nil}}

%posttrans  devel
%{posttrans_devel %{nil}}

%post javadoc
%{post_javadoc %{nil}}

%postun javadoc
%{postun_javadoc %{nil}}

%post javadoc-zip
%{post_javadoc_zip %{nil}}

%postun javadoc-zip
%{postun_javadoc_zip %{nil}}
%endif

%if %{include_debug_build} 
%post debug
%{post_script -- %{debug_suffix_unquoted}}

%post headless-debug
%{post_headless -- %{debug_suffix_unquoted}}

%postun debug
%{postun_script -- %{debug_suffix_unquoted}}

%postun headless-debug
%{postun_headless -- %{debug_suffix_unquoted}}

%posttrans debug
%{posttrans_script -- %{debug_suffix_unquoted}}

%post devel-debug
%{post_devel -- %{debug_suffix_unquoted}}

%postun devel-debug
%{postun_devel -- %{debug_suffix_unquoted}}

%posttrans  devel-debug
%{posttrans_devel -- %{debug_suffix_unquoted}}

%post javadoc-debug
%{post_javadoc -- %{debug_suffix_unquoted}}

%postun javadoc-debug
%{postun_javadoc -- %{debug_suffix_unquoted}}

%post javadoc-zip-debug
%{post_javadoc_zip -- %{debug_suffix_unquoted}}

%postun javadoc-zip-debug
%{postun_javadoc_zip -- %{debug_suffix_unquoted}}
%endif

%if %{include_normal_build} 
%files
# main package builds always
%{files_jre %{nil}}
%else
%files
# placeholder
%endif


%if %{include_normal_build} 
%files headless
# important note, see https://bugzilla.redhat.com/show_bug.cgi?id=1038092 for whole issue 
# all config/norepalce files (and more) have to be declared in pretrans. See pretrans
%{files_jre_headless %{nil}}

%files devel
%{files_devel %{nil}}

%files demo -f %{name}-demo.files
%{files_demo %{nil}}

%files src
%{files_src %{nil}}

%files javadoc
%{files_javadoc %{nil}}

%files javadoc-zip
%{files_javadoc_zip %{nil}}

%files accessibility
%{files_accessibility %{nil}}

%if %{with_openjfx_binding}
%files openjfx -f %{name}-openjfx.files

%files openjfx-devel -f %{name}-openjfx-devel.files
%endif
%endif

%if %{include_debug_build} 
%files debug
%{files_jre -- %{debug_suffix_unquoted}}

%files headless-debug
%{files_jre_headless -- %{debug_suffix_unquoted}}

%files devel-debug
%{files_devel -- %{debug_suffix_unquoted}}

%files demo-debug -f %{name}-demo.files-debug
%{files_demo -- %{debug_suffix_unquoted}}

%files src-debug
%{files_src -- %{debug_suffix_unquoted}}

%files javadoc-debug
%{files_javadoc -- %{debug_suffix_unquoted}}

%files javadoc-zip-debug
%{files_javadoc_zip -- %{debug_suffix_unquoted}}

%files accessibility-debug
%{files_accessibility -- %{debug_suffix_unquoted}}

%if %{with_openjfx_binding}
%files openjfx-debug -f %{name}-openjfx.files-debug

%files openjfx-devel-debug -f %{name}-openjfx-devel.files-debug
%endif
%endif

%changelog
* Fri Sep 15 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.144-2.170809
- bump release to 2 to fix dist.upgradepath

* Wed Sep 6 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.144-1.170809
- mainline package merge
- provides disabled

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.8.0.131-3.170420
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 24 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.141-1.170721
- update sources to 8u141
- sync with mainline package

* Sun Apr 30 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.131-2.170420
- revert boot jdk to zero due to koschei arch-specific dep problem persists

* Sat Apr 29 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.131-1.170420
- update sources to 8u131
- sync with mainline package

* Wed Apr 12 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.121-4.170210
- sync with mainline package
- add 8175234-aarch32 upstream patch

* Fri Mar 10 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.121-4.170210
- version bump to fix duplicated failed f26 build

* Tue Feb 28 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.121-3.170210
- rebuild because of NSS

* Mon Feb 20 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.121-2.170210
- add symlinks to jre/lib/arm directory for all aarch32 libs

* Sun Feb 19 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.121-1.170210
- sources tarball updated to jdk8u121-b13-aarch32-170210
- add libjvm.so and libjava.so symlinks to jre/lib/arm directory
- disable javadoc provides
- fixes RHBZ#1412953

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:1.8.0.112-4.161109
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 30 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.112-3.161109
- 8u121 update

* Mon Jan 2 2017 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.112-2.161109
- disable hardened build flags
- remove Xmx patch
- fixes RHBZ#1290936

* Thu Dec 22 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.112-1.161109
- fontconfig and nss restricted by isa
- debug subpackages allowed
- eu-readelfs on libraries, gdb call
- java SSL/TLS implementation: should follow the policies of system-wide crypto policy
- sync patches with mainline package
- 8u112 sources tarball
- add aarch32 post-u112 upstream patches

* Tue Oct 25 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-11.160812
- added aarch32-8u111.patch
- removed corba_typo_fix.patch

* Tue Oct 04 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.102-10.160812
- enabled debug build

* Mon Oct 03 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-9.160812
- added aarch32-8167027.patch
- fixes RHBZ#1379061

* Fri Sep 30 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-8.160812
- added aarch32-archname.patch

* Thu Sep 22 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-7.160812
- revert boot jdk back to zero

* Wed Sep 21 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-6.160812
- fixed macro in comments
- re-enabled openjdk-aarch32 as a boot jdk
- enabled provides for both java and javac

* Tue Sep 20 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.102-5.160812
- sync with normal java packages:
-  added zipped javadocs
-  updated systemtap
-  added (commented out) provides on jjs

* Sat Sep 10 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-4.160812
- declared check_sum_presented_in_spec and used in prep and check
- it is checking that latest packed java.security is mentioned in listing
- added ECDSA check
- added %%{_arch} postfix to alternatives

* Wed Aug 31 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-3.160812
- revert boot jdk back to zero

* Mon Aug 29 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-2.160812
- added C1 JIT patches
- use java-1.8.0-openjdk-aarch32 as a boot jdk

* Sun Aug 14 2016 Alex Kashchenko <akashche@redhat.com> - 1:1.8.0.102-1.160812
- remove upstreamed soundFontPatch.patch
- added patches 6260348-pr3066.patch, pr2974-rh1337583.patch, pr3083-rh1346460.patch, pr2899.patch, pr2934.patch, pr1834-rh1022017.patch, corba_typo_fix.patch, 8154313.patch
- removed unused patches java-1.8.0-openjdk-rh1191652-root.patch, java-1.8.0-openjdk-rh1191652-jdk.patch, java-1.8.0-openjdk-rh1191652-hotspot-aarch64.patch
- removed upstreamed (and previously unused) patches 8143855.patch, rhbz1206656_fix_current_stack_pointer.patch, remove_aarch64_template_for_gcc6.patch, make_reservedcodecachesize_changes_aarch64_only.patch
- added JDWP patches 8044762-pr2960.patch and 8049226-pr2960.patch
- priority lowered for ine zero digit, tip moved to 999
- Restricted to depend on exactly same version of nss as used for build,
- Resolves: rhbz#1332456
- used aarch32-port-jdk8u-jdk8u102-b14-aarch32-160812.tar.xz as new sources

* Wed Jun 29 2016 Jiri Vanek <jvanek@redhat.com> - 1:1.8.0.91-1.160510
- initial clone form java-1.8.0-openjdk
- using aarch32 sources
- restricted to {arm}  arch only
- adapted description and summary
- all {name} in pathches replaced by java-1.8.0-openjdk. Same for source12
- blindly commented out not applicable patches
- removed all java provides
