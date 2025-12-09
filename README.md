# media-catalog-system

# Project Setup

## Prerequisites
Make sure you have **Python 3.10 or newer** installed:

```bash
python3 --version
```
## Installation
1. Create a virtual environment

```bash
python3 -m venv venv
```
2. Activate the virtual environment
macOS / Linux:


```bash
source venv/bin/activate
```
Windows (Command Prompt):

```batch
.\venv\Scripts\activate
```

3. Install dependencies
(Ensure your terminal shows (catalog_env) before running)

```bash
pip install -r requirements.txt
```
## Usage

Give premission for running the script (Linux/MacOS/WSL)
```bash
chmod +x setup_env.sh
```
Run the development server:

```bash
python manage.py runserver
```
