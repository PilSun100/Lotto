import random


MIN_NUMBER = 1
MAX_NUMBER = 45
PICK_COUNT = 6


def normalize_numbers(numbers):
    try:
        normalized = [int(number) for number in numbers]
    except (TypeError, ValueError):
        raise ValueError("번호는 숫자여야 합니다.")

    if len(normalized) != PICK_COUNT:
        raise ValueError("번호는 6개를 선택해야 합니다.")
    if len(set(normalized)) != PICK_COUNT:
        raise ValueError("번호는 중복될 수 없습니다.")
    if any(number < MIN_NUMBER or number > MAX_NUMBER for number in normalized):
        raise ValueError("번호는 1부터 45 사이여야 합니다.")

    return sorted(normalized)


def generate_ticket_numbers():
    return sorted(random.sample(range(MIN_NUMBER, MAX_NUMBER + 1), PICK_COUNT))


def generate_draw_numbers():
    numbers = random.sample(range(MIN_NUMBER, MAX_NUMBER + 1), PICK_COUNT + 1)
    return sorted(numbers[:PICK_COUNT]), numbers[-1]


def calculate_rank(ticket_numbers, winning_numbers, bonus_number):
    matched = len(set(ticket_numbers) & set(winning_numbers))
    has_bonus = bonus_number in ticket_numbers

    if matched == 6:
        return "1등"
    if matched == 5 and has_bonus:
        return "2등"
    if matched == 5:
        return "3등"
    if matched == 4:
        return "4등"
    if matched == 3:
        return "5등"
    return "미당첨"
