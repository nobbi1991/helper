import json

import requests


class VersionCheck:

	def __init__(self, current_version: str, pypi_pkg_name: str):
		self.current_version = current_version
		self.pypi_pkg_name = pypi_pkg_name

	def __get_pypi_version(self) -> str:
		result = requests.get(f"https://pypi.org/pypi/{self.pypi_pkg_name}/json")
		if not result.status_code == 200:
			raise Exception("no response!")

		return json.loads(result.text)["info"]["version"]

	@staticmethod
	def __str_to_version(version: str) -> int:
		version_parts = version.split(".")

		if not len(version_parts) == 3 or not all([value.isdigit() for value in version_parts]):
			raise AttributeError(f"The format of the given version ({version}) is not correct. Version must have the following format X.X.X")

		return int(version_parts[0]) * 1000000 + int(version_parts[1]) * 1000 + int(version_parts[2])

	def check_version(self):
		pypi_representation = self.__str_to_version(self.__get_pypi_version())
		branch_representation = self.__str_to_version(self.current_version)

		return 0 if branch_representation > pypi_representation else -1
