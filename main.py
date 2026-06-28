import tkinter as tk
from tkinter import messagebox
import json
import random
import re
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
ORIGINAL_DIR = Path(r"C:\Users\admin\Desktop\History_Trainer")

PROGRESS_FILE = APP_DIR / "progress.json"
MISTAKES_FILE = APP_DIR / "mistakes.json"

BG_COLOR = "#E8DCC4"
CARD_COLOR = "#F5ECD7"
WOOD_COLOR = "#6B4423"
WOOD_HOVER = "#8B5A2B"
GOLD_COLOR = "#B8860B"
TEXT_COLOR = "#2C1810"
RED_COLOR = "#8B0000"
GREEN_COLOR = "#1E7A2E"

TITLE_FONT = ("Georgia", 20, "bold")
TEXT_FONT = ("Georgia", 14)


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def find_cards_file():
    paths = [
        APP_DIR / "cards.json",
        Path.cwd() / "cards.json",
        ORIGINAL_DIR / "cards.json",
    ]

    for path in paths:
        if path.exists():
            return path

    return None


def load_cards():
    cards_file = find_cards_file()

    if cards_file is None:
        messagebox.showerror(
            "Помилка",
            "Не знайдено cards.json. Покладіть його поруч із програмою."
        )
        return []

    cards = load_json(cards_file, [])

    cards = [
        card for card in cards
        if isinstance(card, dict) and card.get("event") and card.get("date")
    ]

    if not cards:
        messagebox.showerror(
            "Помилка",
            "У cards.json немає правильних карток."
        )

    return cards


def load_progress():
    data = load_json(PROGRESS_FILE, {"points": 0})

    if not isinstance(data, dict):
        return {"points": 0}

    try:
        points = int(data.get("points", 0))
    except (TypeError, ValueError):
        points = 0

    return {"points": max(points, 0)}


def save_progress(data):
    save_json(PROGRESS_FILE, data)


def update_points_label():
    progress = load_progress()
    points_label.config(text=f"⭐ Очки: {progress['points']}")


def add_points(amount):
    progress = load_progress()
    progress["points"] += amount
    save_progress(progress)
    update_points_label()


def load_mistakes():
    mistakes = load_json(MISTAKES_FILE, [])

    if not isinstance(mistakes, list):
        return []

    return [
        item for item in mistakes
        if isinstance(item, dict) and item.get("event") and item.get("date")
    ]


def save_mistakes(data):
    save_json(MISTAKES_FILE, data)


def add_mistake(card):
    mistakes = load_mistakes()

    exists = any(item["event"] == card["event"] for item in mistakes)

    if not exists:
        mistakes.append({
            "event": card["event"],
            "date": card["date"]
        })
        save_mistakes(mistakes)


def remove_mistake(event_name):
    mistakes = [
        item for item in load_mistakes()
        if item["event"] != event_name
    ]
    save_mistakes(mistakes)


def normalize_answer(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def make_label(parent, text="", font=TEXT_FONT, bg=BG_COLOR, fg=TEXT_COLOR, **kwargs):
    return tk.Label(
        parent,
        text=text,
        font=font,
        bg=bg,
        fg=fg,
        **kwargs
    )


def make_button(parent, text, command, width=22, danger=False):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Georgia", 14, "bold"),
        width=width,
        bg=RED_COLOR if danger else WOOD_COLOR,
        fg="white",
        activebackground="#A00000" if danger else WOOD_HOVER,
        activeforeground="white",
        bd=3,
        relief="raised",
        cursor="hand2"
    )


root = tk.Tk()
root.title("NMT History Trainer")
root.geometry("900x650")
root.configure(bg=BG_COLOR)


def open_cards():
    cards = load_cards()
    if not cards:
        return

    cards_window = tk.Toplevel(root)
    cards_window.title("Картки")
    cards_window.geometry("700x510")
    cards_window.configure(bg=BG_COLOR)

    current_card = random.choice(cards)
    answered = False

    card_frame = tk.Frame(
        cards_window,
        bg=CARD_COLOR,
        bd=5,
        relief="ridge"
    )
    card_frame.pack(padx=30, pady=30)
    card_frame.config(width=600, height=300)
    card_frame.pack_propagate(False)

    make_label(
        card_frame,
        text="📜 ІСТОРИЧНА ПОДІЯ 📜",
        font=("Georgia", 12, "bold"),
        bg=CARD_COLOR,
        fg=WOOD_COLOR
    ).pack(pady=(20, 10))

    card_label = make_label(
        card_frame,
        text=current_card["event"],
        font=TITLE_FONT,
        bg=CARD_COLOR,
        wraplength=500,
        justify="center"
    )
    card_label.pack(expand=True)

    def flip_animation(new_text):
        widths = [600, 500, 400, 300, 200, 100, 40]
        reversed_widths = list(reversed(widths))

        def shrink(index=0):
            if index < len(widths):
                card_frame.config(width=widths[index])
                cards_window.after(20, lambda: shrink(index + 1))
            else:
                card_label.config(text=new_text)
                expand()

        def expand(index=0):
            if index < len(reversed_widths):
                card_frame.config(width=reversed_widths[index])
                cards_window.after(20, lambda: expand(index + 1))

        shrink()

    def show_answer():
        nonlocal answered

        if answered:
            return

        flip_animation(f"{current_card['event']}\n\n{current_card['date']}")
        add_points(1)
        answered = True

    def next_card():
        nonlocal current_card, answered

        current_card = random.choice(cards)
        card_label.config(text=current_card["event"])
        answered = False

    make_button(cards_window, "Показати відповідь", show_answer, 24).pack(pady=15)
    make_button(cards_window, "Наступна картка", next_card, 24).pack(pady=15)


