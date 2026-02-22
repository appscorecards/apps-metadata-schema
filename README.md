# apps-metadata-schema

JSON Schema for the scorecard markdown front-matter used by
[appscorecards/awesome-mobile-apps](https://github.com/appscorecards/awesome-mobile-apps).

Work in progress. This repo will hold:

- `schema/scorecard.schema.json` -- the canonical schema.
- `validator/` -- a small Python validator that extracts front-matter from a
  `.md` file and runs it through the schema.
- `examples/` -- sample scorecards that should and should not validate.

## License

MIT. See [LICENSE](LICENSE).
