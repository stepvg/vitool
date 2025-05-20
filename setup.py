# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md', 'r') as readme_file:
	readme = readme_file.read()


if __name__ == '__main__':
	setup(
		name='vitool',
		version='1.0.11',
		author='stepvg',
		author_email='stepvg@ya.ru',
		description='A simple tools.',
		long_description=readme,
		long_description_content_type='text/markdown',
		url='https://github.com/stepvg/vitool',
		packages=find_packages(),
		install_requires=['tqdm', 'requests>=2'],
		classifiers=[
			'Programming Language :: Python :: 3.7',
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		],
	)
