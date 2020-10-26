from kiwoom.Kiwoom import *

class Threading_():

    def asdf(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.receive_thread()
        time.sleep(10000)
        self.kiwoom.receive_thread_2()

