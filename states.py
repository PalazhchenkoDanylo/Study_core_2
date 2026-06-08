from aiogram.fsm.state import State, StatesGroup


class AddTask(StatesGroup):
    subject = State()
    title = State()
    description = State()
    deadline = State()


class EditTask(StatesGroup):
    task_id = State()
    subject = State()
    title = State()
    description = State()
    deadline = State()


class AIChat(StatesGroup):
    chatting = State()