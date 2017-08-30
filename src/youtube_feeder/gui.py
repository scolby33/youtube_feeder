import curio
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.widgets import Divider, Frame, Label, Layout, MultiColumnListBox, Widget


class MyMultiColumnListBox(MultiColumnListBox):
    @MultiColumnListBox.options.setter
    def options(self, new_value):
        self._options = new_value
        if self.value not in {option[1] for option in self._options}:
            self.value = self._options[0][1] if len(self._options) > 0 else None

    @property
    def frame_update_count(self):
        return 10


class VideoListView(Frame):
    def __init__(self, screen, model):
        super().__init__(
            screen,
            screen.height,
            screen.width,
            on_load=self._reload_list,
            hover_focus=True,
            title='Youtube Feeder'
        )
        self._model = model

        self._list_view = MyMultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=['<0', '>7', '>2'],
            options=model.get_summary(),
            name='videos'
        )

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        layout.add_widget(Divider())
        layout.add_widget(Label('(q)uit, (c)ancel'))

        self.fix()

    def update(self, frame_no):
        self._reload_list()
        super().update(frame_no)

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code in {ord('q'), ord('Q'), Screen.ctrl('c')}:
                self._quit()
            elif event.key_code in {ord('c'), ord('C')}:
                self._cancel(self._list_view.value)
            elif event.key_code in {ord('r'), ord('R')}:
                self._reload_list()
        return super().process_event(event)

    def _reload_list(self):
        self._list_view.options = self._model.get_summary()

    def _cancel(self, value):
        self._model.cancel_download(value)

    @staticmethod
    def _quit():
        raise StopApplication('User quit')


async def gui(model):
    screen = Screen.open(height=200, catch_interrupt=False)
    restore = True

    try:
        try:
            scenes = [
                Scene([VideoListView(screen, model)], -1, name='Youtube Feeder')
            ]
            screen.set_scenes(scenes)

            while True:
                screen.draw_next_frame()
                await curio.sleep(1/20)
        except ResizeScreenError:
            restore = False
            raise
    except StopApplication:
        model.cancel_all_downloads()
    finally:
            screen.close(restore)
