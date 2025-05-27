from setuptools import setup, find_packages

setup(
    name="pelikul-core",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psutil==5.9.8",
        "colorama==0.4.6",
        "requests==2.31.0",
        "watchdog==3.0.0",
    ],
    entry_points={
        'console_scripts': [
            'disk-monitor=main:main',
        ],
    },
    author="Metehan Alp Saral",
    author_email="metehansaral@glynet.com",
    description="A disk monitoring and management tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    package_dir={
        'disk_utils': 'disk_utils',
        'monitoring': 'monitoring',
        'utils': 'utils',
    },
)
