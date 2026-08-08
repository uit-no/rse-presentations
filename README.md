[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8368301.svg)](https://doi.org/10.5281/zenodo.8368301)

## [RSE group](https://research-software.uit.no/) presentations

**Browse all decks at https://uit-no.github.io/rse-presentations/**, with links to the HTML slides and downloadable PDFs.

### How it works

- Each top-level `.md` file starting with a
  [cicero](https://tangled.org/radovan.xyz/cicero) header block is a slide deck.
- HTML slides are rendered on the fly at [cicero.pages.dev](cicero.pages.dev), e.g.
    - https://cicero.pages.dev/github/uit-no/rse-presentations/main/rse-intro.md/
    - https://cicero.pages.dev/github/uit-no/rse-presentations/main/rse-intro-short.md/
    - ...
- On every push to `main`, CI rebuilds all PDFs with
  [decktape](https://github.com/astefanutti/decktape) and republishes them to GitHub Pages

### Adding a deck

Create a top-level `.md` file starting with the same cicero header as the
existing decks. CI discovers it automatically. After merge it appears on the
index page.

### Previewing a deck from a PR

PR's slides can be previewed before
merging by putting the source repo and branch into the URL:

    https://cicero.pages.dev/github/<owner>/rse-presentations/<branch>/<deck>.md/

For a PR from a fork, `<owner>` is the fork's owner — e.g. a PR from
`egavazzi/rse-presentations`, branch `new-slides`, deck `rse-intro.md` would be accessible at

    https://cicero.pages.dev/github/egavazzi/rse-presentations/new-slides/rse-intro.md/

### Local preview

Install cicero's preview tool (needs Rust), then point it at a deck:

    cargo install --git https://tangled.org/radovan.xyz/cicero
    cicero rse-intro.md

### Building a PDF locally

    npx decktape https://cicero.pages.dev/github/uit-no/rse-presentations/main/rse-intro.md/ rse-intro.pdf