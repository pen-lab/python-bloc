import asyncio
import dataclasses
from abc import ABC, abstractmethod

from typing import Final

from bloc import *



@dataclasses.dataclass
class LoginData:
    is_loading: Final[bool]
    is_login_button_enabled: Final[bool]
    error: Final[str]
    token: Final[str]


class LoginState:
    def __init__(self, login_data: LoginData) -> None:
        self.login_data: Final[LoginData] = login_data

    @classmethod
    def initial(cls) -> 'LoginState':
        return cls(
            LoginData(
                is_loading=False,
                is_login_button_enabled=True,
                error='',
                token='',
            )
        )

    @classmethod
    def loading(cls) -> 'LoginState':
        return cls(
            LoginData(
                is_loading=True,
                is_login_button_enabled=False,
                error='',
                token='',
            )
        )

    @classmethod
    def failure(cls, error: str) -> 'LoginState':
        return cls(
            LoginData(
                is_loading=False,
                is_login_button_enabled=True,
                error=error,
                token='',
            )
        )

    @classmethod
    def success(cls, token: str) -> 'LoginState':
        return cls(
            LoginData(
                is_loading=False,
                is_login_button_enabled=True,
                error='',
                token=token,
            )
        )


class LoginEvent(ABC):
    @property
    @abstractmethod
    def password(self) -> str:
        ...

    @property
    @abstractmethod
    def username(self) -> str:
        ...


class LoginButtonPressed(LoginEvent):

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password

    @property
    def password(self) -> str:
        return self._password

    @property
    def username(self) -> str:
        return self._username


class LoginBloc(Bloc[LoginEvent, LoginState]):
    @property
    def initial_state(self) -> LoginState: return LoginState.initial()

    async def on_login_button_pressed(self, username: str, password: str) -> None:
        await self.dispatch(
            LoginButtonPressed(username, password)
        )

    async def _authenticate(self, username: str, password: str) -> str:
        return asyncio.sleep(5, '12kew333')


    async def map_event_to_state(self, event: LoginEvent) -> Stream[LoginState]:
        # TODO: не работает, нужна возможность возвращать значение
        #  в поток не прерывая текущий метод
        if isinstance(event, LoginButtonPressed):
            yield LoginState.loading()

            try:
                token = await self._authenticate(event.username, event.password)
                yield LoginState.success(token)
            except Exception as e:
                yield LoginState.failure(f'{e}')


async def main(bloc: LoginBloc):
    await bloc._bind_state_subject()

    await bloc.on_login_button_pressed(
        username='pen',
        password='qwerty'
    )


if __name__ == '__main__':
    # BlocSupervisor().delegate = SimpleBlocDelegate()
    # counter_bloc = CounterBloc()

    asyncio.run(main(LoginBloc()))