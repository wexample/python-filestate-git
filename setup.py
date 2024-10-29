from setuptools import setup, find_packages

setup(
    name='wexample-filestate-git',
    version=open('version.txt').read(),
    author='weeger',
    author_email='contact@wexample.com',
    description='An extension for "filestate" package, which adds GIT management operations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/wexample/python-filestate-git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'gitpython',
        'pydantic',
        'wexample-filestate',
        'wexample-helpers',
    ],
    python_requires='>=3.6',
)
