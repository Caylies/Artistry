# Changelog

Artistry changes will be documented on this page.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Improved the Artistry website in terms of UI and documentation.

### Fixed

- Fixed generation failing when two channel IDs are blank.
- Fixed the Artistry name in `pyproject.toml` being title-cased.

## [1.1.0] - 2026-07-12

### Added

- Added support for generating and accepting emoji art ([#1](https://github.com/Caylies/Artistry/pull/1)).
- Added automatic setting syncing.
- Improved error handling by adding errors for the following situations:
    - When two or more art channels have the same ID value during generation.
    - When attempting to accept an art thread's starter message.

### Changed

- Increased the max length of *Accepted Message* (256 -> 2,000).
- Increase the text input area for *Accept Message* and *Safe Thread IDs* settings.
- Minor changes to the generation view description.
- Refactored codebase.

### Removed

- Removed `/artistry sync` in favor of automatic syncing.

### Fixed

- Fixed the `/artistry generate` command becoming unusable if an error occurred.

## [1.0.0] - 2026-07-10

- Initial Artistry release.
