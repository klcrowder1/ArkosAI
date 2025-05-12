from setuptools import setup, find_packages

setup(
    name="arkos-client",
    version="0.1.0",
    description="Python client library for the Arkos AI API",
    author="Arkos AI",
    author_email="info@arkos.ai",
    url="https://github.com/arkosai/arkos-client-python",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
        "pyjwt>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
