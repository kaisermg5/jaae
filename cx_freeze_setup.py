
import os
import sys
import subprocess

from cx_Freeze import setup, Executable

try:
    version = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
except FileNotFoundError:
    print("Cannot get version. Git isn't installed.", file=sys.stderr)
    version = 'unknown'
except subprocess.CalledProcessError:
    print("Cannot get version. Git repo wasn't cloned", file=sys.stderr)
    version = 'unknown'

scripts = ['jaae.py']
base = 'Win32GUI'

data_files = ['resources', 'README.md']

build_exe_options = {'packages': ['PyQt5', 'PIL', 'jaae'],
                     'includes': ['sip'],
                     'excludes': 'tkinter',
                     'include_files': data_files,
                     }

executables = []
for script in scripts:
    executables.append(Executable(script, base=base, icon=os.path.abspath('resources/jaae.ico')))


setup(name='JAAE - Just an Animation Editor',
      version=version,
      description='A tileset animations editor for pokémon gen 3 games.',
      author='Kaiser de Emperana',
      url='https://github.com/kaisermg5/jaae',
      options={"build_exe": build_exe_options},
      requires=['sip', 'PyQt5', 'PIL'],
      scripts=scripts,
      packages=['jaae'],
      executables=executables
      )
