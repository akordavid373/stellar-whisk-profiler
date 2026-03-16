from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stellar-whisk-profiler",
    version="0.1.0",
    author="Stellar Whisk Team",
    author_email="team@stellar-whisk.org",
    description="A comprehensive infrastructure for profiling parallelism in Stellar blockchain applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stellar/stellar-whisk-profiler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Scientific/Engineering",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "stellar-whisk-profiler=stellar_whisk_profiler.cli:main",
            "stellar-whisk-dashboard=stellar_whisk_profiler.frontend.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "stellar_whisk_profiler": ["frontend/templates/*", "frontend/static/*"],
    },
)
