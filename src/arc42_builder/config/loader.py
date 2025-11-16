import yaml
from pathlib import Path
from .models import BuildConfig, TemplateConfig, FormatOptions, BuildConfigOptions, LoggingConfig

class ConfigLoader:
    """
    Loads the build configuration from a YAML file and populates the dataclass models.
    """
    def load(self, config_path: Path) -> BuildConfig:
        """
        Loads and parses the YAML configuration file.
        """
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)

        return self._parse_config(raw_config)

    def _parse_config(self, raw_config: dict) -> BuildConfig:
        """
        Parses the raw dictionary from YAML into nested dataclasses.
        """
        template_conf = TemplateConfig(**raw_config.get("template", {}))
        
        formats_conf = {
            name: FormatOptions(**opts)
            for name, opts in raw_config.get("formats", {}).items()
        }
        
        build_conf = BuildConfigOptions(**raw_config.get("build", {}))
        logging_conf = LoggingConfig(**raw_config.get("logging", {}))

        return BuildConfig(
            version=raw_config.get("version", "1.0"),
            template=template_conf,
            languages=raw_config.get("languages", []),
            formats=formats_conf,
            flavors=raw_config.get("flavors", ["plain", "withHelp"]),
            build=build_conf,
            logging=logging_conf,
        )
