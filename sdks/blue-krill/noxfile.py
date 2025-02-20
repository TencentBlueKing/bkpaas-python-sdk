import os
import tempfile

import nox

ALL_PYTHON = ["3.9", "3.10", "3.11"]


# ref: https://stackoverflow.com/questions/59768651/how-to-use-nox-with-poetry
def install_with_constraints(session, *args: str, **kwargs) -> None:
    """
    Install packages constrained by Poetry's lock file.

    This function is a wrapper for nox.sessions.Session.install. It
    invokes pip to install packages inside of the session's virtualenv.
    Additionally, pip is passed a constraints file generated from
    Poetry's lock file, to ensure that the packages are pinned to the
    versions specified in poetry.lock. This allows you to manage the
    packages as Poetry development dependencies.

    Arguments:
        session: The Session object.
        args: Command-line arguments for pip.
        kwargs: Additional keyword arguments for Session.install.
    """
    req_path = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
    session.run(
        "poetry",
        "export",
        "--with=dev",
        "--format=requirements.txt",
        f"--output={req_path}",
        external=True,
    )
    session.install(f"--constraint={req_path}", "--use-deprecated=legacy-resolver", *args, **kwargs)
    os.unlink(req_path)


@nox.session(reuse_venv=True)
@nox.parametrize("python", ALL_PYTHON)
def tests(session):
    # Prepare pip and poetry
    session.run("python", "-m", "ensurepip", "--upgrade")
    session.install("poetry")
    session.run("poetry", "self", "add", "poetry-plugin-export@latest")

    # Install dev/test dependencies
    session.install("-e", ".[all]")
    install_with_constraints(
        session,
        "pytest",
        "django",
        "pytest-django",
        "django-rest-framework",
        "celery",
        "requests-mock",
        "redis",
        "boto3",
        "moto",
    )

    django_test_files = [
        "tests/test_encrypt.py",
        "tests/async_utils/test_django_utils.py",
        "tests/secure/test_dj_environ.py",
        "tests/web/",
    ]
    ignore_django_test_files = [f"--ignore={file}" for file in django_test_files]

    # Run the tests
    session.run(
        "pytest",
        # Ignore pyjwt tests
        "--ignore=tests/auth",
        # Ignore Django tests
        *(ignore_django_test_files + ["tests/"]),
        *session.posargs,
    )

    django_versions = [
        ">=2.2,<3",
        ">=3.2,<4",
        ">=4.2,<5",
    ]
    pyjwt_versions = [
        ">=1.7.0,<2",
        ">=2.0.0,<3",
    ]
    # Run Django related tests, test multiple versions
    for django in django_versions:
        session.install(f"django{django}")
        session.run("pytest", *django_test_files)

        # Run django+pyjwt related tests, test multiple versions
        for pyjwt in pyjwt_versions:
            session.install(f"pyjwt{pyjwt}")
            session.run("pytest", "tests/auth")
