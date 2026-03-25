from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import Database
from formatter import Formatter
from keyboard_builder import KeyboardBuilder
from states import AddTask, EditTask

CANCEL_TEXT = "❌ Cancel"


class TaskHandlers:
    def __init__(self, db: Database):
        self.db = db
        self.router = Router()
        self._register_handlers()

    def _register_handlers(self):
        r = self.router

        # Start & Help
        r.message.register(self.cmd_start, CommandStart())
        r.message.register(self.cmd_help, Command("help"))

        # Add task
        r.message.register(self.start_add, F.text == "➕ Add Task")
        r.message.register(self.start_add, Command("add"))
        r.message.register(self.add_subject, AddTask.subject)
        r.message.register(self.add_title, AddTask.title)
        r.message.register(self.add_description, AddTask.description)
        r.message.register(self.add_deadline, AddTask.deadline)

        # List tasks
        r.message.register(self.list_tasks, F.text == "📋 All Tasks")
        r.message.register(self.list_tasks, Command("list"))

        # Upcoming
        r.message.register(self.upcoming_tasks, F.text == "🔥 Upcoming")
        r.message.register(self.upcoming_tasks, Command("upcoming"))

        # By subject
        r.message.register(self.by_subject_menu, F.text == "📚 By Subject")
        r.callback_query.register(self.show_subject_tasks, F.data.startswith("subject:"))

        # Done tasks
        r.message.register(self.done_tasks, F.text == "✅ Completed")
        r.message.register(self.done_tasks, Command("done"))

        # Stats
        r.message.register(self.stats, F.text == "📊 Statistics")
        r.message.register(self.stats, Command("stats"))

        # Callbacks
        r.callback_query.register(self.cb_mark_done, F.data.startswith("done:"))
        r.callback_query.register(self.cb_delete, F.data.startswith("delete:"))
        r.callback_query.register(self.cb_confirm_delete, F.data.startswith("confirm_delete:"))
        r.callback_query.register(self.cb_cancel_delete, F.data.startswith("cancel_delete:"))
        r.callback_query.register(self.cb_edit, F.data.startswith("edit:"))

        # Edit task FSM
        r.message.register(self.edit_subject, EditTask.subject)
        r.message.register(self.edit_title, EditTask.title)
        r.message.register(self.edit_description, EditTask.description)
        r.message.register(self.edit_deadline, EditTask.deadline)

    # ── Start & Help ──────────────────────────────────────────────────────────

    async def cmd_start(self, message: Message):
        await message.answer(
            "👋 Hello! I'm your deadline management bot.\n\n"
            "I'll help you never miss a submission again 📅\n"
            "Use the buttons below or the /add command",
            reply_markup=KeyboardBuilder.main_menu()
        )

    async def cmd_help(self, message: Message):
        await message.answer(
            "📖 <b>Bot commands:</b>\n\n"
            "/add — add a new task\n"
            "/list — all active tasks\n"
            "/upcoming — deadlines in the next 48h\n"
            "/done — completed tasks\n"
            "/stats — statistics\n\n"
            "Date format: <code>31.12.2025 23:59</code>",
            parse_mode="HTML"
        )

    # ── Add Task FSM ──────────────────────────────────────────────────────────

    async def start_add(self, message: Message, state: FSMContext):
        await state.set_state(AddTask.subject)
        await message.answer("📚 Enter the subject name:", reply_markup=KeyboardBuilder.cancel())

    async def add_subject(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        await state.update_data(subject=message.text)
        await state.set_state(AddTask.title)
        await message.answer("📌 Task title:")

    async def add_title(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        await state.update_data(title=message.text)
        await state.set_state(AddTask.description)
        await message.answer(
            "📝 Description (or type <b>skip</b> to leave it empty):",
            parse_mode="HTML"
        )

    async def add_description(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        desc = None if message.text.lower() in ("skip", "no", "-") else message.text
        await state.update_data(description=desc)
        await state.set_state(AddTask.deadline)
        await message.answer(
            "📅 Enter the deadline:\n"
            "<code>31.12.2025 23:59</code>\n\n"
            "Or <code>31.12 23:59</code> for the current year",
            parse_mode="HTML"
        )

    async def add_deadline(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        deadline = Formatter.parse_deadline(message.text)
        if not deadline:
            return await message.answer(
                "❌ Invalid date format. Try: <code>31.12.2025 23:59</code>",
                parse_mode="HTML"
            )
        data = await state.get_data()
        task_id = await self.db.add_task(
            message.from_user.id, data["subject"],
            data["title"], data.get("description"), deadline
        )
        await state.clear()
        task = await self.db.get_task_by_id(task_id, message.from_user.id)
        await message.answer(
            f"✅ Task added!\n\n{Formatter.task_card(dict(task))}",
            parse_mode="HTML",
            reply_markup=KeyboardBuilder.main_menu()
        )

    # ── List / Upcoming / Done / Stats ────────────────────────────────────────

    async def list_tasks(self, message: Message):
        tasks = await self.db.get_active_tasks(message.from_user.id)
        if not tasks:
            return await message.answer("📭 No active tasks!", reply_markup=KeyboardBuilder.main_menu())

        text = "📋 <b>All active tasks:</b>\n\n"
        for i, task in enumerate(tasks, 1):
            text += Formatter.task_card(dict(task), i) + "\n\n"
        await message.answer(text, parse_mode="HTML")

        for task in tasks:
            await message.answer(
                f"<b>{task['subject']}</b> — {task['title']}",
                parse_mode="HTML",
                reply_markup=KeyboardBuilder.task_actions(task["id"])
            )

    async def upcoming_tasks(self, message: Message):
        tasks = await self.db.get_upcoming_tasks(message.from_user.id, hours=48)
        if not tasks:
            return await message.answer(
                "✨ No upcoming deadlines in the next 48 hours!",
                reply_markup=KeyboardBuilder.main_menu()
            )
        text = "🔥 <b>Upcoming deadlines (48 hours):</b>\n\n"
        for i, task in enumerate(tasks, 1):
            text += Formatter.task_card(dict(task), i) + "\n\n"
        await message.answer(text, parse_mode="HTML")

    async def by_subject_menu(self, message: Message):
        subjects = await self.db.get_subjects(message.from_user.id)
        if not subjects:
            return await message.answer("📭 No active subjects!", reply_markup=KeyboardBuilder.main_menu())
        await message.answer("Choose a subject:", reply_markup=KeyboardBuilder.subjects(subjects))

    async def show_subject_tasks(self, callback: CallbackQuery):
        subject = callback.data.split(":", 1)[1]
        tasks = await self.db.get_tasks_by_subject(callback.from_user.id, subject)
        if not tasks:
            return await callback.answer("No tasks for this subject", show_alert=True)
        text = f"📚 <b>{subject}:</b>\n\n"
        for i, task in enumerate(tasks, 1):
            text += Formatter.task_card(dict(task), i) + "\n\n"
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()

    async def done_tasks(self, message: Message):
        tasks = await self.db.get_done_tasks(message.from_user.id)
        if not tasks:
            return await message.answer("📭 No completed tasks yet!", reply_markup=KeyboardBuilder.main_menu())
        text = "✅ <b>Completed tasks:</b>\n\n"
        for i, task in enumerate(tasks, 1):
            text += (
                f"{i}. 📚 <b>{task['subject']}</b> — {task['title']}\n"
                f"   📅 {Formatter.format_deadline(task['deadline'])}\n\n"
            )
        await message.answer(text, parse_mode="HTML")

    async def stats(self, message: Message):
        active = await self.db.get_active_tasks(message.from_user.id)
        done = await self.db.get_done_tasks(message.from_user.id)
        upcoming = await self.db.get_upcoming_tasks(message.from_user.id, hours=24)

        subjects: dict[str, int] = {}
        for task in active:
            subjects[task["subject"]] = subjects.get(task["subject"], 0) + 1

        subject_list = "\n".join([f"   • {s}: {c}" for s, c in sorted(subjects.items())])
        await message.answer(
            f"📊 <b>Statistics:</b>\n\n"
            f"📌 Active tasks: <b>{len(active)}</b>\n"
            f"✅ Completed: <b>{len(done)}</b>\n"
            f"🔥 Due soon (24h): <b>{len(upcoming)}</b>\n\n"
            f"📚 <b>By subject:</b>\n{subject_list or '   —'}",
            parse_mode="HTML"
        )

    # ── Callbacks ─────────────────────────────────────────────────────────────

    async def cb_mark_done(self, callback: CallbackQuery):
        task_id = int(callback.data.split(":")[1])
        task = await self.db.get_task_by_id(task_id, callback.from_user.id)
        if not task:
            return await callback.answer("Task not found", show_alert=True)
        await self.db.mark_done(task_id, callback.from_user.id)
        await callback.message.edit_text(
            f"✅ <b>Done!</b>\n{task['subject']} — {task['title']}",
            parse_mode="HTML"
        )
        await callback.answer("Marked as completed! 🎉")

    async def cb_delete(self, callback: CallbackQuery):
        task_id = int(callback.data.split(":")[1])
        await callback.message.edit_reply_markup(reply_markup=KeyboardBuilder.confirm_delete(task_id))
        await callback.answer()

    async def cb_confirm_delete(self, callback: CallbackQuery):
        task_id = int(callback.data.split(":")[1])
        await self.db.delete_task(task_id, callback.from_user.id)
        await callback.message.edit_text("🗑 Task deleted.")
        await callback.answer("Deleted!")

    async def cb_cancel_delete(self, callback: CallbackQuery):
        task_id = int(callback.data.split(":")[1])
        await callback.message.edit_reply_markup(reply_markup=KeyboardBuilder.task_actions(task_id))
        await callback.answer("Cancelled")

    async def cb_edit(self, callback: CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split(":")[1])
        task = await self.db.get_task_by_id(task_id, callback.from_user.id)
        if not task:
            return await callback.answer("Task not found", show_alert=True)
        await state.update_data(task_id=task_id)
        await state.set_state(EditTask.subject)
        await callback.message.answer(
            f"✏️ Editing task.\n\nSubject (current: <b>{task['subject']}</b>):",
            parse_mode="HTML",
            reply_markup=KeyboardBuilder.cancel()
        )
        await callback.answer()

    async def edit_subject(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        await state.update_data(subject=message.text)
        await state.set_state(EditTask.title)
        await message.answer("📌 Task title:")

    async def edit_title(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        await state.update_data(title=message.text)
        await state.set_state(EditTask.description)
        await message.answer("📝 Description (or <b>skip</b>):", parse_mode="HTML")

    async def edit_description(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        desc = None if message.text.lower() in ("skip", "no", "-") else message.text
        await state.update_data(description=desc)
        await state.set_state(EditTask.deadline)
        await message.answer("📅 New deadline (<code>31.12.2025 23:59</code>):", parse_mode="HTML")

    async def edit_deadline(self, message: Message, state: FSMContext):
        if message.text == CANCEL_TEXT:
            return await self._cancel(message, state)
        deadline = Formatter.parse_deadline(message.text)
        if not deadline:
            return await message.answer(
                "❌ Invalid format. Try: <code>31.12.2025 23:59</code>",
                parse_mode="HTML"
            )
        data = await state.get_data()
        await self.db.update_task(
            data["task_id"], message.from_user.id,
            data["subject"], data["title"], data.get("description"), deadline
        )
        await state.clear()
        await message.answer("✅ Task updated!", reply_markup=KeyboardBuilder.main_menu())

    async def _cancel(self, message: Message, state: FSMContext):
        await state.clear()
        await message.answer("↩️ Cancelled.", reply_markup=KeyboardBuilder.main_menu())