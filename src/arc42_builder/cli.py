import click
from pathlib import Path
import logging

from .core.builder import BuildPipeline
from .config.loader import ConfigLoader
from .converters import list_converters

# Default config path inside the container
DEFAULT_CONFIG_PATH = Path("/app/config/build.yaml")

@click.group()
@click.option('--config', 'config_path', type=click.Path(exists=True, path_type=Path), default=str(DEFAULT_CONFIG_PATH), help=f"Path to the build configuration file. Defaults to {DEFAULT_CONFIG_PATH}.")
@click.option('--verbose', '-v', is_flag=True, help="Enable verbose logging.")
@click.pass_context
def cli(ctx, config_path, verbose):
    """arc42 template build system"""
    log_level = "DEBUG" if verbose else "INFO"
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    ctx.ensure_object(dict)
    try:
        config = ConfigLoader().load(config_path)
        ctx.obj['config'] = config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}. Please specify a valid path with --config.")
        ctx.exit(1)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}", exc_info=True)
        ctx.exit(1)


@cli.command()
@click.option('--lang', multiple=True, help='Language(s) to build (e.g., EN). Overrides config file.')
@click.option('--format', 'formats', multiple=True, help='Format(s) to build (e.g., pdf). Overrides config file.')
@click.option('--flavor', multiple=True, help='Flavor(s) to build (e.g., withHelp). Overrides config file.')
@click.option('--all', 'build_all', is_flag=True, help='Build all languages, formats, and flavors from config file.')
@click.pass_context
def build(ctx, lang, formats, flavor, build_all):
    """Build arc42 templates based on the configuration."""
    config = ctx.obj['config']
    
    if not build_all and not any([lang, formats, flavor]):
        click.echo("Please specify what to build or use --all.")
        click.echo("Example: `build --lang EN --format pdf` or `build --all`")
        ctx.exit(0)

    # Override config with CLI options if provided
    if lang:
        config.languages = list(lang)
    if formats:
        # Filter formats from config
        enabled_formats = {f: config.formats[f] for f in formats if f in config.formats}
        config.formats = enabled_formats
    if flavor:
        config.flavors = list(flavor)
    
    try:
        pipeline = BuildPipeline(config)
        pipeline.run()
    except Exception as e:
        logging.error(f"The build pipeline failed: {e}", exc_info=True)
        ctx.exit(1)

@cli.command()
@click.pass_context
def validate(ctx):
    """Validate template sources and build environment."""
    config = ctx.obj['config']
    try:
        # The validator is initialized in the pipeline
        pipeline = BuildPipeline(config)
        pipeline.validator.run_all_validations()
        click.echo(click.style("✓ Validation passed", fg="green"))
    except Exception as e:
        logging.error(f"Validation failed: {e}", exc_info=True)
        click.echo(click.style("✗ Validation failed. See logs for details.", fg="red"))
        ctx.exit(1)

@cli.command("list-formats")
def list_formats_command():
    """List all available output formats."""
    click.echo("Available formats:")
    for name, converter in list_converters().items():
        click.echo(f"  - {name} (priority: {converter.priority})")

def main():
    cli(obj={})

if __name__ == "__main__":
    main()
