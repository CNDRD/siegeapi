from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name="siegeapi",
    version="6.1.2",
    url="https://github.com/CNDRD/siege-api",
    description="Rainbow Six Siege API interface",
    author="CNDRD",
    packages=find_packages(),
    license="MIT",
    include_package_data=True,
    install_requires=["aiohttp>=3.6.0,<3.8.0"],
    python_requires=">=3.8.0",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ]
)
