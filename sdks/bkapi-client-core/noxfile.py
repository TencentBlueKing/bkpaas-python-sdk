from pathlib import Path

import nox

nox.options.default_venv_backend = "venv"

ROOT = Path(__file__).parent.resolve()
ALL_PYTHON = ["3.6", "3.7"]
REQUESTS_VERSIONS = ["2.20", "2.26"]
REQUIREMENTS_PATH = ROOT / "requirements.txt"


def _ensure_requirements_exported(session) -> Path:
    if REQUIREMENTS_PATH.exists():
        return REQUIREMENTS_PATH

    session.error("requirements.txt not found. Run `nox -s export_deps` first.")
    return REQUIREMENTS_PATH


def install_with_constraints(session, *args: str, **kwargs) -> None:
    """
    Install packages constrained by exported requirements.txt.

    This function is a wrapper for nox.sessions.Session.install. It
    invokes pip to install packages inside of the session's virtualenv.
    Additionally, pip is passed a constraints file generated from
    Poetry's lock file, to ensure that the packages are pinned to the
    versions specified in poetry.lock.
    """
    requirements = _ensure_requirements_exported(session)
    session.install(
        f"--constraint={requirements}",
        "--use-deprecated=legacy-resolver",
        *args,
        **kwargs,
    )


@nox.session(python="3.11", reuse_venv=True)
def export_deps(session):
    """Export dependencies from Poetry to requirements.txt. When running tests later, the
    requirements.txt file will be used as a constraints file to ensure that the same version
    of each dependency is used.
    """
    session.run("python", "-m", "ensurepip", "--upgrade")
    session.install("poetry")
    session.run("poetry", "self", "add", "poetry-plugin-export@latest")
    session.run(
        "poetry",
        "export",
        "--with=dev",
        "--format=requirements.txt",
        "--without-hashes",
        f"--output={REQUIREMENTS_PATH}",
    )


@nox.session(reuse_venv=True)
@nox.parametrize("python", ALL_PYTHON)
def tests(session):
    session.run("python", "-m", "ensurepip", "--upgrade")
    session.run("python", "-m", "pip", "install", "--upgrade", "pip<24", "setuptools<68", "wheel")
    # Install main dependencies
    install_with_constraints(
        session,
        "-v",
        "requests",
        "curlify",
        "typing-extensions",
        "six",
    )
    # Install test dependencies
    install_with_constraints(
        session,
        "pytest",
        "pytest-django",
        "pytest-mock",
        "requests-mock",
        "Faker",
        "django",
        "prometheus-client",
    )

    for version in REQUESTS_VERSIONS:
        session.install(f"requests=={version}")
        session.run("pytest", "tests", *session.posargs)
