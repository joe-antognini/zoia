"""Interface with the SQLite backend."""

import json
import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

import zoia.backend.metadata

Base = declarative_base()

ZOIA_METADATA_FILENAME = 'metadata.db'


class Author(Base):
    """An author for an entry."""

    __tablename__ = 'authors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    first_name = sqlalchemy.Column(sqlalchemy.String)
    last_name = sqlalchemy.Column(sqlalchemy.String)

    entry_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('entries.citekey')
    )
    entry = sqlalchemy.orm.relationship('Entry', backref='authors')


class Tag(Base):
    """A tag for an entry."""

    __tablename__ = 'tags'

    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)

    entry_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('entries.citekey')
    )
    entry = sqlalchemy.orm.relationship('Entry', backref='tags')


class Entry(Base):
    """A single paper, book, article, etc."""

    __tablename__ = 'entries'

    citekey = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    entry_type = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.Integer)
    arxiv_id = sqlalchemy.Column(sqlalchemy.String)
    doi = sqlalchemy.Column(sqlalchemy.String)
    isbn = sqlalchemy.Column(sqlalchemy.String)
    pdf_md5 = sqlalchemy.Column(sqlalchemy.String)

    # This contains a JSON-serialized dictionary of other data not included
    # above.
    other_metadata = sqlalchemy.Column(sqlalchemy.String)

    def to_dict(self):
        authors = [
            [author.first_name, author.last_name] for author in self.authors
        ]
        tags = [elem.id for elem in self.tags]

        dictionary = {
            'citekey': self.citekey,
            'entry_type': self.entry_type,
            'title': self.title,
            'authors': authors,
            'year': self.year,
            'tags': tags,
        }
        for key in ['arxiv_id', 'doi', 'isbn', 'pdf_md5']:
            if getattr(self, key) is not None:
                dictionary[key] = getattr(self, key)

        if self.other_metadata is not None:
            dictionary.update(**json.loads(self.other_metadata))
        return dictionary

    @classmethod
    def from_dict(cls, citekey, dictionary):
        keys = {
            'entry_type',
            'title',
            'year',
            'arxiv_id',
            'doi',
            'isbn',
            'pdf_md5',
        }
        other_metadata_dict = {
            key: val for key, val in dictionary.items() if key not in keys
        }
        other_metadata = json.dumps(other_metadata_dict)
        if 'authors' in dictionary:
            authors = [
                Author(first_name=elem[0], last_name=elem[1])
                for elem in dictionary['authors']
            ]
        else:
            authors = None

        tags = []
        if 'tags' in dictionary:
            tags = tags.extend([Tag(name=elem) for elem in dictionary['tags']])

        return cls(
            citekey=citekey,
            entry_type=dictionary.get('entry_type'),
            title=dictionary.get('title'),
            year=dictionary.get('year'),
            arxiv_id=dictionary.get('arxiv_id'),
            doi=dictionary.get('doi'),
            isbn=dictionary.get('isbn'),
            pdf_md5=dictionary.get('pdf_md5'),
            authors=authors,
            tags=tags,
            other_metadata=other_metadata,
        )


class SQLiteMetadata(zoia.backend.metadata.Metadata):
    """A class to interact with the SQLite backend."""

    def __init__(self, config):
        """Start up the library metadata database."""

        self.config = config
        self.metadata_filename = os.path.join(
            config.db_root, ZOIA_METADATA_FILENAME
        )
        self.engine = sqlalchemy.create_engine(
            'sqlite:///' + self.metadata_filename
        )
        Base.metadata.create_all(self.engine)

        self.session = sqlalchemy.orm.sessionmaker(bind=self.engine)()

    def __contains__(self, citekey):
        """Determine whether the citekey exists in the library."""
        row = self.session.query(Entry).filter_by(citekey=citekey).scalar()
        return row is not None

    def __getitem__(self, citekey):
        """Load the metadata for a citekey."""
        entry = self.session.query(Entry).filter_by(citekey=citekey).first()
        return entry.to_dict()

    def write(self):
        self.session.commit()

    def append(self, key, value):
        self.session.add(Entry.from_dict(key, value))
        self.session.commit()

    def replace(self, key, value):
        new_entry = Entry.from_dict(key, value)
        query = self.session.query(Entry).filter_by(citekey=key)
        entry = query.first()
        columns = entry.__table__.columns.keys()
        update_dict = {key: getattr(new_entry, key) for key in columns}
        query.update(update_dict)
        self.session.commit()

    def rename_key(self, old_key, new_key):
        query = self.session.query(Entry).filter_by(citekey=old_key)
        query.update({'citekey': new_key})
        self.session.commit()

    def arxiv_id_exists(self, arxiv_id):
        row = self.session.query(Entry).filter_by(arxiv_id=arxiv_id).first()
        return row is not None

    def doi_exists(self, doi):
        row = self.session.query(Entry).filter_by(doi=doi).first()
        return row is not None

    def isbn_exists(self, isbn):
        row = self.session.query(Entry).filter_by(isbn=isbn).first()
        return row is not None

    def pdf_md5_hash_exists(self, pdf_md5):
        row = self.session.query(Entry).filter_by(pdf_md5=pdf_md5).first()
        return row is not None
