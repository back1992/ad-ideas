import subprocess
from pathlib import Path
from importlib.metadata import distributions


def get_installed_versions(requirements):
    """Get currently installed versions of packages using importlib.metadata"""
    versions = {}
    try:
        for dist in distributions():
            versions[dist.metadata['Name'].lower()] = dist.version
    except Exception as e:
        print(f"Warning: Error getting package versions: {e}")
    return versions


def remove_duplicates(requirements):
    """Remove duplicate entries from requirements list"""
    return list(dict.fromkeys(requirements))


def get_installed_packages():
    """Get list of installed packages using pip freeze"""
    result = subprocess.run(
        ["pip", "freeze"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return [line.split('==')[0].lower() for line in result.stdout.splitlines()]


def is_django_dependency(package_name):
    """Check if package is a common Django-related dependency"""
    django_related = [
        'django',
        'djangorestframework',
        'django-filter',
        'django-mptt',
        'django-debug-toolbar',
        'django-crispy-forms',
        'crispy-bootstrap4',
        'djangorestframework-simplejwt',
        'drf-spectacular',
    ]
    return any(package_name.startswith(dep.lower()) for dep in django_related)


def is_testing_package(package_name):
    """Check if package is a testing-related package"""
    test_packages = ['pytest', 'coverage', 'mock']
    return any(test_pkg in package_name for test_pkg in test_packages)



def main():
    """
    Clean and update requirements.txt by:
    - Removing duplicate entries
    - Removing unused packages
    - Adding version numbers for installed packages
    - Creating a backup of the original file
    """
    try:
        # Read current requirements
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            print("Error: requirements.txt not found")
            return

        with open(requirements_file, "r", encoding='utf-8') as f:
            current_requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        # Remove duplicates
        current_requirements = remove_duplicates(current_requirements)

        # Get installed versions
        installed_versions = get_installed_versions(current_requirements)
        installed_packages = get_installed_packages()

        # Create new requirements list with versions
        new_requirements = []
        for req in current_requirements:
            # Normalize package name by removing any version specifiers
            package_name = req.lower()
            for operator in ['>=', '==', '<=', '>', '<', '~=', '!=']:
                package_name = package_name.split(operator)[0]
            package_name = package_name.strip()

            # Keep package if it's:
            # 1. Currently installed, or
            # 2. A Django-related package, or
            # 3. A testing package
            if (package_name in installed_packages or
                    is_django_dependency(package_name) or
                    is_testing_package(package_name)):

                # Keep existing version constraints if present
                if any(op in req for op in ['>=', '==', '<=', '>', '<', '~=', '!=']):
                    new_requirements.append(req)
                # Add version for installed packages
                elif package_name in installed_versions:
                    new_requirements.append(f"{package_name}=={installed_versions[package_name]}")
                else:
                    new_requirements.append(package_name)
            else:
                print(f"Removing potentially unused package: {package_name}")

        # # Create backup
        # backup_path = requirements_file.with_suffix('.txt.bak')
        # counter = 1
        # while backup_path.exists():
        #     backup_path = requirements_file.with_suffix(f'.txt.bak.{counter}')
        #     counter += 1

        # requirements_file.rename(backup_path)

        # Write new requirements
        with open(requirements_file, "w", encoding='utf-8') as f:
            f.write("\n".join(sorted(new_requirements)) + "\n")

        # print(f"\nUpdated requirements.txt and created backup: {backup_path}")
        print("\nPlease review the changes and test your application!")

    except Exception as e:
        print(f"Error: Failed to update requirements.txt: {e}")
        return

if __name__ == "__main__":
    main()
