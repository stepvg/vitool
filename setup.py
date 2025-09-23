# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages
from pathlib import Path

PKG_NAME = 'vitool'
GITHUB_URL = f'https://github.com/stepvg/{PKG_NAME}'

def get_version():
	content = Path(f'{PKG_NAME}/__init__.py').read_text(encoding='utf-8')
	return re.search(r"__version__ = '(.+)'", content).group(1)

if __name__ == '__main__':

	readme = Path('README.md').read_text(encoding='utf-8')

	setup(
		license='GPLv3',
		name='vitool',
		author='stepvg',
		author_email='vyac.st@gmail.com',
		description='A simple tools.',
		install_requires=['tqdm', 'requests>=2'],
		classifiers=[
			'Programming Language :: Python :: 3',
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
			'Operating System :: OS Independent',
			'Topic :: System :: Monitoring',
			'Topic :: Software Development :: Libraries',
			'Topic :: Software Development :: Quality Assurance',
			'Topic :: Utilities',
		],
		keywords=[
			PKG_NAME,
			'timer',
			'profiling',
			'logging',
			'download',
			'http',
			'file extraction',
			'archives',
			'utils',
			'timeit',
		],
		project_urls={
			'Homepage': GITHUB_URL,
			'Source': GITHUB_URL,
			'Bug Tracker': f'{GITHUB_URL}/issues',
			'Documentation': f'{GITHUB_URL}#readme',
		},
		version=get_version(),
		long_description=readme,
		long_description_content_type='text/markdown',
		url=GITHUB_URL,
		packages=find_packages(),
	)
