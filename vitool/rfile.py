# -*- coding: utf-8 -*-

import pathlib, zipfile, tarfile
import logging, urllib, requests, http
import typing as tp

from tqdm import tqdm
from . import profiling as pfl


logger = logging.getLogger(__name__)
verbose = pfl.Verbose(logger)



class Https:
	"""
	Wrapper around requests.Session for HTTP/HTTPS requests.

	Provides:
	- Custom User-Agent
	- Optional cookie persistence
	- Optional proxy support
	- Ability to clone from another Https instance
	"""

	chunk_size = 512*1024
	cookies_file_path = pathlib.Path('~/.cache').expanduser() / __name__  / 'cookies.txt'

	def __init__(
			self,
			user_agent: str = 'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0',
			use_cookies: bool = True,
			proxy: str = '',
			https: tp.Optional["Https"] = None
		):
		"""
		Initialize the HTTPS helper.

		Args:
			user_agent: Custom User-Agent string; if None, defaults to Firefox.
			use_cookies: Whether to use persistent cookies stored on disk.
			proxy: Optional proxy server (applies to both HTTP and HTTPS).
			https: If another Https instance is provided, clone its session.

		Notes:
			If `https` is given, the session and cookie settings are copied.
			Otherwise, a new requests.Session is created.
		"""
		if isinstance(https, Https):
			self.session = https.session
			self.use_cookies = https.use_cookies
			return
		self.use_cookies = use_cookies
		self.session = requests.session()
		self.session.headers.update({"User-Agent": user_agent})
		if self.use_cookies:
			self.load_cookies()
		if proxy:
			self.session.proxies = {"https": proxy, "http": proxy}


	def query(self, mode: str, url: str, **kwargs) -> requests.Response:
		"""
		Send an HTTP request using `mode` (e.g. 'get', 'post') and return the response.

		Raises:
			HTTPError if request was unsuccessful.
		"""
		response = getattr(self.session, mode)(url, stream=True, verify=True, **kwargs)
		response.raise_for_status()
		if self.use_cookies:
			self.save_cookies()
		return response


	def download(self, response: requests.Response, file_path: pathlib.Path) -> None:
		"""
		Download content from a streaming response to a file, with progress bar
		unless in quiet mode.

		Args:
			response: Response object with streamed content.
			file_path: Destination file path.
		"""
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


	def load_cookies(self) -> None:
		"""
		Load cookies from the cache file into the session, if exists.
		"""
		if self.cookies_file_path.exists():
			cookies = http.cookiejar.MozillaCookieJar(self.cookies_file_path)
			cookies.load()
			self.session.cookies.update(cookies)


	def save_cookies(self) -> None:
		"""
		Save current session cookies into the cache file.
		"""
		if not self.cookies_file_path.exists():
			self.cookies_file_path.parent.mkdir(parents=True, exist_ok=True)
		cookies = http.cookiejar.MozillaCookieJar(self.cookies_file_path)
		for cookie in self.session.cookies:
			cookies.set_cookie(cookie)
		cookies.save()



def download(
		url: str,
		path: str = "",
		extract_to: None | str | bool = True,
		redownload: bool = False,
		quiet: bool = False,
		https: None | Https = None
	) -> pathlib.Path:
	"""
	Download a file from `url` to `path`, optionally extract it.

	If `redownload` is False and the file already exists, reuses it.
	If `extract_to` is False or None, does not extract; if True, extracts
	to the same folder; if a path is provided, extracts to that path.

	Args:
		url: The URL to download.
		path: Destination directory or file path.
		extract_to: Whether to extract archive; can be bool or path.
		redownload: Force re-download even if file exists.
		quiet: Suppress progress / info output.
		https: Optional HTTPS helper instance.

	Returns:
		The path to the downloaded (and possibly extracted) file or directory.
	"""
	with verbose.quiet(quiet):
		if https is None:
			https = Https()
		url, file_path = GetLink.and_file_path(url, path, redownload, quiet, https=https)
		download_to(file_path, url, redownload, https=https)
		# If extraction not desired, return the downloaded file path
		if extract_to is False or extract_to is None:
			return file_path
		# if extract_to is True, treat it as default (same folder)
		if extract_to is True:
			extract_to = None
		ex = Extract(file_path, extract_to, reextract=redownload)
		return ex.extract_path



