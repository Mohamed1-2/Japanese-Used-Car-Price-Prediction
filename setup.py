from typing import List

from setuptools import find_packages, setup

HYPEN_E_DOT = "-e ."


def get_requirements(path: str = "requirements.txt") -> List[str]:
    """Read requirements.txt but skip the '-e .' self-reference line."""
    with open(path) as f:
        requirements = f.read().splitlines()
    return [r for r in requirements if r and not r.startswith("#") and r != HYPEN_E_DOT]


setup(
    name="usedcar-price-prediction",
    version="0.1.0",
    description="Production-ready ML pipeline for Japanese used-car price prediction",
    author="Mohamed Aldofani",
    author_email="mohamedaldofani@example.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)