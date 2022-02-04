from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel
from PySide6.QtWidgets import QTableView, QLineEdit, QVBoxLayout, QHeaderView

from binaryninja.binaryview import BinaryDataNotification


class TableModel(QAbstractTableModel):
    def __init__(self, headers, formats):
        super().__init__()
        self.headers = headers
        self.formats = formats
        self._data = {}
        self._rows = []

    def data(self):
        return self._rows

    def update_rows(self):
        self._rows = sorted((k, v) for k, v in self._data.items())

    def rowCount(self, parent):
        return len(self._rows)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if role != Qt.DisplayRole:
            return None

        column = index.column()
        row = index.row()
        return format(self._rows[row][column], self.formats[column])

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return self.headers[section]


class MetadataNotification(BinaryDataNotification):
    def __init__(self, callback):
        self.callback = callback

    def data_metadata_updated(self, offset, length):
        self.callback(offset, length)


class CommentsWidget:
    def __init__(self):
        self._binary_view = None

        self.model = TableModel(headers=['Address', 'Comment'], formats=['08x', 's'])

        #self.filter = QSortFilterProxyModel(self.view)
        #self.filter.setFilterKeyColumn(-1)
        #self.filter.setSourceModel(self.model)
        #self.filter.setFilterCaseSensitivity(Qt.CaseInsensitive)
        #self.filter.sort(0, Qt.AscendingOrder)

        self.view = QTableView()
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view.setModel(self.model)
        self.view.doubleClicked.connect(self.goto_addr)

        #self.searchbar = QLineEdit()
        #self.searchbar.textChanged.connect(self.filter.setFilterFixedString)

    @property
    def binary_view(self):
        return self._binary_view

    @binary_view.setter
    def binary_view(self, bv):
        # Populate the initial state of the sidebar from existing function and
        if self._binary_view is None:
            self.model._data = dict( \
                    [(k, v) for k, v in bv.address_comments.items()] + \
                    sum(([(k, v) for k, v in f.comments.items()] for f in bv.functions), start=[]) \
            )
            self.model.update_rows()

            # Now register for updates
            bv.register_notification(MetadataNotification(self.metadata_callback))

            self._binary_view = bv

    def metadata_callback(self, offset, length):
        for addr in range(offset, offset+length+1):
            old = self.model._data.get(addr)

            f = self._binary_view.get_function_at(addr)
            if f is None:
                new = f.get_comment_at(addr)
            else:
                new = self._binary_view.get_comment_at(addr)

            if old is not None and new is None:
                del self.model._data[addr]
            elif old != new:
                self.model._data[addr] = new

        self.model.update_rows()

    def get_layout(self):
        layout = QVBoxLayout()
        #layout.addWidget(self.searchbar)
        layout.addWidget(self.view)
        return layout

    def goto_addr(self, index):
        #mapped_index = self.filter.mapToSource(index)
        #addr = self.model._rows[mapped_index.row()][0]
        addr = self.model._rows[index.row()][0]
        self._binary_view.navigate(self._binary_view.view, addr)
