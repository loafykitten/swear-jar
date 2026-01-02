"""API client for swear-jar service."""

import urllib.error
import urllib.request

from logging_setup import get_logger

log = get_logger(__name__)


class SwearAPIClient:
	"""Client for reporting swears to the swear-jar service API."""

	def __init__(self, base_url: str, api_key: str):
		"""Initialize API client.

		Args:
			base_url: Base URL of the swear-jar service (e.g., http://localhost:3000)
			api_key: API key for authentication
		"""
		self.base_url = base_url.rstrip('/')
		self.api_key = api_key

	def report_swears(self, count: int) -> bool:
		"""Report swear count to the API.

		Makes POST request to {base_url}/api/swears?pricePerSwear={price}&by={count}

		Args:
			count: Number of swears to report.

		Returns:
			True if request succeeded, False otherwise.
		"""
		if count <= 0:
			return True

		url = f'{self.base_url}/api/swears?pricePerSwear=0&by={count}'

		headers = {
			'API-KEY': self.api_key,
			'Content-Type': 'application/json',
		}

		log.info(f'Reporting {count} swear(s) to API: {url}')

		try:
			request = urllib.request.Request(
				url,
				method='POST',
				headers=headers,
				data=b'',
			)

			with urllib.request.urlopen(request, timeout=10) as response:
				status = response.status
				body = response.read().decode('utf-8')

				if status == 200:
					log.info(f'API response ({status}): {body}')
					return True
				else:
					log.warning(f'API returned non-200 status: {status} - {body}')
					return False

		except urllib.error.HTTPError as e:
			log.error(f'HTTP error reporting swears: {e.code} - {e.reason}')
			return False
		except urllib.error.URLError as e:
			log.error(f'URL error reporting swears: {e.reason}')
			return False
		except Exception as e:
			log.exception(f'Unexpected error reporting swears: {e}')
			return False
