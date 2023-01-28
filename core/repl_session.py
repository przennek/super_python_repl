import atexit
import multiprocessing
from multiprocessing import Queue
from typing import Optional, Dict, List

from apscheduler.schedulers.background import BackgroundScheduler

from core.pysize import get_size

shell_state = {}

__nested_session = False
__counter = 0
__default_history_path = "./sessions/session.history"
__autosave_seconds = 10
__state_comm_idle_secs = 1
__session_persistence_variable_regex = "^(([A-Z]+_)+|[A-Z]+)+$"


def __is_persistent_variable(variable_name: str) -> bool:
    import re
    return re.search(__session_persistence_variable_regex, variable_name) is not None


def __send_state(state, q):
    global shell_state
    # a[-1] == "_" and a[0] != "_"
    shell_state = {a: state[a] for a in state.keys() if __is_persistent_variable(a)}
    q.put(shell_state)


def __load_history(path: str = __default_history_path, file_suffix: Optional[str] = None):
    import dill
    history_path = __get_history_path(file_suffix, path)
    try:
        with open(history_path, 'rb') as fin:
            globs = dill.load(fin)
            for key in globs.keys():
                globals()[key] = globs.get(key)
    except FileNotFoundError:
        session_name = file_suffix if file_suffix is not None else "<Default>"
        print(f"No session found {session_name}.")  # todo @1 configure logger of some sort


def __get_history_path(file_suffix, path) -> str:
    history_path = path
    if file_suffix is not None:
        history_path += f".{file_suffix}"
    return history_path


def __notify_save(q, s):
    s.shutdown()
    q.put("Bye!")
    from time import sleep
    print("Saving changes...")  # todo @1
    sleep(1)
    q.close()


def __save_session(q: Queue,
                   session_name: Optional[str] = None,
                   path: str = __default_history_path) -> None:
    global shell_state, __counter
    from time import sleep

    history_path = __get_history_path(file_suffix=session_name, path=path)

    def save():
        import dill
        with open(history_path, 'wb') as fin:
            dill.dump(shell_state, file=fin)

    while True:
        msg = q.get()
        if msg == "Bye!":
            print(msg)  # todo @1
            save()
            break
        else:
            shell_state = msg
            __counter += 1
            if __counter % __autosave_seconds == 0:
                save()
            sleep(__state_comm_idle_secs)


def __start_session_tracking(session_name: Optional[str] = None):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=__save_session, args=(queue, session_name,))
    p.start()

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: __send_state(globals(), queue), 'interval', seconds=1)
    scheduler.start()

    atexit.register(__notify_save, queue, scheduler)


def load_session(session_name: Optional[str] = None):
    global __nested_session
    if not __nested_session:
        __load_history(file_suffix=session_name)
        __start_session_tracking(session_name=session_name)
        __nested_session = True
    else:
        print("Nesting sessions is not supported.")


def list_sessions():
    # "./sessions/session.history"
    import os
    sessions = [n for n in os.listdir(os.path.dirname(__default_history_path))
                if "history" in n and n != "session.history"]
    session_names = [n.split("history")[1][1:] for n in sessions]

    print(f"Available sessions: {session_names}. Use load_session(session_name: "
          f"Optional[str] to load a session.")  # todo @1


def status() -> Dict[str, List]:
    return {
        n: [
            f"value: {str(globals()[n])[:47] + ('...' if len(str(globals()[n])) > 50 else '')}",
            f"type: {type(globals()[n])}",
            f"size: {get_size(globals()[n])} bytes"
        ]
        for n in globals() if __is_persistent_variable(n)}
