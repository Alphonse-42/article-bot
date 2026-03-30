import subprocess
from loguru import logger

class LocalGitManager:
    """
    Manages local git operations using the subprocess module.
    Runs `git add .`, `git commit -m "..."` and `git push origin main`.
    """
    def __init__(self, commit_template: str = "Auto-publish: [{slug}]"):
        self.commit_template = commit_template

    def publish(self, slug: str) -> bool:
        """
        Executes the exact requested workflow:
        1. git add .
        2. git commit -m "Auto-publish: [{slug}]"
        3. git push origin main
        """
        commit_message = self.commit_template.format(slug=slug)

        try:
            # Step 1: Add all files
            logger.info("Running: git add .")
            subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)

            # Step 2: Commit
            logger.info(f"Running: git commit -m \"{commit_message}\"")
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True
            )
            
            # If exit code is not 0, it may be because there's nothing to commit
            if commit_result.returncode != 0:
                out = (commit_result.stdout + commit_result.stderr).lower()
                if "nothing to commit" in out or "working tree clean" in out:
                    logger.info("Nothing to commit. Skipping push.")
                    return True
                else:
                    logger.error(f"Git commit failed. Code {commit_result.returncode}:\nOutput: {out}")
                    return False
            else:
                logger.debug(commit_result.stdout.strip())

            # Step 3: Push
            logger.info("Running: git push origin main")
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True
            )
            
            if push_result.returncode != 0:
                logger.error(f"Git push failed. Code {push_result.returncode}:\nOutput: {push_result.stderr}")
                return False
            
            logger.success("Local git operations successful. Changes pushed to GitHub.")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Git process error:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during local git operations: {e}")
            return False
