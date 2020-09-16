"""Functionality to handle YAML formatting."""

import yaml


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
