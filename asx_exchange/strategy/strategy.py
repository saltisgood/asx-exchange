from abc import abstractmethod
import threading
import time
from typing import Protocol

class Strategy(Protocol):
    @abstractmethod
    def run(self) -> bool:
        """
        Run the strategy.
        Returns True if executed and should be removed, False otherwise.
        """
        raise NotImplementedError()

class StrategyRunner:
    def __init__(self, strategy: Strategy, interval: int=10):
        self._strategy = strategy
        self._interval = interval
        self._thread = threading.Thread(target=self._loop)
        self._continue = True
        self._running = False
        self._fired = False
    
    def start(self):
        self._thread.start()
    
    def end(self):
        self._continue = False
        self._thread.join()

    def _loop(self):
        self._running = True
        while True:
            next_run = time.time() + self._interval

            while True:
                if not self._continue:
                    self._running = False
                    return
                
                if time.time() >= next_run:
                    break
                    
                time.sleep(1)
            
            if self._strategy.run():
                self._fired = True
                self._running = False
                return

    @property
    def running(self):
        return self._running
    
    @property
    def fired(self):
        return self._fired
    
    def __str__(self):
        return f'{self._strategy}(running={self.running}, fired={self.fired})'


class StrategyMaster:
    def __init__(self):
        self._strategies = dict[str, StrategyRunner]()
        self._finished_stragies = dict[str, StrategyRunner]()
    
    def add_strategy(self, key: str, strategy: Strategy, interval: int=60):
        if key in self._strategies:
            raise RuntimeError(f"{key} already in strategies")

        runner = StrategyRunner(strategy, interval)
        runner.start()
        self._strategies[key] = runner

    def stop_strategy(self, key: str):
        try:
            strategy = self._strategies[key]
        except KeyError:
            return False
        
        strategy.end()
        self._finished_stragies[key] = strategy
        del self._strategies[key]

    def stop_all(self):
        for strategy in self._strategies.values():
            strategy.end()
        
        self._finished_stragies.update(self._strategies)
        self._strategies.clear()
    
    def get_all(self):
        self._cleanup_finished()
        return self._strategies.items(), self._finished_stragies.items()
    
    def _cleanup_finished(self):
        cleaned_up = dict[str, StrategyRunner]()

        for key, strategy in self._strategies.items():
            if not strategy.running:
                strategy.end()
                cleaned_up[key] = strategy
        
        for key, strategy in cleaned_up.items():
            del self._strategies[key]
            self._finished_stragies[key] = strategy