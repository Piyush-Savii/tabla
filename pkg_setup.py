import subprocess
import sys
import importlib.metadata
import os
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion
from logger_setup import logger
from datetime import datetime


def install_missing_or_mismatched(requirements_path="requirements.txt", log_to_file=True):
    """
    Ensures all required packages are installed and match specified versions.
    Uses importlib.metadata for checking installed versions and packaging for parsing version specifiers.

    Args:
        requirements_path (str): Path to requirements.txt
        log_to_file (bool): Whether to save a log to file
    """

    func = "install_missing_or_mismatched"
    # Auto-create requirements.txt if missing
    if not os.path.exists(requirements_path):
        logger.warning(f" in {func} ⚠️ {requirements_path} not found.\n")

    successful = []
    failed = []

    # Cache for installed versions
    installed_versions = {
        dist.metadata['Name'].lower(): dist.version
        for dist in importlib.metadata.distributions()
    }

    with open(requirements_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            req = Requirement(line)
        except Exception as e:
            logger.warning(f" in {func} ⚠️ Invalid requirement '{line}': {e}\n")
            failed.append((line, "Invalid requirement format"))
            continue

        name = req.name.lower()
        specifier = req.specifier

        try:
            version_str = installed_versions.get(name)
            if not version_str:
                raise importlib.metadata.PackageNotFoundError

            version = Version(version_str)

            if not specifier.contains(version, prereleases=True):
                logger.warning(f" in {func}  🔁 {name}=={version} does not meet {specifier}. Reinstalling...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", line])
                successful.append(name)
            else:
                logger.info(f" in {func} ✅ {name}=={version} is up-to-date\n")
                successful.append(name)

        except importlib.metadata.PackageNotFoundError:
            logger.info(f" in {func} 📦 {name} not installed. Installing...\n")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", line])
                successful.append(name)
            except Exception as e:
                logger.error(f" in {func} ❌ Failed to install {name}: {e}\n")
                failed.append((name, str(e)))

        except (InvalidVersion, Exception) as e:
            logger.error(f" in {func} ❌ Error checking/installing {name}: {e}\n")
            failed.append((name, str(e)))

    # Log summary
    logger.info(f"\n in {func} 📦 Dependency Check Complete\n")
    logger.info(f" in {func} ✅ Installed/Matched: {successful}\n")
    if failed:
        logger.warning(f" in {func} ❌ Failed/Invalid: {failed}\n")

    # Optional: Write to log file
    if log_to_file:
        os.makedirs("logs", exist_ok=True)
        log_file = f"logs/dependency_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, "w") as f:
            f.write("Installed/Matched:\n" + "\n".join(successful) + "\n\n")
            f.write("Failed:\n" + "\n".join([f"{name} - {reason}" for name, reason in failed]))
        logger.info(f" in {func} 📝 Full log written to {log_file}\n")
