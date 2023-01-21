import atexit
import multiprocessing
import os
from extensions.trashcan import *

from apscheduler.schedulers.background import BackgroundScheduler

shell_state = {}

__counter = 0
__history_path = "./sessions/session.history"
__autosave_seconds = 10
__state_comm_idle_secs = 1


def __send_state(state, q):
    global shell_state
    shell_state = {a: state[a] for a in state.keys() if a[-1] == "_" and a[0] != "_"}
    q.put(shell_state)


def __load_history(path=__history_path):
    import dill
    with open(path, 'rb') as fin:
        globs = dill.load(fin)
        for key in globs.keys():
            globals()[key] = globs.get(key)


def __notify_save(q, s):
    s.shutdown()
    q.put("Bye!")
    from time import sleep
    print("Saving changes...")
    sleep(1)
    q.close()


def __save_session(q, path=__history_path):
    global shell_state, __counter
    from time import sleep

    def save():
        import dill
        with open(path, 'wb') as fin:
            dill.dump(shell_state, file=fin)

    while True:
        msg = q.get()
        if msg == "Bye!":
            print(msg)
            save()
            break
        else:
            shell_state = msg
            __counter += 1
            if __counter % __autosave_seconds == 0:
                save()
            sleep(__state_comm_idle_secs)


if os.path.exists(__history_path):
    __load_history()

queue = multiprocessing.Queue()
p = multiprocessing.Process(target=__save_session, args=(queue,))
p.start()

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: __send_state(globals(), queue), 'interval', seconds=1)
scheduler.start()

atexit.register(__notify_save, queue, scheduler)
