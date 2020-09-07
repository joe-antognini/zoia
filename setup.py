"""Setup tooling for `zoia`."""

from setuptools import setup

with open('README.md') as fp:
    long_description = fp.read()

setup(
    name='zoia',
    version='0.1.0',
    description='Command line tool to manage references.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/joe-antognini/zoia',
    author='Joseph Antognini',
    author_email='joe.antognini@gmail.com',
    license='MIT',
    packages=['zoia'],
    install_requires=[
        'click>=7.1.2',
        'feedparser>=5.2.1',
        'halo>=0.0.30',
        'pyyaml>=5.3.1',
        'requests>=2.24.0',
    ],
    entry_points={
        'console_scripts':
            ['zoia=zoia.cli:zoia'],
    },
    include_package_data=True,
    setup_requires=['pytest-runner'],
    test_requires=['pytest'],
    python_requires='>=3.8',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
    ],
)
