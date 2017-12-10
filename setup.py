from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sense_hat_display_utils',
    version='0.1.6',
    # packages=[''],
    url='https://github.com/e2m4n/python-sense-hat-display-utils',
    license='',
    author='Aaron Fleming',
    author_email='e_z_a@hotmail.com',
    description='Utilities for the LED display on the Raspberry Pi Sense HAT',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords='sense-hat',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['sense-hat',
                      'Pillow',
                      'colour',
                      # 'RTIMU'
                      ],
    dependency_links=[
        # "https://github.com/RPi-Distro/RTIMULib.git#egg=version_subpkg&subdirectory=Linux/python"
    ],
    entry_points={
        'console_scripts': [
            'sense-hat-display-utils=sense_hat_display_utils.__main__:main',
        ],
    },
)
