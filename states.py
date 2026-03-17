from aiogram.fsm.state import State, StatesGroup

class Game21(StatesGroup):
    fact1 = State()
    fact2 = State()
    fact3 = State()
    false_fact = State()

class Profile(StatesGroup):
    name = State()
    age = State()
    date = State()
    faculty = State()
    hobby = State()
    city = State()
    metro = State()
    fact = State()
    phrase = State()
    approval = State()
