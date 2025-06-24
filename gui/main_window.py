from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
	def __init__(self):
		super( ).__init__( )
		self.setWindowTitle("Doctor App")
		self.resize(800, 500)

		# Create central widget and layout
		central_widget = QWidget( )
		self.setCentralWidget(central_widget)
		layout = QVBoxLayout(central_widget)

		# Add Hello World label
		label = QLabel("Hello World")
		layout.addWidget(label)