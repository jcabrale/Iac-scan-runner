from typing import Optional

import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class YamlLintCheck(Check):
    """Yamllint check class object."""

    def __init__(self) -> None:
        super().__init__("yamllint", "A linter for YAML files that checks for syntax validity, key repetition and "
                                     "cosmetic problems such as lines length, trailing spaces, indentation, etc.",
                         CheckTargetEntityType.IAC)
        self._config_filename: Optional[str] = None

    def configure(self, config_filename: Optional[str]) -> CheckOutput:
        """Set configuration."""
        if config_filename:
            self._config_filename = config_filename
            return CheckOutput(f"Check: {self.name} has been configured successfully.", 0)
        raise Exception(f"Check: {self.name} requires you to pass a configuration file.")

    def run(self, directory: str) -> CheckOutput:
        """Run check."""
        if self._config_filename:
            return run_command(f"{env.YAMLLINT_CHECK_PATH} -c {env.CONFIG_DIR}/{self._config_filename} .", directory)
        return run_command(f"{env.YAMLLINT_CHECK_PATH} .", directory)
