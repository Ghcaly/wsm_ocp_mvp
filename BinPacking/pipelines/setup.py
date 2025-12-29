
from setuptools import find_packages, setup

setup(
    name="boxing",
    packages=find_packages(include=["boxing"]),
    version="0.1.1",
    description="This library is a heuristic-based algorithm that calculates the configurations of boxes having unitary items placed into them.",
    author="AdvancedAnalytics-Logistics",
    license="MIT",
    install_requires=[],
    python_requires='>=3.7',
    setup_requires=['pytest-runner'],
    tests_require=["pytest"],
    test_suite="tests"
)