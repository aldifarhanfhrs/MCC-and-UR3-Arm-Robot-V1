import PySimpleGUI as sg
import threading
from datetime import datetime


def get_current_datetime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


def update_datetime(window):
    while True:
        current_datetime = get_current_datetime()
        window['-DATETIME-'].update(current_datetime)
        sg.sleep(1)  # Tunggu selama 1 detik sebelum memperbarui waktu

# ... Kode program Anda yang sudah ada ...


# Membuat tata letak GUI
layout = [
    # ... Komponen GUI Anda yang sudah ada ...
    [sg.Text('Tanggal dan Waktu:', size=(20, 1), font=(
        'Helvetica', 14), justification='center')],
    [sg.Text(get_current_datetime(), size=(20, 1), font=(
        'Helvetica', 14), justification='center', key='-DATETIME-')]
]

# Membuat jendela GUI
window = sg.Window('Judul Jendela', layout)

# ... Kode program Anda yang sudah ada ...

# Membuat thread untuk memperbarui waktu
update_thread = threading.Thread(
    target=update_datetime, args=(window,), daemon=True)
update_thread.start()

while True:
    event, values = window.read()

    # ... Penanganan acara lainnya di jendela GUI Anda ...

    # Penanganan acara untuk tombol keluar
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

# ... Kode program Anda yang sudah ada ...

window.close()
