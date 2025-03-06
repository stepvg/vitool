# -*- coding: utf-8 -*-

import pathlib, zipfile, tarfile
import logging, urllib, requests, http

from tqdm import tqdm
from .profiling import Verbose, TimeitFunc, ArgsResFunc


logger = logging.getLogger(__name__)
verbose = Verbose(logger)



def download(url, path='', extract_to=True, redownload=False, quiet=False, https=None):
	with verbose.quiet(quiet):
		if https is None:
			https = Https()
		url, file_path = GetLink.and_file_path(url, path, redownload, quiet, https=https)
		download_to(file_path, url, redownload, https=https)
		if extract_to is False or extract_to is None:
			return file_path
		if extract_to is True:
			extract_to = None
		ex = Extract(file_path, extract_to, reextract=redownload)
		return ex.extract_path



def download_to(file_path, url, redownload=False, quiet=False, https=None):
	file_path = pathlib.Path(file_path).expanduser()
	with verbose.quiet(quiet):
		if not redownload and file_path.exists():
			logger.info('%s already exists!' % file_path)
			return
		file_path.parent.mkdir(parents=True, exist_ok=True)
		logger.info('Downloading %s ...' % url)
		if https is None:
			https = Https()
		response = https.query('get', url)
		https.download(response, file_path)
		logger.info('%s downloaded' % file_path)



class Extract:
	
	#~ @ArgsResFunc(logger.warning)
	#~ @TimeitFunc()
	def __init__(self, file_path, extract_path=None, reextract=False, quiet=False):
		file_path = pathlib.Path(file_path).expanduser()
		with verbose.quiet(quiet):
			if extract_path is None:
				self.extract_path = file_path.parent
			else:
				self.extract_path = pathlib.Path(extract_path).expanduser()
			if not self.unzip(file_path, self.extract_path, reextract):
				self.untar(file_path, self.extract_path, reextract)
	
	def tqdm(self, items):
		if verbose.is_quiet():
			return items
		return tqdm(items, desc='Extracted', total=len(items), mininterval=2, unit="items")
	
	def unzip(self, file_path, extract_path, reextract=False):
		try:
			with zipfile.ZipFile(file_path) as csf:
				logger.info('Extracting %s ...' % file_path)
				extracted_count = 0
				for entry_path in self.tqdm(csf.infolist()):
					try:
						entry_path.filename = entry_path.filename.encode('cp437').decode('cp866')
					except UnicodeEncodeError:
						pass
					extract_object = extract_path / entry_path.filename
					if not extract_object.exists() or reextract:
						csf.extract(entry_path, extract_path)
						extracted_count += 1
				logger.info('Extracted %d entry to %s' % (extracted_count, extract_path) )
		except zipfile.BadZipFile:
			return False
		return True

	def untar(self, file_path, extract_path, reextract=False):
		""" gzip, bzip2, lzma"""
		try:
			with tarfile.open(file_path) as csf:
				logger.info('Extracting %s ...' % file_path)
				extracted_count = 0
				for entry_path in self.tqdm(csf.getmembers()):
					extract_object = extract_path / entry_path.name
					if not extract_object.exists() or reextract:
						csf.extract(entry_path, extract_path)
						extracted_count += 1
				logger.info('Extracted %d entry to %s' % (extracted_count, extract_path) )
		except tarfile.ReadError:
			return False
		return True



