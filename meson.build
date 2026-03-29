project('io.github.Pavle012.Skakavi-krompir',
  version: '2.1.1',
  meson_version: '>= 0.62.0'
)

# Detect python
python = import('python').find_installation('python3')

# Dirs
pkgdatadir = get_option('datadir') / 'skakavi-krompir'
bindir = get_option('bindir')

install_subdir('original', install_dir: pkgdatadir)
install_subdir('shared', install_dir: pkgdatadir)
install_subdir('assets', install_dir: pkgdatadir)

# Desktop file
install_data('io.github.Pavle012.Skakavi-krompir.desktop', install_dir: get_option('datadir') / 'applications')

# Metainfo
install_data('io.github.Pavle012.Skakavi-krompir.metainfo.xml', install_dir: get_option('datadir') / 'metainfo')

# Icon
install_data('assets/io.github.Pavle012.Skakavi-krompir.png',
  install_dir: get_option('datadir') / 'icons/hicolor/256x256/apps/',
  rename: 'io.github.Pavle012.Skakavi-krompir.png'
)

# License
install_data('LICENSE',
  install_dir: get_option('datadir') / 'licenses' / 'io.github.Pavle012.Skakavi-krompir'
)

# Launch script generator
conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set('PKG_DATA_DIR', pkgdatadir)

configure_file(
  input: 'skakavi-krompir.sh.in',
  output: 'skakavi-krompir',
  configuration: conf,
  install_dir: bindir
)
