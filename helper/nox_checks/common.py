import collections
import pathlib
import sys
import typing

import nox
import nox.command

nox.options.error_on_external_run = True
nox.options.error_on_missing_interpreters = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = []

VENV_PREPARED = ""


class NoxBase:

	def __init__(self, session: nox.Session, project_name=None, changelog_path: typing.Optional[pathlib.Path] = None):
		self._session = session
		self._base_dir = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
		self._project_name = project_name if project_name else self._base_dir.name
		self._changelog_path = changelog_path
		print(self._project_name)
		self._silent = False
		self._python_executable: str = sys.executable if isinstance(session.virtualenv, nox.sessions.PassthroughEnv) else "python"

	def _install_requirements(self):
		"""Install requirement files into venv but only if it's not a pass-through venv."""
		global VENV_PREPARED  # pylint: disable=global-statement
		if not isinstance(self._session.virtualenv, nox.sessions.PassthroughEnv) and VENV_PREPARED != self._session.virtualenv.location:
			self._session.install("-U", "pip", silent=self._silent)
			self._session.install("-U", "wheel", silent=self._silent)
			req_list = []
			for req in ["requirements.txt", "helper/requirements.txt"]:
				req_list.append("-r")
				req_list.append(req)
			self._session.install("-U", *req_list, silent=self._silent)

		if not VENV_PREPARED:
			if isinstance(self._session.virtualenv, nox.sessions.PassthroughEnv):
				VENV_PREPARED = sys.executable
			else:
				VENV_PREPARED = self._session.virtualenv.location

	def pylint(self, dir_names: list[str] = None, rcfile: pathlib = None, jobs: int = 8) -> None:

		if not dir_names:
			dir_names = [self._project_name, "tests"]

		if not rcfile:
			rcfile = self._base_dir / "helper/helper/nox_checks/config/.pylintrc"

		self._install_requirements()
		args = dir_names
		args.append(f"--rcfile={rcfile}")
		args.append(f"--jobs={jobs}")
		print(args)
		self._session.run(self._python_executable, "-m", "pylint", *args, silent=self._silent)

	def coverage(self):
		"""Run coverage."""
		self._install_requirements()

		run_args = ["--rcfile=.coveragerc"]
		html_args = ["--skip-covered", "--fail-under=100"]
		with self._session.chdir("tests"):
			self._session.run(self._python_executable, "-m", "coverage", "run", *run_args, "run_unittest.py", silent=self._silent)
			try:
				self._session.run(self._python_executable, "-m", "coverage", "html", *html_args, silent=self._silent)
			except nox.command.CommandFailed:
				result_path = "tests/htmlcov/index.html"
				self._session.warn(f"Coverage result: {self._base_dir.joinpath(result_path).as_uri()}")
				raise

	def version_check(self, pypi_name: typing.Optional[str] = None, version_file: typing.Optional[str] = None):
		"""Check if version is updated"""
		self._install_requirements()

		pypi_name = pypi_name if pypi_name else self._project_name
		version_file = version_file if version_file else self._base_dir / self._project_name / "__version__.py"

		version_data = {}
		with open(version_file, "r", encoding="utf-8") as file:
			exec(file.read(), version_data)
		branch_version = version_data.get("__version__", "0.0.0")

		self._session.run("python", "helper/helper/nox_checks/version_check.py", "--branch_version", f"{branch_version}", "--pypi_name", f"{pypi_name}", "--changelog_path", f"{self._changelog_path}")


def run_combined_sessions(session: nox.Session, sub_sessions: list[tuple[str, collections.abc.Callable[[], None]]]) -> None:
	"""Run combined nox sessions.

	:param session: nox session that should run the sub sessions
	:param sub_sessions: a list of a pair of name and sub session functions that should be executed
	:raises nox.command.CommandFailed: if one or more sub-sessions fail
	"""
	errors = []
	for name, sub_session in sub_sessions:
		try:
			session.warn(f"Running sub-session {name}")
			sub_session()
		except Exception:  # pylint: disable=broad-except
			errors.append(name)
	if errors:
		session.error(str(errors))
