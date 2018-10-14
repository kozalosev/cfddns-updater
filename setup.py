from setuptools import setup, find_packages
from os.path import join, dirname
import versioneer

setup(
    name="cfddns-updater",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A script to keep the values in the Cloudflare DDNS service in sync with your local dynamic IP address.",
    long_description=open(join(dirname(__file__), "README.md")).read(),
    long_description_content_type="text/markdown",
    keywords="cloudflare dns ddns domain dynamic ip address update",
    author="Leonid Kozarin",
    author_email="kozalo@sadbot.ru",
    url="https://github.com/kozalosev/cfddns-updater",
    license="MIT",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: Name Service (DNS)'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['cfddns_updater = cfddns_updater.main:main']
    },
    install_requires=['cloudflare-ddns', 'PyYAML'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
