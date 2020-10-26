from kiwoom.kiwoom import *
import sys                                          # 스크립트를 관리하는 기능 (스크립트 종료 or 파이썬 변수, 함수 다루는 기능)
from PyQt5.QtWidgets import *

class Main():
    def __init__(self):
        print('Main() start')

        self.app = QApplication(sys.argv)           # PyQt5로 실행할 파일명을 자동 설정
        self.kiwoom = Kiwoom()                      # 키움 클래스 객체화
        self.app.exec_()                            # 이벤트 루프 실행

if __name__ == '__main__':
    Main()