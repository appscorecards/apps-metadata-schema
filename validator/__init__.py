"""Scorecard front-matter validator.

Small wrapper around jsonschema + PyYAML that reads markdown files, extracts
their front-matter, and validates against ``schema/scorecard.schema.json``.
"""
