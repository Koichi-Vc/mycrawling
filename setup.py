from setuptools import setup, find_namespace_packages
from pathlib import Path

this_directory = Path(__file__).parent
description = (this_directory / "README.md").read_text(encoding='UTF-8')
#description = Path("README.md").read_text(encoding="UTF-8")

setup(
    name='mycrawling',
    version='0.0.0',
    packages=find_namespace_packages(),
    include_package_data=True,
    long_description = description,
    long_description_content_type = 'text/markdown',
    license_files = ['LICENSE','NOTICE', 'third_party_license/Third_Party_License.txt']
)