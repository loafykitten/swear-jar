"""
Captures user microphone audio in realtime and uses speech-to-text to detect user-defined swear words and interact with the swear-jar service upon detection.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label

from halp import Halp


class VoxAnalysis(App):
	CSS_PATH = ['vox.tcss']
	SCREENS = {'halp': Halp}
	BINDINGS = [
		Binding(key='q', action='quit', description='Quit the app'),
		Binding(
			key='question_mark',
			action='push_screen("halp")',
			description='Show help screen',
			key_display='?',
		),
	]

	def compose(self) -> ComposeResult:
		yield Header()
		yield Label('hewwo, world')
		yield Footer()

	def on_mount(self) -> None:
		self.title = 'Swear Jar'
		self.sub_title = '(Vox Analysis)'


if __name__ == '__main__':
	VoxAnalysis().run()
