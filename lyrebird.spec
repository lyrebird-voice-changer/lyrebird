Name:          lyrebird
Summary:       Simple and powerful voice changer for Linux, written with Python & GTK.
URL:           https://github.com/lyrebird-voice-changer/%{name}

Version:       1.2.0
Release:       1%{dist}
License:       MIT

Source0:       %{URL}/archive/v%{version}.tar.gz
BuildArch:     noarch

BuildRequires: gettext

Requires:      python3 >= 3.7.0
Requires:      python3-toml
Requires:      python3-gobject
Requires:      pulseaudio
Requires:      sox

%description
Simple and powerful voice changer for Linux, written with Python & GTK.
Features:
* Built in effects for accurate male and female voices.
* Ability to create and load custom presets.
* Manual pitch scale for finer adjustment.
* Creates its own temporary virtual input device.
* A clean and easy to use GUI.

%prep
%setup -q -n %{name}-%{version}

%install
install -dm 0755 %{buildroot}/%{_bindir}
install -m 0755 %{name} %{buildroot}/%{_bindir}/
install -dm 0755 %{buildroot}/%{_datadir}/%{name}
cp -rf app app.py icon.png %{buildroot}/%{_datadir}/%{name}/
install -dm 0755 %{buildroot}/%{_datadir}/applications
BIN_PATH=%{_bindir} SHARE_PATH=%{_datadir}/%{name} envsubst < %{name}.desktop > %{buildroot}/%{_datadir}/applications/%{name}.desktop

%files
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%license LICENSE
%doc README.md CHANGELOG.md

%changelog
* Tue Aug 22 2023 sT331h0rs3 <sT331h0rs3@gmail.com> - 1.2.0-1
- Update version to 1.2.0 and description.

* Fri Jan 28 2022 sT331h0rs3 <sT331h0rs3@gmail.com> - 1.1.0-4
- Change the GitHub URL and set noarch.

* Sun Apr 04 2021 sT331h0rs3 <sT331h0rs3@gmail.com> - 1.1.0-3
- Initial RPM packaging for Fedora is done.

