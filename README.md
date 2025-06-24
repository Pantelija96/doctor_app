# Doctor App

A single-user desktop application for doctors to manage patients and appointments. Built with **Python** and **PyQt6**, it features a local **SQLite** database, offline **Serbian speech-to-text**, and **PDF report generation**. The app runs on **Windows**, uses **pipenv** for dependency management, and stores data in `%APPDATA%\DoctorApp\data`.

---
## Project Structure

```text
doctor_app/
├── audio               -> Audio files for appointment recordings
├── backup              -> Database backups
├── gui                 -> GUI-related Python modules (planned for PyQt6)
├── logs                -> Error logs in JSON format (created at runtime)
├── reports             -> Temporary PDF reports (created at runtime)
├── .gitignore          -> Git ignore file
├── confing.json        -> Env config file
├── database_manager.py -> SQLite database setup and management
├── main.py             -> App entry point, initializes database
├── Pipfile             -> Dependency configuration
├── Pipfile.lock        -> Locked dependency versions
├── README.md           -> Project documentation
├── report_generator.py -> For creating PDF for report printing
├── speech_processor.py -> Speech-to-text processor
├── utils.py            -> Error logging and utilities
```

---

## Setup

### Prerequisites

- Python 3.10+
- `pipenv` for dependency management
- Windows (target platform)

### Installation

```bash
# Clone the repository
git clone https://github.com/Pantelija96/doctor_app.git
cd doctor_app

# Install pipenv (if not already installed)
pip install pipenv

# Install dependencies
pipenv install

# Activate the virtual environment
pipenv shell

# Check if everything is installed
pipenv graph

# Run the app
python main.py
```
#### This initializes the SQLite database in %APPDATA%\DoctorApp\data\database.db and creates an audio folder for future use.

---
## Development Notes

- **Naming Convention:** Uses `snake_case` for all code.
- **Data Storage:** Database, audio files, and logs are stored in `%APPDATA%\DoctorApp\data` and `%APPDATA%\DoctorApp\logs`.
- **Modular Design:** Backend and future GUI components are separated for maintainability.
- **Dependencies:** Managed via `Pipfile` and `Pipfile.lock` for reproducible builds.
- **Future Dependencies:** Will include `PyQt6`, `whisper`, `pyaudio`, and `reportlab`.

---
## Contributing

To ensure clean and organized development, we follow this workflow:

1. Always start by creating a **feature branch** from the `main` branch:
   ```bash
   git switch main
   git pull
   git switch -c branch-name
2. Work on your feature in the feature branch. Commit your changes with clear commit messages:
   ```bash
   git add .
   git commit -m "Description of what you did"
   
3. Push your feature branch to the repository:
   ```bash
   git push -u origin branch-name
   
4. Open a Pull Request (PR) from your feature branch to main.
5. The other developer will review and merge (or close) the PR.
> **Note:** You should not merge your own PR — this ensures both of us review each other's work and maintain code quality.

---
### Branch Naming Convention

We use the following branch naming patterns:

- `feature/<short-description>` — For new features  
  Example: `feature/add-patient-form`

- `bugfix/<short-description>` — For bug fixes  
  Example: `bugfix/fix-date-validation`

- `hotfix/<short-description>` — For urgent production fixes  
  Example: `hotfix/crash-on-startup`

- `refactor/<short-description>` — For code refactoring that doesn't change functionality  
  Example: `refactor/clean-database-manager`

✅ **Guidelines:**  
- Use lowercase letters and hyphens (`-`) to separate words.  
- Keep names short but descriptive.  
- Always branch from `main`.

---

### Pull Request Naming Convention

When creating a pull request:

- **Title:** Use the branch name or a short, clear description  
  Example: `Feature: Add patient form`
- **Description:** Briefly explain what was done and any important notes for the reviewer.

---

