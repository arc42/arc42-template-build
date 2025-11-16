# Requirements for automated arc42 build process

## What is arc42?
arc42 is a lightweight software architecture description template that provides a structured approach to documenting and communicating software architecture. It consists of a template and guidelines that help developers create clear, concise, and consistent documentation.

arc42 is available in a number of natural languages (e.g. EN, DE, FR, CZ, ES, IT, NL,PT, RU, UKR, ZH).
The core maintainers are responsible for EN and DE, the other languages have been contributed by individuals and checked by the community.

## arc42 source
The arc42 template is maintained open-source in a number of asciidoc files.

These files are located in a GitHub repository at https://github.com/arc42/arc42-template.
The code for each  natural language is contained in a subdirectory (e.g. /EN, /DE, /FR etc), with each subdirectory containing the asciidoc files for that language.

For example, here you find the directory content of the EN version:
```
.
├── asciidoc
│   ├── arc42-template.adoc
│   └── src
│       ├── 01_introduction_and_goals.adoc
│       ├── 02_architecture_constraints.adoc
│       ├── 03_context_and_scope.adoc
│       ├── 04_solution_strategy.adoc
│       ├── 05_building_block_view.adoc
│       ├── 06_runtime_view.adoc
│       ├── 07_deployment_view.adoc
│       ├── 08_concepts.adoc
│       ├── 09_architecture_decisions.adoc
│       ├── 10_quality_requirements.adoc
│       ├── 11_technical_risks.adoc
│       ├── 12_glossary.adoc
│       ├── about-arc42.adoc
│       └── config.adoc
└── version.properties
```


A few diagrams are included in the template to help explain some terms  and concepts, jpg or png based upon drawio sources.
These diagrams are located within an `/image` directory. 
In the future, these (localized) diagrams could also be moved to the language subdirectories, if required.

### version.properties
The file `version.properties` contain some asciidoc variables to denote the template version of the respective natural language.
For example:

```
revnumber=9.0-EN
revdate=July 2025
revremark=(based upon the asciidoc version)
```

## Technical formats
For practical use in development projects, arc42 can be downloaded in various technical formats:

| prio | format | extension |
|---|---|---|
|1 | HTML | html |
|1 | PDF | pdf |
|1 | Microsoft Word (R) | docx |
|1 | AsciiDoc | adoc |
|1 | Markdown simple | markdown |
|1 | Markdown multipage | markdownMP |
|2 | GitHub Markdown | GHmarkdown |
|2 | GitHub Markdown multipage | GHmarkdownMP |
|2 | Atlassian Confluence (R)  | xhtml |
|3 | LaTeX | latex |
|3 | Restructured Text | rst |
|3 | Textile | textile |

## Content flavors

For every format, there are two distinct _flavors_ available:

- plain (just the template with very brief section headings and introductory sentences for some sections).
- withHelp, containing detailed explanations, aka "help texts". Whenever a technical format allows it, the help texts are clearly distinguishable from the template text.



## What does the build process need to achieve?

- generate as many of the technical formats (see above) as possible (with 1 the highest priority, 3 the lowest)
- create both flavors (plain and withHelp)
- create the technical formats with the fonts required for these languages (e.g. UKR, RU and ZH require non-ASCII characters)
- generate locally (using Docker), AND using GitHub codespaces or similar technology.
- build process shall use ONLY open-source tools like asciidoctor, pandoc, groovy etc.
- It shall be possible to add new technical formats (e.g. sphinx)
- It shall to be possible to configure both the number of natural languages AND the technical formats that are generated, so one can build just a subset of the available formats. Yaml or groovy or json config syntax preferred.
- It shall be possible to version-pin some or all required libraries and tools, to ensure reproducibility.


## One or two repositories for content and build-process
The committers originally decided to move the build process to a second repository, in which we include the arc42-template as submodule.

That has the following advantages:

- The generated artifacts (created under the /dist directory in the template submodule) can be manually inspected prior to release.
- The build process can be re-used for req42, another open source template (used for maintaining requirements documentation of systems)
- It separates the build process from the content, making it easier to maintain and update (following the SOC principle)

>### This decision can be reverted, if a better approach is found.


## Issues with the current build process

The current build process, contained in the GitHub repository github.com/arc42/arc42-generator, suffers from the following issues:

- It grew historically, and is a complicated mixture of groovy, gradle and shell scripts.
- It cannot generate PDF.
- It cannot generate Atlassian Confluence
