from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kage-framework",
    version="1.0.0",
    author="Kid A",
    author_email="thisismeamir@outlook.com",
    description="JSON schema-validated plugin framework with function orchestration. Developed for Kage system of automation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thisismeamir/kage-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL-v3 License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "kage": ["templates/**/*"],
    },
    entry_points={
        "console_scripts": [
            "kage=kage.cli:main_cli",
        ],
    },
)