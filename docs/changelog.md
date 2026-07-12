# Changelog

Artistry changes will be documented on this page.

## [Unreleased]

### Added

- Added support for generating and accepting emoji art ([#1](https://github.com/Caylies/Artistry/pull/1)).
- Added automatic setting syncing.
- Improved error handling by adding errors for the following situations:
    - When two or more art channels have the same ID value during generation.
    - When attempting to accept an art thread's starter message.

### Changes

- Increased the max length of *Accepted Message* (256 -> 2,000).
- Increase the text input area for *Accept Message* and *Safe Thread IDs* settings.
- Minor changes to the generation view description.
- Refactored codebase.

### Fixed

- Fixed the `/artistry generate` command becoming unusable if an error occurred.

### Removed

- Removed `/artistry sync` in favor of automatic syncing.

## [1.0.0] - 2026-10-7

- Initial Artistry release.
