from dataclasses import dataclass
from environs import Env


@dataclass
class DataBase:
    sql_url: str


@dataclass
class TgBot:
    token: str
    admin_id: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DataBase


def create_config(path: str | None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_id=env('ADMIN_ID')
        ),
        db=DataBase(
            sql_url=env('SQLALCHEMY_URL')
        )
    )



# def create_db_config(path: str | None) -> Config:
#     env: Env = Env()
#     env.read_env(path)

#     return Config(
#         db=DataBase(
#             sql_url=env('SQLALCHEMY_URL')
#         )
#     )
