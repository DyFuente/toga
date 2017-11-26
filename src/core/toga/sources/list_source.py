from .base import Source


class Row:
    def __init__(self, **data):
        self._source = None
        for name, value in data.items():
            setattr(self, name, value)

    ######################################################################
    # Utility wrappers
    ######################################################################

    def __setattr__(self, attr, value):
        super().__setattr__(attr, value)
        if not attr.startswith('_'):
            if self._source is not None:
                self._source._notify('change', item=self)


class ListSource(Source):
    """A data source to store a list of multiple data values, in a row-like fashion.

    Args:
        data (`list`): The data in the list. Each entry in the list should have the
            same number of entries as there are accessors.
        accessors (`list`): A list of attribute names for accessing the value
            in each column of the row.
    """
    def __init__(self, data, accessors):
        super().__init__()
        self._accessors = accessors
        self._data = []
        for value in data:
            self._data.append(self._create_row(value))

    ######################################################################
    # Methods required by the ListSource interface
    ######################################################################

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]

    ######################################################################
    # Factory methods for new rows
    ######################################################################

    def _create_row(self, data):
        if isinstance(data, dict):
            row = Row(**{
                name: value
                for name, value in data.items()
            })
        else:
            row = Row(**{
                accessor: value
                for accessor, value in zip(self._accessors, data)
            })
        row._source = self
        return row

    ######################################################################
    # Utility methods to make ListSources more list-like
    ######################################################################

    def __setitem__(self, index, value):
        row = self._create_row(value)
        self._data[index] = row
        self._notify('insert', index=index, item=row)

    def __iter__(self):
        return iter(self._data)

    def clear(self):
        self._data = []
        self._notify('clear')

    def insert(self, index, *values, **named):
        # Coalesce values and data into a single data dictionary,
        # and use that to create the data row
        node = self._create_row(dict(
            named,
            **{
                accessor: value
                for accessor, value in zip(self._accessors, values)
            }
        ))
        self._data.insert(index, node)
        self._notify('insert', index=index, item=node)
        return node

    def prepend(self, *values, **named):
        return self.insert(0, *values, **named)

    def append(self, *values, **named):
        return self.insert(len(self), *values, **named)

    def remove(self, node):
        self._data.remove(node)
        self._notify('remove', item=node)
        return node