def download_to(
		file_path: str,
		url: str,
		redownload: bool = False,
		quiet: bool = False,
		https: None | Https = None
	) -> pathlib.Path:
	"""
	Download content from `url` and save to `file_path`.

	If `redownload` is False and the target exists, does nothing.

	Args:
		file_path: Local file path (or path-like) to save to.
		url: The URL to fetch.
		redownload: Whether to force download even if file exists.
		quiet: Suppress progress / info output.
		https: Optional HTTPS helper instance.

	Returns:
		The pathlib.Path of the file after download (ensured).
	"""
	file_path = pathlib.Path(file_path).expanduser()
	with verbose.quiet(quiet):
		if not redownload and file_path.exists():
			logger.info('%s already exists!', file_path)
			return
		# ensure parent directory exists
		file_path.parent.mkdir(parents=True, exist_ok=True)
		logger.info('Downloading %s ...', url)
		if https is None:
			https = Https()
		response = https.query('get', url)
		https.download(response, file_path)
		logger.info('%s downloaded', file_path)



class Extract:
	"""
	Handle extraction of zip or tar (gzip, bzip2, lzma) archives.
	"""
	
	#~ @pfl.ArgsResFunc(logger.warning)
	#~ @pfl.TimeitFunc()
	def __init__(
			self,
			file_path: str,
			extract_path: None | str = None,
			reextract: bool = False,
			quiet: bool = False
		):
		"""
		Initialize extraction. Tries unzip first; if fails, tries untar.

		Args:
			file_path: Path to the archive file.
			extract_path: Directory to extract into; defaults to same directory.
			reextract: Whether to overwrite existing files.
			quiet: Suppress progress / info output.
		"""
		file_path = pathlib.Path(file_path).expanduser()
		with verbose.quiet(quiet):
			if extract_path is None:
				self.extract_path = file_path.parent
			else:
				self.extract_path = pathlib.Path(extract_path).expanduser()
			if not self.unzip(file_path, self.extract_path, reextract):
				self.untar(file_path, self.extract_path, reextract)

	
	def tqdm(self, items: tp.Iterable[tp.Any]) -> tp.Iterator[tp.Any]:
		"""
		Wrap items with tqdm progress.

		Args:
			items: Iterable items to iterate over.

		Returns:
			tqdm-wrapped iterable.
		"""
		if verbose.is_quiet():
			return items
		return tqdm(items, desc='Extracted', total=len(items), mininterval=2, unit="items")

	
	def unzip(
			self,
			file_path: pathlib.Path,
			extract_path: pathlib.Path,
			reextract: bool = False
		) -> bool:
		"""
		Extract a zip archive.

		Args:
			file_path: Path to the archive file.
			extract_path: Directory to extract into; defaults to same directory.
			reextract: Whether to overwrite existing files.
		Returns:
			True if extraction succeeded, False otherwise.
		"""
		try:
			with zipfile.ZipFile(file_path) as csf:
				logger.info('Extracting %s ...', file_path)
				extracted_count = 0
				for entry_path in self.tqdm(csf.infolist()):
					# Attempt to fix encoding issues from CP437 -> CP866 if needed
					try:
						entry_path.filename = entry_path.filename.encode('cp437').decode('cp866')
					except UnicodeEncodeError:
						pass
					extract_object = extract_path / entry_path.filename
					if not extract_object.exists() or reextract:
						csf.extract(entry_path, extract_path)
						extracted_count += 1
				logger.info('Extracted %d entry to %s', extracted_count, extract_path )
		except zipfile.BadZipFile:
			return False
		return True


	def untar(
			self,
			file_path: pathlib.Path,
			extract_path: pathlib.Path,
			reextract: bool = False
		) -> bool:
		"""
		Extract a tar archive (gzip, bzip2, lzma).

		Args:
			file_path: Path to the archive file.
			extract_path: Directory to extract into; defaults to same directory.
			reextract: Whether to overwrite existing files.
		Returns:
			True if extraction succeeded, False otherwise.
		"""
		try:
			with tarfile.open(file_path) as csf:
				logger.info('Extracting %s ...', file_path)
				extracted_count = 0
				for entry_path in self.tqdm(csf.getmembers()):
					extract_object = extract_path / entry_path.name
					if not extract_object.exists() or reextract:
						csf.extract(entry_path, extract_path)
						extracted_count += 1
				logger.info('Extracted %d entry to %s', extracted_count, extract_path )
		except tarfile.ReadError:
			return False
		return True



