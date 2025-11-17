# PDF Themes

This directory is reserved for custom Asciidoctor PDF theme files.

For the PoC, the default Asciidoctor PDF theme is used.

## Future Use

Place custom `.yml` theme files here to customize the PDF output appearance. Reference them in the build process using the `-a pdf-theme` attribute.

Example:
```bash
asciidoctor-pdf -a pdf-theme=/workspace/docker/pdf-themes/arc42-theme.yml
```
