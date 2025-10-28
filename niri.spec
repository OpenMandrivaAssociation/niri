%bcond_with test
Name:           niri
Version:        25.08
Release:        2
Summary:        Scrollable-tiling Wayland compositor
License:        GPL-3.0-or-later
URL:            https://github.com/YaLTeR/niri
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{url}/releases/download/v%{version}/niri-%{version}-vendored-dependencies.tar.xz
Source2:        cargo_config
BuildRequires:  rust-packaging
BuildRequires:  clang
BuildRequires:  pango-devel
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig
BuildRequires:  rust >= 1.70.0
BuildRequires:  wayland-devel
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(cairo-gobject)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(udev)
BuildRequires:  pkgconfig(xkbcommon)
# Portal implementations used by niri
Recommends:     xdg-desktop-portal-gtk
Recommends:     xdg-desktop-portal-gnome
Recommends:     gnome-keyring
Recommends:     polkit-gnome
# Recommended utilities, bound in the default config
Recommends:     alacritty
Recommends:     fuzzel
Recommends:     swaylock
# Recommended utilities
Recommends:     swaybg
Recommends:     mako
Recommends:     xwayland-run

# Niri by deflaut at launch trying to spawn waybar. Lets add it as recommended (per upstream request).
# This can be configured to other packages.
Recommends:     waybar

%description
A scrollable-tiling Wayland compositor.

Windows are arranged in columns on an infinite strip going to the right.
Opening a new window never causes existing windows to resize.

%prep
%autosetup -a1 -p1
%cargo_prep
sed -i -e 's,source.crates-io,sources.rust-sucks,g' .cargo/config.toml
cat %{SOURCE2} >>.cargo/config.toml

%build
%cargo_build

target/rpm/niri completions bash > niri.bash
target/rpm/niri completions fish > niri.fish
target/rpm/niri completions zsh > _niri

%install
install -Dm755 -t %{buildroot}%{_bindir} target/release/%{name}
install -Dm755 -t %{buildroot}%{_bindir} resources/niri-session
install -Dm644 -t %{buildroot}%{_datadir}/wayland-sessions resources/niri.desktop
install -Dm644 -t %{buildroot}%{_datadir}/xdg-desktop-portal resources/niri-portals.conf
install -Dm644 -t %{buildroot}%{_userunitdir} resources/niri{.service,-shutdown.target}

install -Dpm0644 niri.bash -t %{buildroot}%{_datadir}/bash-completions/completions/
install -Dpm0644 niri.fish -t %{buildroot}%{_datadir}/fish-completions/completions/
install -Dpm0644 _niri -t %{buildroot}%{_datadir}/zsh-completions/completions/

%check
%if %{with test}
%cargo_test -- --workspace --exclude niri-visual-tests
%endif

%post
%systemd_user_post niri.service

%preun
%systemd_user_preun niri.service

%postun
%systemd_user_postun_with_reload niri.service

%files
%license LICENSE
%doc README.md resources/default-config.kdl docs/wiki
%{_bindir}/niri
%{_bindir}/niri-session
%dir %{_datadir}/wayland-sessions
%{_datadir}/wayland-sessions/niri.desktop
%dir %{_datadir}/xdg-desktop-portal
%{_datadir}/xdg-desktop-portal/niri-portals.conf
%{_userunitdir}/niri.service
%{_userunitdir}/niri-shutdown.target
%{_datadir}/bash-completions/completions/
%{_datadir}/fish-completions/completions/
%{_datadir}/zsh-completions/completions/
