from setuptools import setup, find_packages

setup(
    name='terrafron',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic>=2.10.6",
        "schedule>=1.2.2"
    ],
    entry_points={
        'console_scripts': [
            'terracron=terracron.main:main',
        ],
    },
    author='Glend Maatita',
    author_email='me@glendmaatita.com',
    description='Terraform provision scheduler',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/glendmaatita/terracron',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)