class YandexDisk:
	"""
	Handle download links from Yandex Disk shared URLs.
	"""
	
	def __init__(
			self,
			url: str | urllib.parse.ParseResult,
			https: None | Https = None
		):
		"""
		Initialize YandexDisk helper.

		Args:
			url: Shared URL or parsed URL pointing to Yandex Disk.
			https: Optional HTTPS helper instance.

		Raises:
			ValueError: if URL is not a valid Yandex Disk share link.
		"""
		self.https = https
		if isinstance(url, urllib.parse.ParseResult):
			self.urlparse = url
		else:
			self.urlparse = urllib.parse.urlparse( url )
		urlpath = pathlib.Path(self.urlparse.path)
		self.parts = urlpath.parts
		# Check that path conforms to Yandex Disk shared URL structure
		if self.parts[1] != 'd' or len(self.parts) < 3:
			raise ValueError('URL not from Yandex disk!', url)


	def gen_name(self) -> str:
		"""
		Generate a default filename for the shared resource.

		Returns:
			Filename with .zip extension or the same.
		"""
		file_name = pathlib.Path(self.parts[-1])
		if not file_name.suffix:
			file_name = file_name.with_suffix('.zip')
		return str(file_name)


	def for_download(self) -> dict:
		"""
		Produce URL and metadata for downloading the shared resource.

		Returns:
			A dict with keys such as 'href', 'filename', etc.
		"""
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
		# Parse and rebuild download href
		href_parsed = urllib.parse.urlparse( ans['href'] )
		for k, v in urllib.parse.parse_qs( href_parsed.query ).items():
			ans[k] = v[0]
		return ans



class GetLink:
	"""
	Resolve URL to a direct download link and determine local file path.
	"""

	@classmethod
	#~ @pfl.ArgsResFunc()
	#~ @pfl.TimeitFunc(logger.warning)
	def and_file_path(
			Cls,
			url: str,
			path: str | pathlib.Path,
			redownload: bool = False,
			quiet: bool = False,
			https: None | Https = None
		) -> tuple[ None | str, pathlib.Path]:
		"""
		Determine the download URL and target file path for a given URL.

		If the URL is from Yandex Disk, resolve to an API-based download link.

		Args:
			url: Original URL.
			path: Desired local base path.
			redownload: Whether to ignore existing file.
			quiet: Suppress logging / verbosity.
			https: Optional HTTPS helper for link resolution.

		Returns:
			A tuple (resolved_url or None, file_path). If resolved_url is None
			and file already exists (and redownload is False), path may point
			to existing file.
		"""
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
					logger.info('%s already exists!', file_path)
					return None, file_path
				fordwn = ya_disk.for_download()
				if fordwn.get('fsize'):
					file_path = full_path / fordwn['filename']
					if not redownload and file_path.exists():
						logger.info('%s already exists!', file_path)
						return None, file_path
				return fordwn['href'], file_path
			return url, full_path / pathlib.Path(urlparse.path).name



