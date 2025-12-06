import os
import sys
import json
import csv
#added for the Optional features
import subprocess

def find_repo_dirs(base_dir):
    """Return a list of absolute paths to subdirectories of base_dir (candidate repos)."""
    repos=[]
    try:
        for entry in os.listdir(base_dir):
            full_path = os.path.join(base_dir, entry)
            if os.path.isdir(full_path):
                repos.append(full_path)
    except OSError as e:
        print(f"Error reading directory {base_dir}: {e}\n")
        sys.exit(1)
    return repos


def get_git_commit(repo_dir):
    """
    Return the latest commit hash for the repository at repo_dir.
    If the repo is not a real git repo or git command fails, return None.
    """
    try:
        # Running the command: git log --format=%H -n 1  in this repo directory
        result = subprocess.check_output(
            ["git", "log", "--format=%H", "-n", "1"],
            cwd=repo_dir,
            stderr=subprocess.DEVNULL  # no error output clutter
        )
        return result.decode().strip()
    except Exception:
        return None  # repo may not be a git repo
    

def parse_requirements_txt( path, git_commit):
    """
    Parse a requirements.txt file.

    Assumptions:
    - Only lines of the form 'name==version' are handled.
    - Lines starting with '#' or empty lines are ignored.
    - Other formats are ignored.
    """

    deps =[]
    try:
        with open(path, "r", encoding="utf-8")as f:
            for line in f:
                line= line.strip()
                if not line or line.startswith("#"):
                    continue
                if "==" in line:
                    name, version = line.split("==")
                    name = name.strip()
                    version= version.strip()
                    if name and version:
                        deps.append({
                            "name": name,
                            "version": version,
                            "type": "pip",
                            "path": os.path.abspath(path),
                            "git_commit": git_commit,
                        })
                    # Other formats (like >= or ~=) are ignored for this assignment
    except OSError as e:
        print(f"Warning: could not read {path}: {e}\n")
    
    return deps

def parse_package_json(path, git_commit):
    """
    Parse a package.json file.

    Assumptions:
    - i include only 'dependencies' and 'devDependencies' .
    """
    deps=[]
    try:
        with open(path, "r", encoding="utf-8")as f:
            data= json.load(f)

    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: could not parse {path}: {e}\n")
        return deps
    
    abs_path = os.path.abspath(path)

    def add_deps(section_name):

        section = data.get(section_name, {})

        if isinstance(section, dict):

            for name, version in section.items():
                deps.append({
                    "name": name,
                    "version": version,
                    "type": "npm",
                    "path": abs_path,
                    "git_commit": git_commit,
                })

    add_deps("dependencies")
    add_deps("devDependencies")

    return deps

def collect_dependencies_for_repo(repo_dir):
    """
    Look for requirements.txt and package.json in the repo root.
    Return list of dependency entries.
    """
    deps = []

    git_commit = get_git_commit(repo_dir) 

    req_path = os.path.join(repo_dir, "requirements.txt")
    pkg_path = os.path.join(repo_dir, "package.json")

    if os.path.isfile(req_path):
        deps.extend(parse_requirements_txt(req_path,git_commit))

    if os.path.isfile(pkg_path):
        deps.extend(parse_package_json(pkg_path,git_commit))

    return deps
             
def write_csv(entries, output_path):
    fieldnames = ["name", "version", "type","path","git_commit"]

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for e in entries:
                writer.writerow(e)

    except OSError as e:
        print(f"Error writing CSV file {output_path}: {e}\n")
        sys.exit(1)


def write_json(entries, output_path):
    try:

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

    except OSError as e:
        print(f"Error writing JSON file {output_path}: {e}\n")
        sys.exit(1)


def main():
    # Argument handling
    if len(sys.argv) != 2:
        print("Error: exactly one directory argument is required.\n")
        sys.exit(1)
    
    base_dir = sys.argv[1]

    if not os.path.exists(base_dir):
        print(f"Error: path {base_dir} does not exist.\n")
        sys.exit(1)

    if not os.path.isdir(base_dir):
        print(f"Error: path {base_dir} is not a directory.\n")
        sys.exit(1)
    
    base_dir = os.path.abspath(base_dir)

    # Finding repo directories 
    repo_dirs = find_repo_dirs(base_dir)
    print(f"Found {len(repo_dirs)} repositories in {base_dir}\n")

    # Collecting dependencies from each repo
    all_entries = []

    for repo in repo_dirs:
        repo_name = os.path.basename(repo)
        deps = collect_dependencies_for_repo(repo)

        if deps:
            print(f"  {repo_name}: found {len(deps)} dependencies\n")
        else:
            print(f"  {repo_name}: no supported dependency files found\n")

        all_entries.extend(deps)
    
    # 4. Write SBOM files in base_dir
    csv_path = os.path.join(base_dir, "sbom.csv")
    json_path = os.path.join(base_dir, "sbom.json")

    write_csv(all_entries, csv_path)
    write_json(all_entries, json_path)

    print(f"Saved SBOM in CSV format to {csv_path}\n")
    print(f"Saved SBOM in JSON format to {json_path}\n")


if __name__ =="__main__":
    main()
    