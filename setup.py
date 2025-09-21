# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from pathlib import Path


if __name__ == '__main__':

	readme = ( Path() / 'README.md' ).read_text(encoding='UTF-8')

	setup(
		license='GPLv3',
		name='vitool',
		version='1.0.12',
		author='stepvg',
		author_email='vyac.st@gmail.com',
		description='A simple tools.',
		long_description=readme,
		long_description_content_type='text/markdown',
		url='https://github.com/stepvg/vitool',
		packages=find_packages(),
		install_requires=['tqdm', 'requests>=2'],
		classifiers=[
			'Programming Language :: Python :: 3',
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
			'Operating System :: OS Independent',
			'Topic :: System :: Monitoring',
			'Topic :: Software Development :: Libraries',
			'Topic :: Software Development :: Quality Assurance',
			'Topic :: Software Development :: Tools',
			'Topic :: Utilities',
		],
		project_urls={
			'Homepage': 'https://github.com/stepvg/vitool',
			'Source': 'https://github.com/stepvg/vitool',
			'Bug Tracker': 'https://github.com/stepvg/vitool/issues',
			'Documentation': 'https://github.com/stepvg/vitool#readme',
		},
		keywords=[
			'vitool',
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
	)
