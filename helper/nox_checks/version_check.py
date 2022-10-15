import argparse
import json
import sys

import requests


class VersionCheck:
	"""Checker to asure that version was updated."""

	def __init__(self, current_version: str, pypi_pkg_name: str) -> None:
		"""Create checker.

		:param current_version: Version of the current branch. E.g 1.1.0
		:param pypi_pkg_name: Name of the PyPi package
		"""
		self.current_version = current_version
		self.pypi_pkg_name = pypi_pkg_name

	def __get_pypi_version(self) -> str:
		"""Get the newest version from PyPi.

		:return: Returns the newest version which is released on PyPi
		"""
		result = requests.get(f"https://pypi.org/pypi/{self.pypi_pkg_name}/json")
		if not result.status_code == 200:
			raise Exception("no response!")

		return json.loads(result.text)["info"]["version"]

	@staticmethod
	def __str_to_version(version: str) -> int:
		"""Get a integer representation for a given version as string.

		:param version: Version as string. E.g. 1.1.0
		:return: A integer representation of the given version
		"""
		version_parts = version.split(".")

		if not len(version_parts) == 3 or not all([value.isdigit() for value in version_parts]):
			raise AttributeError(f"The format of the given version ({version}) is not correct. Version must have the following format X.X.X")

		return int(version_parts[0]) * 1000000 + int(version_parts[1]) * 1000 + int(version_parts[2])

	def check_version(self) -> int:
		"""Check if version of the current branch is higher than the newest PyPi version.

		:return: 0 if branch version is higher than PyPi version. If not -1
		"""
		pypi_version = self.__get_pypi_version()
		branch_version = self.current_version

		print(f"PyPi version: {pypi_version} | branch version: {branch_version}")

		return 0 if self.__str_to_version(branch_version) > self.__str_to_version(pypi_version) else -1


if __name__ == "__main__":
	PARSER = argparse.ArgumentParser()
	PARSER.add_argument("-bv", "--branch_version")
	PARSER.add_argument("-pn", "--pypi_name")
	ARGS = PARSER.parse_args()
	sys.exit(VersionCheck(ARGS.branch_version, ARGS.pypi_name).check_version())
