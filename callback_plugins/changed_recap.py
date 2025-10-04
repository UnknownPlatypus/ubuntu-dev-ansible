from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "changed_recap"

    def __init__(self):
        super().__init__()
        self.changed_task_names = []

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.current_task = task

    def v2_runner_on_ok(self, result):
        if result.is_changed():
            self.changed_task_names.append(self.current_task.get_name())

    def v2_playbook_on_stats(self, stats):
        self._display.banner("CHANGED STEPS")
        if self.changed_task_names:
            for task_name in self.changed_task_names:
                self._display.display(task_name)
        else:
            self._display.display("No changes")
        self._display.display("\n")
