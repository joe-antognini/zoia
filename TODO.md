# To-do list

* [ ] Add arxiv IDs by the arxiv URL (including PDFs)
* [ ] Add header information to `zoia note`.
* [ ] Write a way to print out paper information.
* [ ] Handle ISBNs in `zoia add`
* [ ] Handle DOIs in `zoia add`
* [ ] Make a singleton class to handle metadata operations.
* [ ] Write a class to represent an object's metadata.
* [ ] Add a "no download" flag to `zoia add`
* [.] Write `zoia add`
    * [ ] From DOI
    * [X] From arXiv ID
    * [ ] From ISBN
    * [ ] From BibID
* [X] Write `zoia open`
* [ ] Write `zoia note`
    * [ ] Add authors, title, etc. if not already there.
    * [ ] Update the metadata if the tags change.
* [ ] Write `zoia tag`
* [ ] Write `zoia find`
* [ ] Write `zoia rm`
* [ ] Write `zoia config` to set configuration
* [ ] Add more config options
    * [ ] JSON/YAML indentation
    * [ ] How to store metadata
        * [ ] YAML
        * [ ] SQLite
* [ ] Finish writing the README.
* [ ] Write docs
* [ ] Benchmark performance with libraries of various sizes.
* [ ] Refactor code to minimize I/O reads.
* [ ] Add SQLite database backend
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
