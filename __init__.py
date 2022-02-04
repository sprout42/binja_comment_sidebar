from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QFont, QColor, QImage, QPainter

from binaryninjaui import SidebarWidget, SidebarWidgetType, Sidebar

from .comments import CommentsWidget


class CommentsSidebarWidget(SidebarWidget):
    def __init__(self, name, frame, data):
        SidebarWidget.__init__(self, name)
        self.binary_view = None

        self.widget = CommentsWidget()
        self.setLayout(self.widget.get_layout())

    def notifyViewChanged(self, view_frame):
        if view_frame is not None:
            self.binary_view = view_frame.actionContext().binaryView
            self.widget.binary_view = self.binary_view


class CommentsSidebarWidgetType(SidebarWidgetType):
    def __init__(self):
        # Sidebar icons are 28x28 points. Should be at least 56x56 pixels for
        # HiDPI display compatibility. They will be automatically made theme
        # aware, so you need only provide a grayscale image, where white is
        # the color of the shape.
        icon = QImage(56, 56, QImage.Format_RGB32)
        icon.fill(0)

        # Render an "#" as the example icon
        p = QPainter()
        p.begin(icon)
        p.setFont(QFont("Open Sans", 56))
        p.setPen(QColor(255, 255, 255, 255))
        p.drawText(QRectF(0, 0, 56, 56), Qt.AlignCenter, "#")
        p.end()

        SidebarWidgetType.__init__(self, icon, "Comments")

    def createWidget(self, frame, data):
        # This callback is called when a widget needs to be created for a given context. Different
        # widgets are created for each unique BinaryView. They are created on demand when the sidebar
        # widget is visible and the BinaryView becomes active.
        return CommentsSidebarWidget("Comments", frame, data)


# Register the sidebar widget type with Binary Ninja. This will make it appear as an icon in the
# sidebar and the `createWidget` method will be called when a widget is required.
Sidebar.addSidebarWidgetType(CommentsSidebarWidgetType())
