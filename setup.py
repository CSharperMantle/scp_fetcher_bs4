from setuptools import setup, find_packages


setup(name='scp-fetcher-bs4',
      version='0.0.2',
      author='CSharperMantle',
      author_email='mantlejonse@gmail.com',
      url='https://github.com/CSharperMantle/scp_fetcher_bs4',
      description='fetch SCP-related information from a given SCP Wiki page',
      long_description='see README.md',
      license='GPL-3.0-only',
      install_requires=[
            'beautifulsoup4==4.8.2',
            'certifi==2019.11.28',
            'chardet==3.0.4',
            'idna==2.8',
            'requests==2.22.0',
            'soupsieve==1.9.5',
            'urllib3==1.25.8'
      ],
      include_package_data=True,
      packages=find_packages())
