import os
import json
import csv
import unittest
import tempfile
import sbom

class TestFindRepoDirs(unittest.TestCase):

    def test_find_repo_dirs_only_directories(self):

        with tempfile.TemporaryDirectory() as base_dir:

            # Creates two directories and one file

            os.mkdir(os.path.join(base_dir, "repo1"))
            os.mkdir(os.path.join(base_dir, "repo2"))

            with open(os.path.join(base_dir, "not_repo.txt"), "w", encoding="utf-8") as f:
                f.write("dummy")

            repos = sbom.find_repo_dirs(base_dir)

            repo_names = set()
            for p in repos:
                repo_names.add(os.path.basename(p))

            self.assertEqual(repo_names, {"repo1", "repo2"})

class TestParseRequirementsTxt(unittest.TestCase):

    def test_parse_requirements_basic_and_ignores_non_equal(self):

        with tempfile.TemporaryDirectory() as tmp:

            req_path = os.path.join(tmp, "requirements.txt")

            content = """\
                        # a_comment
                        foo==1.2.3
                        bar==4.5.6
                        baz>=7.8.9
                        qux
                        """

            with open(req_path, "w", encoding="utf-8") as f:
                f.write(content)

            git_commit = "abc123"
            deps = sbom.parse_requirements_txt(req_path, git_commit)

            # Only the == lines should be parsed
            self.assertEqual(len(deps), 2)

            names = set()
            for d in deps:
                names.add(d["name"])

            self.assertEqual(names, {"foo", "bar"})

            for d in deps:
                self.assertEqual(d["git_commit"], git_commit)
                self.assertEqual(d["type"], "pip")
                self.assertTrue(d["path"].endswith("requirements.txt"))



class TestParsePackageJson(unittest.TestCase):

    def test_parse_package_json_dependencies_and_devdependencies(self):

        with tempfile.TemporaryDirectory() as tmp:

            pkg_path = os.path.join(tmp, "package.json")
            
            data = {
                "name": "test-project",
                "dependencies": {
                    "react": "17.0.2",
                    "axios": "0.27.2"
                },
                "devDependencies": {
                    "jest": "29.0.0"
                }
            }

            with open(pkg_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            git_commit = "def456"
            deps = sbom.parse_package_json(pkg_path, git_commit)

            self.assertEqual(len(deps), 3)

            names = set()
            for d in deps:
                names.add(d["name"])

            self.assertEqual(names, {"react", "axios", "jest"})

            types = set()
            for d in deps:
                types.add(d["type"])

            self.assertEqual(types, {"npm"})

            for d in deps:
                self.assertEqual(d["git_commit"], git_commit)
                self.assertTrue(d["path"].endswith("package.json"))

    def test_parse_package_json_invalid_json_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:

            pkg_path = os.path.join(tmp, "package.json")

            # write invalid JSON
            with open(pkg_path, "w", encoding="utf-8") as f:
                f.write("{ invalid json }")

            deps = sbom.parse_package_json(pkg_path, git_commit="any")

            self.assertEqual(deps, [])

if __name__ == "__main__":
    unittest.main()