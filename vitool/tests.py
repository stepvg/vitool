# -*- coding: utf-8 -*-

import unittest
import pathlib
from .rfile import GetLink


class Test_rfile(unittest.TestCase):

	def setUp(self):
		# Создаем объекты для тестирования
		pass
	

	def test_file_name_1_from_yandex_url(self):
		in_url = 'https://disk.yandex.ru/d/XXX.csv'
		url, path_file = GetLink.and_file_path(in_url, './')
		self.assertEqual( url, in_url )
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'XXX.csv' )

	def test_file_name_2_from_yandex_url(self):
		in_url = 'https://storage.yandexcloud.net/d/XXX.csv'
		url, path_file = GetLink.and_file_path(in_url, '')
		self.assertEqual( url, in_url )
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'XXX.csv' )

	def test_file_name_3_from_yandex_url(self):
		in_url = 'https://storage.yandexcloud.net/d/XXX.csv'
		url, path_file = GetLink.and_file_path(in_url, 'TTT')
		self.assertEqual( url, in_url )
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'TTT/XXX.csv'  )

	def test_file_name_4_from_yandex_url(self):
		pass
		#~ x = GetLink.and_file_path('https://disk.yandex.ru/d/XXX', 'TTT')
		#~ x = GetLink.and_file_path('https://storage.yandexcloud.net/d/XXX', './')

	#~ def test_file_name_1_from_google_url(self):
		#~ in_url = 'https://drive.google.com/file/d/1m63AHiVZ'
		#~ url, path_file = GetLink.and_file_path(in_url, 'TTT')
		#~ self.assertEqual( url, in_url )
		#~ self.assertEqual( path_file, pathlib.Path('').resolve() / 'TTT/1m63AHiVZ.zip'  )

	#~ def test_file_name_2_from_google_url(self):
		#~ in_url = 'https://drive.google.com/file/d/1m63AHiVZ/view?usp=drive_link'
		#~ url, path_file = GetLink.and_file_path(in_url, 'TTT')
		#~ self.assertEqual( url, in_url )
		#~ self.assertEqual( path_file, pathlib.Path('').resolve() / 'TTT/1m63AHiVZ.zip'  )

if __name__ == '__main__':
	unittest.main()
	

