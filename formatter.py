from datetime import datetime


class Formatter:
    DATE_FORMATS = [
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%d.%m %H:%M",
        "%m/%d/%Y %H:%M",
    ]

    @staticmethod
    def parse_deadline(text: str) -> datetime | None:
        text = text.strip()
        for fmt in Formatter.DATE_FORMATS:
            try:
                dt = datetime.strptime(text, fmt)
                if dt.year == 1900:
                    dt = dt.replace(year=datetime.now().year)
                return dt
            except ValueError:
                continue
        return None

    @staticmethod
    def format_deadline(deadline_str: str) -> str:
        try:
            dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d, %Y at %H:%M")
        except Exception:
            return deadline_str

    @staticmethod
    def time_until(deadline_str: str) -> str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
            diff = deadline - datetime.utcnow()
            if diff.total_seconds() < 0:
                return "⚠️ overdue"
            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            if days > 0:
                return f"{days}d {hours}h"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except Exception:
            return ""

    @staticmethod
    def task_card(task: dict, index: int = None) -> str:
        prefix = f"{index}. " if index else ""
        deadline_fmt = Formatter.format_deadline(task["deadline"])
        time_left = Formatter.time_until(task["deadline"])
        desc = f"\n   📝 {task['description']}" if task.get("description") else ""
        return (
            f"{prefix}📚 <b>{task['subject']}</b> — {task['title']}\n"
            f"   📅 {deadline_fmt} (left: {time_left})"
            f"{desc}"
        )

    @staticmethod
    def task_reminder(task: dict, label: str) -> str:
        deadline_fmt = Formatter.format_deadline(task["deadline"])
        desc = f"\n📝 {task['description']}" if task.get("description") else ""
        return (
            f"{label} deadline!\n\n"
            f"📚 <b>{task['subject']}</b>\n"
            f"📌 {task['title']}\n"
            f"📅 {deadline_fmt}"
            f"{desc}"
        )