def reset_progress():
    answer = messagebox.askyesno(
        "Підтвердження",
        "Скинути всі очки та помилки?"
    )

    if answer:
        save_progress({"points": 0})
        save_mistakes([])
        update_points_label()
        messagebox.showinfo("Готово", "Прогрес успішно скинуто.")


def open_profile():
    profile_window = tk.Toplevel(root)
    profile_window.title("Профіль")
    profile_window.geometry("500x430")
    profile_window.configure(bg=BG_COLOR)

    points = load_progress()["points"]

    if points < 100:
        rank = "🌱 Новачок"
        next_level = 100
    elif points < 300:
        rank = "📚 Знавець історії"
        next_level = 300
    elif points < 500:
        rank = "🥇 Майстер НМТ"
        next_level = 500
    else:
        rank = "👑 Історик України"
        next_level = None

    make_label(
        profile_window,
        text="Ваш профіль",
        font=("Georgia", 22, "bold"),
        fg=GOLD_COLOR
    ).pack(pady=20)

    make_label(profile_window, text=f"Очки: {points}").pack(pady=15)
    make_label(profile_window, text=f"Рівень: {rank}").pack(pady=15)

    if next_level:
        remain = next_level - points
        percent = min(int((points / next_level) * 100), 100)

        make_label(
            profile_window,
            text=f"До наступного рівня: {remain} очок"
        ).pack(pady=15)

        progress_bar = tk.Canvas(
            profile_window,
            width=300,
            height=30,
            bg=CARD_COLOR,
            highlightthickness=0
        )
        progress_bar.pack(pady=20)

        progress_bar.create_rectangle(0, 0, 300, 30, outline=WOOD_COLOR)
        progress_bar.create_rectangle(
            0, 0, 3 * percent, 30,
            fill=GREEN_COLOR,
            outline=""
        )

        make_label(profile_window, text=f"{percent}%").pack()
    else:
        make_label(
            profile_window,
            text="🏆 Максимальний рівень досягнуто!"
        ).pack(pady=20)

    make_button(
        profile_window,
        "🔄 Скинути прогрес",
        reset_progress,
        width=20,
        danger=True
    ).pack(pady=20)


def open_dates_test():
    cards = load_cards()
    if not cards:
        return

    test_window = tk.Toplevel(root)
    test_window.title("Тест дат")
    test_window.geometry("700x500")
    test_window.configure(bg=BG_COLOR)

    score = 0
    current_question = None
    answered = False

    stats_label = make_label(
        test_window,
        text="Правильних відповідей: 0",
        font=("Georgia", 14, "bold"),
        fg=GOLD_COLOR
    )
    stats_label.pack(pady=15)

    question_label = make_label(
        test_window,
        wraplength=600,
        justify="center"
    )
    question_label.pack(pady=20)

    answer_entry = tk.Entry(test_window, font=TEXT_FONT)
    answer_entry.pack(pady=15)

    result_label = make_label(
        test_window,
        text="",
        font=("Georgia", 14, "bold")
    )
    result_label.pack(pady=15)

    def load_question():
        nonlocal current_question, answered

        current_question = random.choice(cards)
        question_label.config(
            text=f"Коли відбулася подія:\n\n{current_question['event']}?"
        )
        answer_entry.delete(0, tk.END)
        result_label.config(text="")
        answered = False

    def check_answer():
        nonlocal score, answered

        if answered or current_question is None:
            return

        user_answer = normalize_answer(answer_entry.get())
        correct_answer = normalize_answer(current_question["date"])

        if user_answer == correct_answer:
            score += 1
            add_points(10)
            stats_label.config(text=f"Правильних відповідей: {score}")
            result_label.config(
                text="✅ Правильно! +10 очок",
                fg=GREEN_COLOR
            )
        else:
            add_mistake(current_question)
            result_label.config(
                text=f"❌ Неправильно.\nПравильна дата: {current_question['date']}",
                fg=RED_COLOR
            )

        answered = True

    answer_entry.bind("<Return>", lambda event: check_answer())

    make_button(test_window, "Перевірити", check_answer, 20).pack(pady=10)
    make_button(test_window, "Наступне питання", load_question, 20).pack(pady=10)

    load_question()


