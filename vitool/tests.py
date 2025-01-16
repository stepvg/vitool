# -*- coding: utf-8 -*-

import unittest
import pathlib
from .rfile import GetLink


class Test_rfile(unittest.TestCase):

	def setUp(self):
		# Создаем объекты для тестирования
		pass
	

	def test_create_file_name_from_url(self):
		in_url = 'https://disk.yandex.ru/d/XXX.csv'
		url, path_file = GetLink.and_file_path(in_url, './')
		self.assertEqual( url, in_url )
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'XXX.csv' )

	def test_file_defined_and_exists(self):
		in_url = 'https://storage.yandexcloud.net/d/XXX.csv'
		url, path_file = GetLink.and_file_path(in_url, '')
		self.assertEqual( url, in_url )
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'XXX.csv' )

	def test_file_defined_and_not_exists(self):
		in_url = 'https://storage.yandexcloud.net/d/XXX.csv'
		url, path_file = GetLink.and_file_path(in_url, 'TTT')
		self.assertEqual( url, in_url )
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'TTT/XXX.csv'  )

	def test_file_defined_and_(self):
		#~ x = GetLink.and_file_path('https://disk.yandex.ru/d/XXX', 'TTT')
		#~ x = GetLink.and_file_path('https://storage.yandexcloud.net/d/XXX', './')
		pass

if __name__ == '__main__':
	unittest.main()
	

