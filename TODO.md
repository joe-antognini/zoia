# To-do list

* [ ] Use `redislite` to handle the backend.
* [ ] Fix issue with adding PDF where arXiv ID is not added.
* [ ] Write `zoia tag`
* [ ] Add a "no download" flag to `zoia add`
* [ ] Handle existing papers better.
        * Add possibility to merge papers.
* [ ] Print a better error message if a user tries to add an existing paper.
        * Show the citekey of the existing paper.
        * Possibly update the metadata if there is more to be found.
* [ ] Add a way to try re-downloading an existing paper.
* [ ] Update the metadata if the tags change in `zoia note`.
* [ ] Add papers from a URL to a PDF.
* [ ] Test `zoia` in `tox` to see which versions of Python are supported.
* [ ] Normalize LaTeX in titles.  (Convert \textendash, etc.)
* [ ] Write `zoia find`
* [ ] Write a mocked backend for testing.
* [ ] Add a code coverage tool.
* [ ] Handle BibIDs.
* [ ] Write `zoia rm`
* [ ] Write `zoia config` to set configuration
* [ ] Add more config options
    * [ ] JSON/YAML indentation
    * [ ] How to store metadata
        * [ ] YAML
        * [ ] SQLite
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
* [ ] `zoia export`
* [ ] `zoia import`
* [ ] Fix pytest timeout.
* [ ] Add a config option that lets you move vs. copy a PDF if you're adding a
      PDF manually.
* [ ] Add a config option to open PDFs with native PDF viewer or in a web
      browser.
* [ ] Eliminate `zoia init`?  Should be possible to auto-detect if `zoia` has
      been initialized and run initalization if it hasn't happened.
* [ ] Add more citekey styles.
