# media-catalog-system

# Project Setup

## Pre-requisites
Make sure you have **Python 3.10 or newer** installed:

```bash
python3 --version
```

Clone the repo
``` bash
git clone https://github.com/moeg100/media-catalog-system.git
```

Change the directory
``` bash
cd media-catalog-system
```

## 1. Installation
1. Create a virtual environment

```bash
python3 -m venv catalog_env
```
2. Activate the virtual environment
macOS / Linux:


```bash
source catalog_env/bin/activate
```
Windows (Command Prompt):

```batch
.\catalog_env\Scripts\activate
```

3. Install dependencies
(Ensure your terminal shows (catalog_env) before running)

```bash
pip install -r requirements.txt
```
## 2. Automatic installation.

Give premission for running the script (Linux/MacOS/WSL)
```bash
chmod +x setup_env.sh
```

Run the script 
``` bash
./setup_env

## Usage
Run the development server:

```bash
python manage.py runserver
```
