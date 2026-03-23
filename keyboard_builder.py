from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)


class KeyboardBuilder:

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Add Task"), KeyboardButton(text="📋 All Tasks")],
                [KeyboardButton(text="🔥 Upcoming"), KeyboardButton(text="📚 By Subject")],
                [KeyboardButton(text="✅ Completed"), KeyboardButton(text="📊 Statistics")],
            ],
            resize_keyboard=True
        )

    @staticmethod
    def cancel() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Cancel")]],
            resize_keyboard=True
        )

    @staticmethod
    def task_actions(task_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Mark Done", callback_data=f"done:{task_id}"),
                InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit:{task_id}"),
            ],
            [
                InlineKeyboardButton(text="❌ Delete", callback_data=f"delete:{task_id}"),
            ]
        ])

    @staticmethod
    def confirm_delete(task_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🗑 Yes, delete", callback_data=f"confirm_delete:{task_id}"),
                InlineKeyboardButton(text="↩️ Cancel", callback_data=f"cancel_delete:{task_id}"),
            ]
        ])

    @staticmethod
    def subjects(subjects: list[str]) -> InlineKeyboardMarkup:
        buttons = [[InlineKeyboardButton(text=s, callback_data=f"subject:{s}")] for s in subjects]
        return InlineKeyboardMarkup(inline_keyboard=buttons)