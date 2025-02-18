# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md', 'r') as readme_file:
	readme = readme_file.read()


if __name__ == '__main__':
	setup(
		name='vitool',
		version='1.0.7',
		author='stepvg',
		author_email='stepvg@ya.ru',
		description='A simple tools.',
		long_description=readme,
		long_description_content_type='text/markdown',
		url='https://github.com/your_package/homepage/',
		packages=find_packages(),
		#~ install_requires=['tqdm', 'seaborn', 'requests>=2'],
		classifiers=[
			'Programming Language :: Python :: 3.7',
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		],
	)
