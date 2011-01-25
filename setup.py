#!/usr/bin/env python

from setuptools import setup

setup(name='pyvst',
      version='0.1.0',
      description='Python ctypes-based VST wrapper',
      author='Matthieu Brucher',
      author_email='matthieu.brucher@gmail.com',
      packages=['pyvst', ],
      classifiers =
            [ 'Development Status :: 4 - Beta',
              'Environment :: Win32 (MS Windows)',
              'Environment :: Plugins',
              'Intended Audience :: Developers',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: GNU General Public License (GPL)',
              'Operating System :: Microsoft :: Windows',
              'Topic :: Multimedia :: Sound/Audio',
              'Topic :: Scientific/Engineering',
            ]
      )

