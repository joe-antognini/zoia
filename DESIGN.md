# `zoia`

`zoia` is a utility to organize your library of academic papers.


## Organization

`zoia` uses a simple, flat layout to organize data.  Every paper is
referenced by a unique citation key.  (This would be the same key that you
would reference with `citep` or `citet` in LaTeX.)  Bibliographic data is
stored in a file called `.metadata.json`.

Each paper also gets its own subdirectory in the root directory.  Within each
subdirectory the document (if it exists) is stored as `document.pdf`.  Any
notes associated with the document are stored as `notes.md`.  However, `zoia`
imposes no additional structure on the layout.  If you would like to add
additional files for a paper (e.g., data or code), you are free to do so.

A sample directory structure might look like this:

```
.
├── einstein05electrodynamics
│   ├── document.pdf
│   └── notes.md
└── .metadata.json
```

TODO: How to handle tags?

## Citation key styles

`zoia` allows you to choose from several different formats to automatically
generate citation keys.

### `zoia` styles

#### Default three-author style

The default style in `zoia` is to use the last name of up to three authors
separated by `+`, (with a trailing `+` if there are more than three authors),
followed by the last two digits of the publication year, followed by a hyphen,
followed by the first word of the title (excluding common words like "the",
"a", "on", etc.).  This style is the least likely to produce collisions but is
also harder to remember.  (Though `zoia`'s search functionality can help you
to find the paper's citation key.)

##### Examples

| Author(s)                                 | Title                                                                          | Year | Citation key                  |
| --------                                  | -----                                                                          | ---- | ------------                  |
| Einstein, A.                              | On the electrodynamics of moving bodies                                        | 1905 | einstein05-electrodynamics    |
| Einstein, A., and Rosen, N.               | The particle problem in the general theory of relativity                       | 1935 | einstein+rosen35-particle     |
| Einstein, A., Podolsky, B., and Rosen, N. | Can quantum-mechanical description of physical reality be considered complete? | 1935 | einstein+podolsky+rosen35-can |
| Abbott, B. P., et al.                     | Observation of Gravitational Waves from a Binary Black Hole Merger             | 2016 | abbott+16-obseravtion         |

#### Two-author style

The two-author style is like the `zoia`'s default style, but will only
include at most two authors in the citation key.  (Any additional authors will
be represented as a `+`.)

##### Examples

| Author(s)                                 | Title                                                                          | Year | Citation key                  |
| --------                                  | -----                                                                          | ---- | ------------                  |
| Einstein, A.                              | On the electrodynamics of moving bodies                                        | 1905 | einstein05-electrodynamics    |
| Einstein, A., and Rosen, N.               | The particle problem in the general theory of relativity                       | 1935 | einstein+rosen35-particle     |
| Einstein, A., Podolsky, B., and Rosen, N. | Can quantum-mechanical description of physical reality be considered complete? | 1935 | einstein+podolsky+35-can |
| Abbott, B. P., et al.                     | Observation of Gravitational Waves from a Binary Black Hole Merger             | 2016 | abbott+16-obseravtion         |

#### Two-author abbreviated style

The two-author abbreviated style will provide up to two authors in the citation
key, but if there are three or more authors only the first will be included,
followed by a `+`.

#### No title

The above styles can be modified by not including the first word of the title
in the citation key.

### Other citation key styles

#### Google Scholar style

Google Scholar generates a citation key by using the last name of the first
author, followed by the year of publication, followed by the first word of the
title (excluding common words).

#### `pubs` style

`[pubs](https://github.com/pubs/pubs)` generates a citation key by using the
capitalized last name of the first author, followed by an underscore, followed
by the year.

### Collisions

Inevitably you will one day try to add two different papers which have the same
auto-generated citation keys.  The default style makes this rare, but does not
guarantee that it will never happen.  When it does, `zoia` will try to figure
out which paper was published first.  It will then append an `a` to the year in
the citation key of the earlier paper and a `b` to the year of the second
paper.  If additional papers would have produced collisions then `zoia` will
continue with a `c`, etc., trying to maintain chronological order.  If `zoia`
cannot determine the order of publication it will order the keys in the order
that the references were added.

## Configuration

`zoia` keeps a configuration file in `~/.local/share/zoia/conf.ini`.
(TODO: What is it on OSx systems?)  Here you can set various things like the
root directory of the library and the citation key style.

## Usage

`zoia init`

`zoia add`

`zoia find`

`zoia open`

`zoia note`

`zoia tag`

`zoia export`

`zoia import`

## Limitations

`zoia` will be tested on Ubuntu and OS X.  No guarantees will be made about its
compatibility with Windows.
