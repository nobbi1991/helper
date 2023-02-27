import typing

import setuptools


def load_req() -> typing.List[str]:
	with open('requirements.txt') as f:
		return f.readlines()


VERSION = "1.0.0"

setuptools.setup(
	name="nose_helper",
	version=VERSION,
	author="Seuling N.",
	description="build helper",
	long_description="helper for building and checking projects",
	packages=setuptools.find_packages(exclude=["tests*"]),
	install_requires=load_req(),
	python_requires=">=3.10",
	license="Apache License 2.0"
)
