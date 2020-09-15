"""Setup tooling for `zoia`."""

import setuptools

import versioneer

with open('README.md') as fp:
    long_description = fp.read()

setuptools.setup(
    name='zoia',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Command line tool to manage references.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/joe-antognini/zoia',
    author='Joseph Antognini',
    author_email='joe.antognini@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'bibtexparser>=1.2.0',
        'click>=7.1.2',
        'feedparser>=5.2.1',
        'halo>=0.0.30',
        'isbnlib>=3.10.3',
        'pyyaml>=5.3.1',
        'requests>=2.24.0',
    ],
    entry_points={
        'console_scripts': ['zoia=zoia.cli:zoia'],
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
