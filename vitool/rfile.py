# -*- coding: utf-8 -*-

import pathlib, zipfile, tarfile
import logging, urllib, requests, http
from tqdm import tqdm
from .ctrl import Verbose


logger = logging.getLogger(__name__)
verbose = Verbose(logger)


def download(url, file_path='./', extract_to=True, find_url=False, redownload=False, quiet=False, https=None):
	with verbose.quiet(quiet):
		if https is None:
			https = Https()
		url, file_path = GetLink.and_file_path(url, file_path, redownload, find_url, https=https)
		if url is not None:
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
		https.download(https.query('get', url), file_path)
		logger.info('%s downloaded' % file_path)


class Extract:
	
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
	def and_file_path(Cls, url, file_path, redownload=False, find_url=False, https=None):
		urlparse = urllib.parse.urlparse( url )
		out_path = pathlib.Path(file_path).expanduser().resolve()
		urlpath = pathlib.Path(urlparse.path)
		if isinstance(file_path, str) and file_path[-1:] == '/':
			out_path = out_path / urlpath.name
		if not redownload and out_path.exists():
			logger.info('%s already exists!' % out_path)
			return None, out_path
		if find_url or 'yandex' in urlparse.netloc and not urlpath.suffix:
			return Cls.yandex( url, https=https ), out_path
		return url, out_path

	@classmethod
	def yandex(Cls, url, https=None):
		base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
		if https is None:
			https = Https()
		response = https.query('get', base_url + urllib.parse.urlencode(dict(public_key=url)) )
		return response.json()['href']


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