class YandexDisk:
	
	def __init__(self, url, https=None):
		self.https = https
		if isinstance(url, urllib.parse.ParseResult):
			self.urlparse = url
		else:
			self.urlparse = urllib.parse.urlparse( url )
		urlpath = pathlib.Path(self.urlparse.path)
		self.parts = urlpath.parts
		if self.parts[1] != 'd' or len(self.parts) < 3:
			raise ValueError('URL not from Yandex disk!', url)
	
	def gen_name(self):
		file_name = pathlib.Path(self.parts[-1])
		if not file_name.suffix:
			file_name = file_name.with_suffix('.zip')
		return str(file_name)

	def for_download(self):
		if len(self.parts) == 3:
			keys = dict(public_key=self.urlparse.geturl())
		else:
			url_key = ('',) + self.parts[1:3]
			ya_path = ('',) + self.parts[3:]
			url_key = self.urlparse._replace(path='/'.join(url_key)).geturl()
			keys = dict(public_key=url_key, path='/'.join(ya_path) )
		base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
		if self.https is None:
			self.https = Https()
		response = self.https.query('get', base_url + urllib.parse.urlencode(keys) )
		ans = response.json()
		href_parsed = urllib.parse.urlparse( ans['href'] )
		for k, v in urllib.parse.parse_qs( href_parsed.query ).items():
			ans[k] = v[0]
		return ans



class GetLink:

	@classmethod
	#~ @ArgsResFunc()
	#~ @TimeitFunc(logger.warning)
	def and_file_path(Cls, url, path, redownload=False, quiet=False, https=None):
		full_path = pathlib.Path(path).expanduser().resolve()
		urlparse = urllib.parse.urlparse( url )
		with verbose.quiet(quiet):
			try:
				ya_disk = YandexDisk( urlparse, https=https )
			except ValueError:
				pass
			else:
				file_path = full_path / ya_disk.gen_name()
				if not redownload and file_path.exists():
					logger.info('%s already exists!' % file_path)
					return None, file_path
				fordwn = ya_disk.for_download()
				if fordwn.get('fsize'):
					file_path = full_path / fordwn['filename']
					if not redownload and file_path.exists():
						logger.info('%s already exists!' % file_path)
						return None, file_path
				return fordwn['href'], file_path
			return url, full_path / pathlib.Path(urlparse.path).name



class Https:
	
	chunk_size = 512*1024
	cookies_file_path = pathlib.Path('~/.cache').expanduser() / __name__  / 'cookies.txt'

	def __init__(self, user_agent=None, use_cookies=True, proxy=None, https=None):
		if isinstance(https, Https):
			self.session = https.session
			self.use_cookies = https.use_cookies
			return
		self.use_cookies = use_cookies
		self.session = requests.session()
		if user_agent is None:
			user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0'
		self.session.headers.update({"User-Agent": user_agent})
		if self.use_cookies:
			self.load_cookies()
		if proxy is not None:
			self.session.proxies = {"https": proxy, "http": proxy}

	def query(self, mode, url, **kwargs):
		response = getattr(self.session, mode)(url, stream=True, verify=True, **kwargs)
		response.raise_for_status()
		if self.use_cookies:
			self.save_cookies()
		return response

	def download(self, response, file_path):
		if verbose.is_quiet():
			with open(file_path, 'wb') as f:
				for chunk in response.iter_content(chunk_size=self.chunk_size):
					f.write(chunk)
			return
		total = response.headers.get('Content-length')
		if total is not None:
			total = int(total)
		man_pb = tqdm(
				desc='Downloaded',
				total=total,
				mininterval=2,
				unit="B",
				unit_scale=True)
		with man_pb as pbar:
			pbar.set_postfix(file=file_path.name, refresh=False)
			with open(file_path, 'wb') as f:
				for chunk in response.iter_content(chunk_size=self.chunk_size):
					f.write(chunk)
					pbar.update(len(chunk))
					#~ except requests.exceptions.ChunkedEncodingError as er: pass

	def load_cookies(self):
		if self.cookies_file_path.exists():
			cookies = http.cookiejar.MozillaCookieJar(self.cookies_file_path)
			cookies.load()
			self.session.cookies.update(cookies)

	def save_cookies(self):
		if not self.cookies_file_path.exists():
			self.cookies_file_path.parent.mkdir(parents=True, exist_ok=True)
		cookies = http.cookiejar.MozillaCookieJar(self.cookies_file_path)
		for cookie in self.session.cookies:
			cookies.set_cookie(cookie)
		cookies.save()


