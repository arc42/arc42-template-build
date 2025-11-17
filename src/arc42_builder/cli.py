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


@cli.command()
@click.pass_context
def test(ctx):
    """Run test suite (if tests exist) or smoke tests."""
    import subprocess
    import sys

    click.echo("Running tests...")

    # Try to run pytest if available
    try:
        result = subprocess.run(
            ["pytest", "/app/tests", "-v"],
            capture_output=True,
            text=True
        )
        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)

        if result.returncode == 0:
            click.echo(click.style("✓ All tests passed", fg="green"))
        else:
            click.echo(click.style("✗ Some tests failed", fg="red"))
            ctx.exit(result.returncode)
    except FileNotFoundError:
        # pytest not found, run basic smoke test
        click.echo("pytest not found, running basic smoke test...")

        # Check that converters can be loaded
        converters = list_converters()
        if not converters:
            click.echo(click.style("✗ No converters found", fg="red"))
            ctx.exit(1)

        click.echo(f"✓ Found {len(converters)} converters")

        # Check that config can be loaded
        config = ctx.obj.get('config')
        if not config:
            click.echo(click.style("✗ Config not loaded", fg="red"))
            ctx.exit(1)

        click.echo("✓ Configuration loaded")
        click.echo(click.style("✓ Basic smoke test passed", fg="green"))


@cli.command("test-artifacts")
@click.option('--build-dir', type=click.Path(exists=True, path_type=Path), default=None, help="Path to build directory (defaults to config)")
@click.pass_context
def test_artifacts(ctx, build_dir):
    """Validate build artifacts for syntax correctness and missing images."""
    config = ctx.obj['config']

    if not build_dir:
        build_dir = Path(config.build.output_dir)

    if not build_dir.exists():
        click.echo(click.style(f"✗ Build directory not found: {build_dir}", fg="red"))
        click.echo("Please run 'build' first to generate artifacts.")
        ctx.exit(1)

    try:
        from .core.builder import BuildPipeline
        pipeline = BuildPipeline(config)
        pipeline.validator.validate_build_artifacts(build_dir)
        click.echo(click.style("✓ All build artifacts validated successfully", fg="green"))
    except Exception as e:
        logging.error(f"Artifact validation failed: {e}", exc_info=True)
        click.echo(click.style(f"✗ Artifact validation failed: {e}", fg="red"))
        ctx.exit(1)


@cli.command("dist")
@click.option('--build-dir', type=click.Path(exists=True, path_type=Path), default=None, help="Path to build directory (defaults to config)")
@click.option('--dist-dir', type=click.Path(path_type=Path), default=None, help="Path to dist directory (defaults to config)")
@click.pass_context
def dist(ctx, build_dir, dist_dir):
    """Create ZIP distributions of build artifacts."""
    import zipfile
    import datetime

    config = ctx.obj['config']

    if not build_dir:
        build_dir = Path(config.build.output_dir)

    if not dist_dir:
        dist_dir = Path(config.build.dist_dir)

    if not build_dir.exists():
        click.echo(click.style(f"✗ Build directory not found: {build_dir}", fg="red"))
        click.echo("Please run 'build' first to generate artifacts.")
        ctx.exit(1)

    # Create dist directory
    dist_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Creating ZIP distributions from {build_dir} to {dist_dir}...")

    # Create ZIPs following the structure: workspace/dist/{LANG}/{FLAVOR}/{FORMAT}/
    zip_count = 0
    for lang_dir in build_dir.iterdir():
        if not lang_dir.is_dir():
            continue

        lang = lang_dir.name
        for flavor_dir in lang_dir.iterdir():
            if not flavor_dir.is_dir():
                continue

            flavor = flavor_dir.name
            for format_dir in flavor_dir.iterdir():
                if not format_dir.is_dir():
                    continue

                format_name = format_dir.name

                # Create output directory structure
                output_zip_dir = dist_dir / lang / flavor / format_name
                output_zip_dir.mkdir(parents=True, exist_ok=True)

                # Create ZIP file
                zip_filename = f"arc42-template-{lang}-{flavor}-{format_name}.zip"
                zip_path = output_zip_dir / zip_filename

                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add all files from the format directory
                    for file_path in format_dir.rglob('*'):
                        if file_path.is_file():
                            # Create relative path for the archive
                            arcname = file_path.relative_to(format_dir)
                            zipf.write(file_path, arcname)

                click.echo(f"  ✓ Created {zip_filename}")
                zip_count += 1

    click.echo(click.style(f"✓ Created {zip_count} ZIP distributions in {dist_dir}", fg="green"))


def main():
    cli(obj={})

if __name__ == "__main__":
    main()
