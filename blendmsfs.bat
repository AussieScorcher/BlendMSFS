@echo off
setlocal enabledelayedexpansion

:: Set up project directories
mkdir src
mkdir tests
mkdir docs

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate

:: Install required packages
pip install bpy pytest

:: Create initial Python files
echo # Main plugin file > src\__init__.py
echo # GLTF export functionality > src\gltf_exporter.py
echo # XML generation > src\xml_generator.py
echo # Texture handling > src\texture_handler.py

:: Create a basic README
echo # BlendMSFS Plugin > README.md
echo. >> README.md
echo This plugin facilitates easy export of 3D models from Blender to Microsoft Flight Simulator format. >> README.md

:: Create a basic setup.py
echo from setuptools import setup, find_packages > setup.py
echo. >> setup.py
echo setup( >> setup.py
echo     name='BlendMSFS', >> setup.py
echo     version='0.1', >> setup.py
echo     packages=find_packages(), >> setup.py
echo     install_requires=[ >> setup.py
echo         'bpy', >> setup.py
echo     ], >> setup.py
echo ) >> setup.py

:: Initialize git repository
git init
echo venv/ > .gitignore
echo *.pyc >> .gitignore
git add .
git commit -m "Initial commit"

echo Project setup complete. Activate the virtual environment with 'venv\Scripts\activate' before starting development.
