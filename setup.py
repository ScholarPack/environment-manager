import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-environment-manager",
    version="2.1.0",
    author="ScholarPack",
    author_email="dev@scholarpack.com",
    description="An environment manager for Flask, with support for whitelists and AWS SSM.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ScholarPack/flask-environment-manager",
    packages=["flask_environment_manager"],
    classifiers=[
        "Development Status :: 5 - Production/Stable ",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["flask", "boto3", "beautifultable"],
)
