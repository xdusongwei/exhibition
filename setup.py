from setuptools import setup, find_packages


setup(
    name='exhibition-proxy',
    version='0.1.1',
    author='宋伟(songwei)',
    author_email='songwei@songwei.io',
    description='',
    long_description='',
    url='https://github.com/xdusongwei/exhibition',
    python_requires='>=3.10.0',
    packages=find_packages(),
    ext_modules=[],
    include_package_data=True,
    entry_points = {
        'console_scripts': ['exhibition=exhibition.main:main'],
    },
    install_requires=[
        'addict',
        'aiofiles',
        'aiohttp[speedups]',
        'aiohttp_socks',
        'base58',
        'toml',
        'xxhash',
        'yarl',
    ],
)
