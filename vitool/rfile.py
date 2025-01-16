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
		url, file_path = GetLink.and_file_path(url, path, redownload, https=https)
		download_to(file_path, url, redownload, https=https)
		if extract_to is False or extract_to is None:
			return file_path
		if extract_to is True:
			ex = Extract(file_path)
		else:
			ex = Extract(file_path, extract_to)
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
	def __init__(self, file_path, extract_path=None, quiet=False):
		with verbose.quiet(quiet):
			if extract_path is None:
				if file_path.suffix:
					self.extract_path = file_path.with_suffix('')
				else:
					self.extract_path = file_path.with_name(file_path.name + '_dir')
			else:
				self.extract_path = pathlib.Path(extract_path).expanduser()
			if self.extract_path.exists():
				logger.info('%s already exists!' % self.extract_path)
				return
			if not self.unzip(file_path, self.extract_path):
				self.untar(file_path, self.extract_path)
	
	def tqdm(self, items):
		if verbose.is_quiet():
			return items
		return tqdm(items, desc='Extracted', total=len(items), mininterval=2, unit="items")
	
	def unzip(self, file_path, extract_path):
		try:
			with zipfile.ZipFile(file_path) as csf:
				logger.info('Extracting %s ...' % file_path)
				for entry_path in self.tqdm(csf.infolist()):
					try:
						entry_path.filename = entry_path.filename.encode('cp437').decode('cp866')
					except UnicodeEncodeError:
						pass
					csf.extract(entry_path, extract_path)
				logger.info('Extracted to %s' % extract_path)
		except zipfile.BadZipFile:
			return False
		return True

	def untar(self, file_path, extract_path):
		""" gzip, bzip2, lzma"""
		try:
			with tarfile.open(file_path) as csf:
				logger.info('Extracting %s ...' % file_path)
				for entry_path in self.tqdm(csf.getmembers()):
					csf.extract(entry_path, extract_path)
				logger.info('Extracted to %s' % extract_path)
		except tarfile.ReadError:
			return False
		return True



class GetLink:

	@classmethod
	def and_file_path(Cls, url, path, redownload=False, https=None):
		file_url, file_path = Cls.yandex( url, path, https=https )
		if file_url:
			return file_url, file_path
		urlparse = urllib.parse.urlparse( url )
		return url, full_path / pathlib.Path(urlparse.path).name

	@classmethod
	#~ @ArgsResFunc()
	#~ @TimeitFunc(logger.warning)
	def yandex(Cls, url, path='', https=None):
		urlparse = urllib.parse.urlparse( url )
		#~ import pprint; pprint.pprint(urlparse)
		if 'yandex' not in urlparse.netloc:
			return None, path
		urlpath = pathlib.Path(urlparse.path)
		parts = urlpath.parts
		if len(parts) < 3:
			return None, path
		full_path = pathlib.Path(path).expanduser().resolve()
		file_path = full_path / urlpath.name
		if not urlpath.suffix:
			file_path = file_path.with_suffix('.zip')
		if len(parts) == 3:
			if urlpath.suffix:
				return url, file_path
			keys = dict(public_key=url)
		else:
			url_path = urlpath.parents[len(parts) - 4]
			url = urlparse._replace(path=str(url_path)).geturl()
			ya_path = '/' + str(urlpath.relative_to(url_path))
			keys = dict(public_key=url, path=ya_path)
		base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
		if https is None:
			https = Https()
		response = https.query('get', base_url + urllib.parse.urlencode(keys) )
		return response.json()['href'], file_path



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


