# To-do list

* [ ] Improve the `Metadatum` object to include other metadata.
* [ ] Refactor code to move work from CLI into backend.
* [ ] Write `zoia ls`.
* [ ] Write `zoia export`.
* [ ] Write `zoia rm`
* [ ] Write `zoia find`.
* [ ] Add tab completion for citekeys.
* [ ] Make a TUI.
* [ ] Add a "no download" flag to `zoia add`
* [ ] Update the metadata if the tags change in `zoia note`.
* [ ] Add tags from `zoia add` with a `-t` or `--tag` option.
* [ ] Add a `zoia download` command.
* [ ] Handle existing papers better.
        * Add possibility to merge papers.
* [ ] Print a better error message if a user tries to add an existing paper.
        * Show the citekey of the existing paper.
        * Possibly update the metadata if there is more to be found.
* [ ] Add a way to try re-downloading an existing paper.
* [ ] Add a way to specify various kinds of metadata when adding a paper.
    * [ ] Specify the entry type (article, book, etc.)
* [ ] Add papers from a URL to a PDF.
* [ ] Test `zoia` in `tox` to see which versions of Python are supported.
* [ ] Normalize LaTeX in titles.  (Convert \textendash, etc.)
* [ ] Write a mocked backend for testing.
* [ ] Add a code coverage tool.
* [ ] Handle BibIDs.
* [ ] Write docs
    * [ ] Docstrings
    * [ ] Sphinx/readthedocs
    * [ ] README
* [ ] Benchmark performance with libraries of various sizes.
* [ ] Find a better way to handle different arxiv versions.
        If the user provides an explicit version we should probably download
        that version, though we should store the unversioned arxiv ID in the
        metadata.
* [ ] Write a web app.
* [ ] `zoia import`
* [ ] Fix pytest timeout.
* [ ] Add a config option that lets you move vs. copy a PDF if you're adding a
      PDF manually.
* [ ] Add a config option to open PDFs with native PDF viewer or in a web
      browser.
* [ ] Eliminate `zoia init`?  Should be possible to auto-detect if `zoia` has
      been initialized and run initalization if it hasn't happened.
