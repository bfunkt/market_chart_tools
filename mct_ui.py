# UI builder for Market Chart Tools
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QDesktopWidget, QLabel

class UI():
    def __init__(self, pg, parent, *args, **kwargs):
        self.parent = parent
        self.pg = pg
        #self.fn = fn
        self.args = args
        self.kwargs = kwargs

        # config
        self.pg.setConfigOptions(antialias=True)
        
        # main window        
        self.win = self.pg.GraphicsLayoutWidget(show=True, title='market chart tools')
        self.win.setGeometry(0, 0, 1600, 900)
        self.win.setWindowTitle('Market Chart Tools')

        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()
        x = ag.width() - self.win.width()
        y = 2 * ag.height() - sg.height() - self.win.height()
        self.win.move(int(x/2), int(y/2))

        #plot object
        self.plot = self.pg.PlotWidget()
        
        #layout object
        self.layout = QtGui.QGridLayout()

        #button objects
        self.btn_go = QtGui.QPushButton('Get data!')
        self.btn_go.clicked.connect(self.btn_go_event)

        self.btn_real = QtGui.QPushButton('Real')
        self.btn_real.clicked.connect(self.btn_real_event)
        self.real_tog = True

        self.btn_next = QtGui.QPushButton('Next')
        self.btn_next.clicked.connect(self.btn_next_event)

        self.btn_show = QtGui.QPushButton('Show')
        self.btn_show.clicked.connect(self.btn_show_event)
        
        self.btn_reset = QtGui.QPushButton('Reset')
        self.btn_reset.clicked.connect(self.btn_reset_event)


        #text objects
        self.text3 = QLabel('')
        self.text3.setStyleSheet("background-color: lightgreen; \
                                    border: 1px solid black;")
        self.text3.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.last_ticker = ''
        self.last_timescale = ''
        self.last_real = ''
        self.text3_tog = False

        # self.arrow = self.pg.ArrowItem(pos=(0, 600), angle=-45)
        # self.plot.addItem(self.arrow)

        #grid layout
        self.win.setLayout(self.layout)

        #register objects
        self.layout.addWidget(self.text3, 5, 0)
        self.layout.addWidget(self.plot, 0, 2, 8, 1)
        self.layout.addWidget(self.btn_go, 0, 0)
        self.layout.addWidget(self.btn_real, 0, 1)
        #self.layout.addWidget(self.btn_next, 2, 0)
        self.layout.addWidget(self.btn_show, 3, 0)
        #self.layout.addWidget(self.btn_reset, 4, 0)


    def add_plot(self):
        self.layout.addWidget(self.plot, 0, 2, 8, 1)

    def win_show(self):
        self.win.show()

    def delete_bgi(self):
        self.layout.removeWidget(self.plot)

    def apply_bgi(self, data, l, h):
        self.bg_up = data[0]
        self.bg_dn = data[1]
        self.bg_wick = data[2]

        self.plot = self.pg.PlotWidget()
        self.plot.addItem(self.bg_wick)
        self.plot.addItem(self.bg_up)
        self.plot.addItem(self.bg_dn)
        self.plot.setYRange(l, h)
        
        self.layout.addWidget(self.plot, 0, 2, 8, 1)

    def btn_go_event(self):
        self.btn_show_event(True)
        self.parent.run(self)

    def btn_real_event(self):
        if self.real_tog:
            self.btn_real.setText('Fake')
            self.real_tog = False
        else:
            self.btn_real.setText('Real')
            self.real_tog = True
        self.win_show()

    def btn_next_event(self):
        pass

    def clear_text3_data(self):
        self.text3.setText('')
        self.text3_tog = False

    def btn_show_event(self, clear_data=False):
        if self.text3_tog == True or clear_data == True:
            self.clear_text3_data()
        else:
            self.text3.setText(f'{self.last_real}\n{self.last_ticker}')
            self.text3_tog = True

    def btn_reset_event(self):
        pass



def main():
    import sys
    import pyqtgraph as pg

    app = QtGui.QApplication([])
    ui = UI(pg)
    ui.win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
   main()