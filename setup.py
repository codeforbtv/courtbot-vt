"""Setup for CourtBot."""

from setuptools import setup


def get_requirements():
    """Get list of requirements."""
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    return requirements


PACKAGE_NAME = 'courtbot-vt'

setup(
    name=PACKAGE_NAME,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Scrape VT Court Calendars',
    url=f'git@github.com:codeforbtv/{PACKAGE_NAME}.git',
    author='Code for BTV',
    python_requires='>=3.8',
    install_requires=get_requirements(),
)
