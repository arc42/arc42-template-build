#!/usr/bin/env python3
"""Quick test script for configuration system."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from arc42_builder.config import load_config, ConfigError


def test_config_loading():
    """Test loading the default configuration."""
    print("Testing configuration system...")
    print("-" * 60)

    try:
        # Load default config
        config_path = Path(__file__).parent / "config" / "build.yaml"
        print(f"Loading config from: {config_path}")

        config = load_config(config_path)

        print("✓ Configuration loaded successfully\n")

        # Display configuration summary
        print("Configuration Summary:")
        print(f"  Version: {config.version}")
        print(f"  Template: {config.template.repository}")
        print(f"  Template ref: {config.template.ref}")
        print(f"  Template path: {config.template.path}")
        print(f"  Languages: {', '.join(config.languages)}")
        print(f"  Flavors: {', '.join(config.flavors)}")
        print(f"  Enabled formats: {', '.join(config.get_enabled_formats())}")
        print(f"  Build parallel: {config.build.parallel}")
        print(f"  Max workers: {config.build.max_workers}")
        print(f"  Log level: {config.logging.level}")
        print(f"  Output dir: {config.build.output_dir}")
        print(f"  Dist dir: {config.build.dist_dir}")

        print("\n✓ All tests passed!")
        return 0

    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_config_loading())
