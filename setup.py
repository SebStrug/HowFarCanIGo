from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='howfarcanigo', 
    version='1.0.0',
    description='A personalised isochrone generator', 
    long_description=long_description,
    url='https://github.com/Sebtps:CanIGo',  
    author='Seb Strug',
    classifiers=[ 
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='map isochrone googlemaps', 

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(exclude=['docs', 'tests']), 
    python_requires='>=3.5',

    install_requires=['googlemaps==3.1.1', 'requests==2.22.0', 'chardet==3.0.4', 'idna==2.8', 'urllib3==1.26.5', \
                        'folium', 'matplotlib', 'seaborn', \
                        ##(ipython) 'ipython', 'parso', 'jedi', 'pygments', 'ipython-genutils', \   
                        'numpy', 'datetime', 'requests', \
                        'polyline', 'sklearn',
                        'shapely'], 


    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'sample=sample:main',
        ],
    },

    project_urls={
        'Say Thanks!': 'https://saythanks.io/to/SebStrug',
        'Source': 'https://github.com/SebStrug/HowFarCanIGo',
    },
)