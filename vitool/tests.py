# -*- coding: utf-8 -*-

import unittest
import pathlib

from .rfile import YandexDisk, GetLink


class Test_rfile(unittest.TestCase):

	def setUp(self):
		# Создаем объекты для тестирования
		pass
	

	def test_file_name_1_from_simple_url(self):
		in_url = 'http://musl.libc.org/releases/musl-1.2.5.tar.gz.asc'
		url, path_file = GetLink.and_file_path(in_url, '')
		self.assertEqual( url, in_url )
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'musl-1.2.5.tar.gz.asc' )

	def test_file_name_1_from_yandex_url(self):
		in_url = 'https://disk.yandex.ru/d/vitool_test.txt'
		file_name = YandexDisk( in_url).gen_name()
		self.assertEqual( file_name, 'vitool_test.txt' )

	def test_file_name_2_from_yandex_url(self):
		in_url = 'https://disk.yandex.com/d/pfjItPdGt6r-Ww'				# vitool_test.txt
		ydsk = YandexDisk(in_url)
		self.assertEqual( ydsk.gen_name(), 'pfjItPdGt6r-Ww.zip' )
		fordwn = ydsk.for_download()
		self.assertEqual( fordwn['fsize'], '11' )
		self.assertEqual( fordwn['filename'], 'vitool_test.txt')

	def test_file_name_3_from_yandex_url(self):
		in_url = 'https://disk.yandex.com/d/lJ3BFEjOSbKIEg'				# vitool_test/
		url, path_file = GetLink.and_file_path(in_url, './')
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'lJ3BFEjOSbKIEg.zip' )

	def test_file_name_4_from_yandex_url(self):
		in_url = 'https://disk.yandex.com/d/lJ3BFEjOSbKIEg/vitool_test.txt'	# vitool_test/vitool_test.txt
		url, path_file = GetLink.and_file_path(in_url, 'TTT')
		self.assertEqual( path_file, pathlib.Path('').resolve() / 'TTT' / 'vitool_test.txt'  )

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
	