def open_mistakes():
    mistakes_window = tk.Toplevel(root)
    mistakes_window.title("Мої помилки")
    mistakes_window.geometry("900x610")
    mistakes_window.configure(bg=BG_COLOR)

    mistakes = load_mistakes()

    make_label(
        mistakes_window,
        text="❗ Мої помилки",
        font=TITLE_FONT,
        fg=GOLD_COLOR
    ).pack(pady=15)

    make_button(
        mistakes_window,
        "🎯 Тренувати помилки",
        train_mistakes,
        width=24
    ).pack(pady=15)

    if not mistakes:
        make_label(
            mistakes_window,
            text="Помилок поки немає 🎉"
        ).pack(pady=20)
        return

    text_box = tk.Text(
        mistakes_window,
        wrap="word",
        font=TEXT_FONT,
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )
    text_box.pack(fill="both", expand=True, padx=10, pady=10)

    for item in mistakes:
        text_box.insert(tk.END, f"• {item['event']}\n")
        text_box.insert(tk.END, f"Дата: {item['date']}\n\n")

    text_box.config(state="disabled")

    make_label(
        mistakes_window,
        text=f"Усього помилок: {len(mistakes)}"
    ).pack(pady=10)


def train_mistakes():
    if not load_mistakes():
        messagebox.showinfo(
            "Тренування помилок",
            "🎉 У вас немає помилок!"
        )
        return

    train_window = tk.Toplevel(root)
    train_window.title("Тренування помилок")
    train_window.geometry("700x500")
    train_window.configure(bg=BG_COLOR)

    current_question = None
    answered = False

    question_label = make_label(
        train_window,
        wraplength=600,
        justify="center"
    )
    question_label.pack(pady=20)

    answer_entry = tk.Entry(train_window, font=TEXT_FONT)
    answer_entry.pack(pady=15)

    result_label = make_label(
        train_window,
        text="",
        font=("Georgia", 14, "bold")
    )
    result_label.pack(pady=15)

    def load_question():
        nonlocal current_question, answered

        mistakes_now = load_mistakes()

        if not mistakes_now:
            question_label.config(text="🎉 Усі помилки виправлено!")
            answer_entry.config(state="disabled")
            result_label.config(text="")
            return

        answer_entry.config(state="normal")
        current_question = random.choice(mistakes_now)

        question_label.config(
            text=f"Коли відбулася подія:\n\n{current_question['event']}?"
        )

        answer_entry.delete(0, tk.END)
        result_label.config(text="")
        answered = False

    def check_answer():
        nonlocal answered

        if answered or current_question is None:
            return

        user_answer = normalize_answer(answer_entry.get())
        correct_answer = normalize_answer(current_question["date"])

        if user_answer == correct_answer:
            add_points(15)
            remove_mistake(current_question["event"])
            result_label.config(
                text="✅ Правильно! Помилку видалено. +15 очок",
                fg=GREEN_COLOR
            )
        else:
            result_label.config(
                text=f"❌ Неправильно.\nПравильна відповідь: {current_question['date']}",
                fg=RED_COLOR
            )

        answered = True

    answer_entry.bind("<Return>", lambda event: check_answer())

    make_button(train_window, "Перевірити", check_answer, 20).pack(pady=15)
    make_button(train_window, "Наступне питання", load_question, 20).pack()

    load_question()


title_label = make_label(
    root,
    text="📜 NMT History Trainer",
    font=("Georgia", 28, "bold"),
    fg=GOLD_COLOR
)
title_label.pack(pady=20)

subtitle_label = make_label(
    root,
    text="Тренажер для підготовки до НМТ з історії України",
    font=("Georgia", 12)
)
subtitle_label.pack(pady=(0, 20))

points_label = make_label(
    root,
    text=f"⭐ Очки: {load_progress()['points']}",
    font=("Georgia", 14, "bold"),
    fg=GOLD_COLOR
)
points_label.pack(pady=15)

make_button(root, "📚 Картки", open_cards).pack(pady=15)
make_button(root, "📝 Тест дат", open_dates_test).pack(pady=15)
make_button(root, "❗ Мої помилки", open_mistakes).pack(pady=15)
make_button(root, "🎮 Профіль", open_profile).pack(pady=15)
make_button(root, "❌ Вихід", root.destroy).pack(pady=15)

root.mainloop()