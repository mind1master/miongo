

def singleton(cls):
    """ Singleton decorator """
    singletone_instances = {}

    def getinstance():
        if cls not in singletone_instances:
            singletone_instances[cls] = cls()
        return singletone_instances[cls]
    return getinstance


@singleton
class SignalRegistry(dict):
    pass

# used to store all connected callbacks
# to all signals and classes
# e.g. signal_registry['Account'] = {'POST_COMMIT': set(func1,func2)}
signal_registry = SignalRegistry()


class SignalException(Exception):
    pass


class SignalEmitterMixin(object):
    AVAILABLE_SIGNALS = ()  # available signals, specify in ancestor

    @classmethod
    def connect_to_signal(cls, signal_type, callback):
        """
        Connects func to signal_type class.
        :param signal_type: one of self.SIGNALS
        :param callback: function to call when signal is fired
        """
        if not signal_type in cls.AVAILABLE_SIGNALS:
            raise SignalException('No such signal available: {}'.format(signal_type))

        if not callable(callback):
            raise SignalException('Callback should be callable')

        if not cls in signal_registry:
            signal_registry[cls] = {}

        if not signal_type in signal_registry[cls]:
            signal_registry[cls][signal_type] = set()

        signal_registry[cls][signal_type].add(callback)

    @classmethod
    def disconnect_from_signal(cls, signal_type, callback):
        if signal_type in signal_registry[cls]:
            signal_registry[cls][signal_type].discard(callback)

    @classmethod
    def clear_all_signals(cls):
        signal_registry[cls] = {}

    @classmethod
    def _get_callbacks_for_signal(cls, signal_type):
        if not signal_type in cls.AVAILABLE_SIGNALS:
            raise SignalException('No such signal available: {}'.format(signal_type))

        if cls in signal_registry and signal_type in signal_registry[cls]:
            return signal_registry[cls][signal_type]

        return set()

    def emit_signal(self, signal_type):
        """
        Calls all functions that are binded to that signal_type
        :param signal_type:
        """
        callbacks_to_call = self.__class__._get_callbacks_for_signal(signal_type)
        for callback in callbacks_to_call:
            callback(signal_type=signal_type, instance=self)
