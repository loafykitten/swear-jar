from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Label


class Halp(Screen):
	BINDINGS = [
		Binding(key='q', action='quit', description='Quit the app'),
		Binding(
			key='question_mark', action='app.pop_screen', description='Exit help screen'
		),
	]

	def compose(self) -> ComposeResult:
		yield Header()
		yield Label('halp')
		yield Footer()

	def on_mount(self) -> None:
		self.title = 'Swear Jar'
		self.sub_title = '(Vox Analysis - Help)'
