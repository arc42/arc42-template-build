import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any
import shutil
from .validator import Validator
from ..converters import get_converter
from ..config.models import BuildConfig
from ..converters.base import BuildContext

logger = logging.getLogger(__name__)

class BuildPipeline:
    def __init__(self, config: BuildConfig):
        self.config = config
        self.validator = Validator(config)
        # self.packager = Packager() # To be implemented
        self.template_path = Path(config.template.path)

    def run(self):
        """Execute the complete build pipeline."""
        
        if self.config.build.clean_before:
            self._clean_workspace()

        if self.config.build.validate:
            self.validator.run_all_validations()
        
        build_matrix = self._generate_build_matrix()
        logger.info(f"Generated {len(build_matrix)} build tasks.")
        
        results = []
        if self.config.build.parallel:
            with ThreadPoolExecutor(max_workers=self.config.build.max_workers) as executor:
                futures = [executor.submit(self._build_single, task) for task in build_matrix]
                for future in as_completed(futures):
                    try:
                        results.append(future.result())
                    except Exception as e:
                        logger.error(f"A build task failed: {e}", exc_info=True)
        else:
            for task in build_matrix:
                try:
                    results.append(self._build_single(task))
                except Exception as e:
                    logger.error(f"Build task failed: {task}", exc_info=True)

        successful_builds = [res for res in results if res]
        logger.info(f"Build finished. {len(successful_builds)}/{len(build_matrix)} artifacts created successfully.")

        # if self.config.build.create_zips:
        #     self.packager.create_packages(successful_builds)

    def _clean_workspace(self):
        """Removes build, dist, and temp directories."""
        logger.info("Cleaning workspace...")
        for dir_name in ["build", "dist", "temp"]:
            dir_path = Path(dir_name)
            if dir_path.exists():
                logger.debug(f"Removing directory: {dir_path}")
                shutil.rmtree(dir_path)
        Path("temp").mkdir(exist_ok=True)


    def _generate_build_matrix(self) -> List[Dict[str, Any]]:
        """Generate all language/flavor/format combinations."""
        matrix = []
        for lang in self.config.languages:
            for flavor in self.config.flavors:
                for format_name, format_config in self.config.formats.items():
                    if format_config.enabled:
                        matrix.append({
                            'language': lang,
                            'flavor': flavor,
                            'format_name': format_name,
                            'format_config': format_config
                        })
        return matrix

    def _load_version_props(self, language: str) -> Dict[str, str]:
        """Loads version.properties for a given language."""
        props = {}
        props_file = self.template_path / language / "version.properties"
        if not props_file.is_file():
            logger.warning(f"version.properties not found for language {language}")
            return {}
        
        with open(props_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    props[key] = value
        return props

    def _build_single(self, task: Dict[str, Any]) -> Path:
        """Build a single artifact."""
        lang = task['language']
        flavor = task['flavor']
        format_name = task['format_name']
        
        logger.info(f"Building: {lang}/{flavor}/{format_name}")
        
        converter = get_converter(format_name)
        
        context = BuildContext(
            language=lang,
            flavor=flavor,
            source_dir=self.template_path / lang / 'asciidoc',
            output_dir=Path('build') / lang / flavor / format_name,
            version_props=self._load_version_props(lang),
            config=task['format_config'].options
        )
        
        context.output_dir.mkdir(parents=True, exist_ok=True)
        
        # The flavor processing is now handled by the converter via attributes
        output_path = converter.convert(context)
        
        logger.info(f"Created: {output_path}")
        return output_path
