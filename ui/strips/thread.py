import threading
import logging

UPDATE_RATE_MILLIS = 100


class IterativeBackgroundTask:
    def __init__(self, frame, task_function, update_function=lambda *args: None,
                 on_complete_function=lambda *args: None):
        self.task_function = task_function
        self.update_function = update_function
        self.on_complete_function = on_complete_function
        self.frame = frame
        self.thread = None

        self.lock = threading.Lock()
        self.__shared_state = None
        self.__finished = False

        self.log = logging.getLogger("IterativeBackgroundTask")

    def start(self):
        self.thread = threading.Thread(target=self.__run_function, daemon=True)
        self.thread.start()
        self.frame.after(UPDATE_RATE_MILLIS, self.__update_in_main_thread)

    def __update_in_main_thread(self):
        with self.lock:
            finished = self.__finished

        if finished:
            self.log.info("Finishing in main thread")
            self.on_complete_function()
            return

        with self.lock:
            if self.__shared_state is not None:
                index, total = self.__shared_state
            else:
                self.frame.after(UPDATE_RATE_MILLIS, self.__update_in_main_thread)
                return

        self.log.debug("Main thread read state: [" + str(index) + ", " + str(total) + "]")
        self.update_function(index, total)
        self.frame.after(UPDATE_RATE_MILLIS, self.__update_in_main_thread)

    def __run_function(self):
        try:
            self.log.info("New thread spawned")
            self.task_function(self.__progress_listener)
        except Exception as e:
            logging.exception("Error in processing task function")

        with self.lock:
            self.__finished = True
        self.log.info("Thread finished")

    def __progress_listener(self, index, total):
        self.log.debug("Thread update state: [" + str(index) + ", " + str(total) + "]")
        with self.lock:
            self.__shared_state = (index, total)


class BackgroundCallableTask:
    def __init__(self, frame, callable, on_complete=lambda *args: None):
        self.frame = frame
        self.callable = callable
        self.on_complete = on_complete

        self.thread = None
        self.lock = threading.Lock()
        self.result = None
        self.__finished = False

        self.log = logging.getLogger("BackgroundCallableTask")

    def start(self):
        self.thread = threading.Thread(target=self.__run_function, daemon=True)
        self.thread.start()
        self.frame.after(500, self.__update_in_main_thread)

    def __update_in_main_thread(self):
        with self.lock:
            finished = self.__finished
            result = self.result

        if finished:
            self.log.info("Background thread finished")
            self.on_complete(result)
        else:
            self.frame.after(500, self.__update_in_main_thread)

    def __run_function(self):
        result = None
        try:
            result = self.callable()
        except Exception as e:
            logging.exception("Error in processing callable")

        with self.lock:
            self.result = result
            self.__finished = True
