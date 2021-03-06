from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
import pandas as pd


def create_action(icon, action, shortcut, tip, conn, parent):
    new_action = QAction(QIcon(icon), action, parent)
    new_action.setShortcut(shortcut)
    new_action.setStatusTip(tip)
    new_action.triggered.connect(conn)
    return new_action


def format_time(sec):
    t = []
    t.append(int(sec % 60))
    minu = sec/60
    t.append(int(minu % 60))
    t.append(int(minu/60))
    t = t[::-1]
    time = [str(tt).zfill(2) for tt in t]
    return ':'.join(time)


def get_metadata_colors(filename):
    try:
        df = pd.read_csv(filename).sort_values(
            by='frame_num', ascending=True)
        return df['diff']
    except:
        return []