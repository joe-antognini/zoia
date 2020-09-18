"""Functionality to handle YAML formatting."""

import yaml

import click

import zoia.backend.metadata


class ZoiaYamlValidationError(Exception):
    pass


class IndentedListDumper(yaml.Dumper):
    """YAML Dumper class to increase the indentation of lists."""

    def increase_indent(self, flow=False, indentless=False):
        """Increase the indentation of lists."""

        return super(IndentedListDumper, self).increase_indent(flow, False)


def dump(obj, *args, **kwargs):
    """Wrapper around `yaml.dump` with certain defaults set."""

    default_kwargs = {
        'sort_keys': False,
        'indent': 4,
    }
    if len(args) < 2 and 'Dumper' not in kwargs:
        kwargs['Dumper'] = IndentedListDumper

    default_kwargs.update(kwargs)

    return yaml.dump(obj, *args, **default_kwargs)


def remove_header(text):
    """Remove a header from the text, returning the remaining raw text."""

    body_start = 0
    n_document_start_tokens = 0
    for elem in yaml.scan(text):
        if isinstance(elem, yaml.DocumentStartToken):
            n_document_start_tokens += 1

        if n_document_start_tokens == 2:
            if len(text) > elem.end_mark.pointer + 1:
                body_start = elem.end_mark.pointer + 1
            break

    return text[body_start:]


def metadata_validator(obj):
    """Determine whether an object is a valid metadatum."""
    try:
        zoia.backend.metadata.Metadatum.from_dict(obj)
    except Exception as e:
        raise ZoiaYamlValidationError(str(e))


def edit_until_valid(text, validation_fn=None):
    """Ask the user to keep editing if they don't provide valid YAML."""

    obj = None
    while True:
        text = click.edit(text=text, extension='.yaml')

        if text is not None:
            try:
                obj = yaml.safe_load(text)
                if validation_fn is not None:
                    try:
                        validation_fn(obj)
                    except ZoiaYamlValidationError as e:
                        click.secho(str(e), fg='red')
                        if click.confirm('Continue editing to fix?'):
                            continue
                        else:
                            break
            except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                if click.confirm(
                    'Error parsing file. Continue editing to fix it?'
                ):
                    continue
                else:
                    break
        else:
            click.secho('No input recorded. Nothing saved.', fg='red')

        break

    return obj
