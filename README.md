# SBOM Generator

Generates a Software Bill of Materials (SBOM) from multiple local repositories. Supports python `requirements.txt` and JavaScript `package.json`.
Outputs results to `sbom.csv` and `sbom.json`.

## Usage

```
python3 sbom.py /path/to/projects/
```

## Features

- Scans all direct subdirectories as repositories
- Detects:
  - `requirements.txt` (pip)
  - `package.json` (npm)
- Outputs:
  - `sbom.csv`
  - `sbom.json`
- Uses only Python standard library

### Implemented Optional Features
- Features 7, 9, 11 and 12


## Assumptions

- Dependency files are located only at the root of each repository
- No recursive searching inside nested folders
- `requirements.txt` must use `name==version` format
- Both `dependencies` and `devDependencies` are included from `package.json`


## Limitations

- Does not parse advanced pip formats (`>=`, `~=` etc.)
- Does not read indirect npm dependencies (`package-lock.json`)
- Requires `git` locally if using commit extraction


## Future Improvements

- Support for `package-lock.json` (transitive dependencies)
- Advanced pip parsing and license metadata
- Optional flags ( `--no-git`, `--json-only`, `--csv-only`)


## Unit Testing

A minimal set of unit tests was implemented to verify the core functionality of the tool. 
The tests focus on the most important parsing and repository detection logic:

- `find_repo_dirs()`  
  Ensures only subdirectories are detected, ignoring other files.

- `parse_requirements_txt()`  
  Verifies correct parsing of `name==version`, and ensures comments or unsupported formats are ignored.

- `parse_package_json()`  
  Tests reading both `dependencies` and `devDependencies`, and verifies behavior on invalid json.

These tests were selected because they validate the main logic of the program and directly affect the validity of the generated SBOM. 
Due to limited time (ongoing exams), additional testing of helper functions, file writing, and git commit extraction was not completed.

### Running the Tests

The tests use only the Python standard library. They can be executed using:

```
python3 -m unittest test_sbom.py
```
