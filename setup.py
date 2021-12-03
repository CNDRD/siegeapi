from setuptools import setup, find_packages

setup(
    name="siegeapi",
    version="1.0",
    url="https://github.com/CNDRD/siege-api",
    description="Rainbow Six Siege API interface",
    author="CNDRD",
    packages=find_packages(),
    license="MIT",
    include_package_data=True,
    install_requires=["aiohttp>=3.6.0,<3.8.0"],
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ]
)
