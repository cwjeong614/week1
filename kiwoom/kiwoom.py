from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errCode import *
import os

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print('Kiwoom() class start')

        # Event Loop 실행 변수 ==========================================================================================
        self.login_event_loop = QEventLoop()                        # 로그인 요청용 이벤트 루프
        self.tr_event_loop = QEventLoop()                           # TR 요청용 이벤트 루프
        # ==============================================================================================================

        # 계좌 관련 변수 ================================================================================================
        self.account_stock_dict = {}                        # 보유 종목 딕셔너리
        self.account_num = None                             # 계좌번호
        self.deposit = 0                                    # 예수금
        self.use_money = 0                                  # 실제 투자에 사용할 금액
        self.use_money_percent = 0.5                        # 예수금에서 실제 사용할 비율
        self.output_deposit = 0                             # 출금 가능 금액
        self.total_profit_loss_money = 0                    # 총평가손익금액
        self.total_profit_loss_rate = 0.0                   # 총수익률(%)
        # ==============================================================================================================

        # 요청 스크린 번호 ===============================================================================================
        self.screen_my_info = '2000'                        # 계좌 관련 스크린 번호
        # ==============================================================================================================

        # 초기 세팅 함수 =================================================================================================
        self.get_ocx_instance()                             # OCX방식을 파이썬에 사용할 수 있게 반환해 주는 함수 실행
        self.event_slots()                                  # 키움과 연결하기 위한 시그널 / 슬롯 모음
        self.signal_login_commConnect()                     # 로그인 요청 함수
        self.get_account_info()                             # 계좌번호 가져오기
        self.get_server()                                   # 서버구분 / 서버별 비밀번호 가져오기
        self.detail_account_info()                          # 예수금 요청 시그널 포함
        self.detail_account_mystock()                       # 계좌평가잔고내역 가져오기
        # ==============================================================================================================

    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')        # 레지스트리에 저장된 API 모듈 불러오기

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)        # 로그인 관련 이벤트
        self.OnReceiveTrData.connect(self.trdata_slot)      # TR 요청 관련 이벤트

    def login_slot(self, err_code):
        print(errors(err_code)[1])
        self.login_event_loop.exit()

    def signal_login_commConnect(self):
        self.dynamicCall('CommConnect()')                   # 로그인 요청 시그널
        self.login_event_loop.exec_()                       # 이벤트 루프 실행
    
    def get_account_info(self):
        account_list = self.dynamicCall('GetLoginInfo(QString)', 'ACCNO')           # 계좌번호 반환
        account_num = account_list.split(';')[0]
        
        self.account_num = account_num
        
        print('계좌번호 : %s' % account_num)

    # 서버 구분
    def get_server(self):
        server_gubun = self.dynamicCall('GetLoginInfo(QString)', 'GetServerGubun')  # 서버구분 : 1: 모의투자 / 나머지: 실서버
        self.server_gubun = server_gubun
        if server_gubun == '1':
            self.server = '모의투자'
            self.pwd = '0000'
        else:
            self.server = '실제투자'  # 실제 투자 시, 입력 or pwd 파일 읽어오기
            f = open('D:/week1/security/pwd.csv')
            lines = f.readlines()
            self.pwd = lines[1].split(',')[1]

    def detail_account_info(self, next='0'):
        self.set_input_value('계좌번호', self.account_num)
        self.set_input_value('비밀번호', self.pwd)
        self.set_input_value('비밀번호입력매체구분', '00')
        self.set_input_value('조회구분', '1')
        self._comm_rq_data('예수금상세현황요청', 'opw00001', next, self.screen_my_info)

    def detail_account_mystock(self, next='0'):
        self.set_input_value('계좌번호', self.account_num)
        self.set_input_value('비밀번호', self.pwd)
        self.set_input_value('비밀번호입력매체구분', '00')
        self.set_input_value('조회구분', '1')
        self._comm_rq_data('계좌평가잔고내역요청', 'opw00018', next, self.screen_my_info)

    def set_input_value(self, id, value):
        self.dynamicCall('SetInputValue(QString, QString)', id, value)

    def _comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall('CommRqData(QString, QString, int, QString)', rqname, trcode, next, screen_no)
        self.tr_event_loop.exec_()

    def _get_comm_data(self, trcode, rqname, index, item_name):
        ret = self.dynamicCall('GetCommData(QString, QString, int, QString)', trcode, rqname, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall('GetRepeatCnt(QString, QString)', trcode, rqname)
        return ret

    def _is_cmp_name(self, code):
        ret = self.dynamicCall('GetMasterCodeName(QString)', code).strip()
        return ret

    def _last_price(self, code):
        ret = int(self.dynamicCall('GetMasterLastPrice(QString)', code).strip())
        return ret

    def trdata_slot(self, screen_num, rqname, trcode, record_name, next):
        if rqname == '예수금상세현황요청':
            deposit = self._get_comm_data(trcode, rqname, 0, '예수금')
            self.deposit = int(deposit)

            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4

            output_deposit = self._get_comm_data(trcode, rqname, 0, '출금가능금액')
            self.output_deposit = int(output_deposit)

            print('예수금: %s' % self.output_deposit)

            self.stop_screen_cancel(self.screen_my_info)
            self.tr_event_loop.exit()

        elif rqname == '계좌평가잔고내역요청':
            total_buy_money = self._get_comm_data(trcode, rqname, 0, '총매입금액')
            self.total_buy_money = int(total_buy_money)
            total_profit_loss_money = self._get_comm_data(trcode, rqname, 0, '총평가손익금액')
            self.total_profit_loss_money = int(total_profit_loss_money)
            total_profit_loss_rate = self._get_comm_data(trcode, rqname, 0, '총수익률(%)')
            self.total_profit_loss_rate = float(total_profit_loss_rate)

            print('계좌평가잔고내역요청 싱글데이터 : %s | %s | %s' % (self.total_buy_money, self.total_profit_loss_money, self.total_profit_loss_rate))

            rows = self._get_repeat_cnt(trcode, rqname)
            for i in range(rows):
                code = self._get_comm_data(trcode, rqname, i, '종목번호')
                code = code.strip()[1:]
                code_nm = self._get_comm_data(trcode, rqname, i, '종목명')
                stock_quantity = self._get_comm_data(trcode, rqname, i, '보유수량')
                buy_price = self._get_comm_data(trcode, rqname, i, '매입가')
                pl_rate = self._get_comm_data(trcode, rqname, i, '수익률(%)')
                current_price = self._get_comm_data(trcode, rqname, i, '현재가')
                total_chegual_price = self._get_comm_data(trcode, rqname, i, '매입금액')
                possible_quantity = self._get_comm_data(trcode, rqname, i, '매매가능수량')

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict[code] = {}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                pl_rate = float(pl_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({'종목명': code_nm})
                self.account_stock_dict[code].update({'보유수량': stock_quantity})
                self.account_stock_dict[code].update({'매입가': buy_price})
                self.account_stock_dict[code].update({'수익률(%)': pl_rate})
                self.account_stock_dict[code].update({'현재가': current_price})
                self.account_stock_dict[code].update({'매입금액': total_chegual_price})
                self.account_stock_dict[code].update({'매매가능수량': possible_quantity})

                print('종목번호: %s | 종목명: %s | 보유수량: %s | 매입가: %s | 수익률: %s | 현재가: %s' %
                      (code, code_nm, stock_quantity, buy_price, pl_rate, current_price))

            print('next: %s' % next)
            print('계좌에 가지고 있는 종목은 %s '% rows)

            if next == '2':
                self.detail_account_mystock(next='2')
            else:
                self.tr_event_loop.exit()

            self.stop_screen_cancel(self.screen_my_info)


    def stop_screen_cancel(self, screen_no=None):
        self.dynamicCall('DisconnectRealData(QString)', screen_no)      # 스크린 번호 연결 끊기
