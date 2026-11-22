import serial
import time
import threading
import sys
from datetime import datetime

# =========================================================================
# НАСТРОЙКИ ПОДКЛЮЧЕНИЯ И ФАЙЛОВ
# =========================================================================
COM_PORT = "COM4"          # Укажите ваш порт (посмотреть в Диспетчере устройств)
BAUD_RATE = 230400         # Скорость UART контроллера
COMMANDS_FILE = "commands.txt"

# Имя лог-файла с привязкой к текущей дате и времени
LOG_FILE = f"ad5941_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# Символ окончания строки для CLI контроллера в ASCII
LINE_ENDING = "\r\n"

# Список допустимых команд контроллера
VALID_COMMANDS = {"status", "adinit", "calib", "bateis","eison","eisoff","charge","load"}

# Словарь обязательных маркеров завершения для длительных команд:
# "команда": ("ожидаемый_текст_окончания", таймаут_в_секундах)
COMMAND_COMPLETION_MARKERS = {
    "calib": ("CalibStop", 60.0*10),          # Ждем CalibStop максимум 2 минуты
    "bateis": ("BatMeasureStop", 1800.0)    # Ждем BatMeasureStop максимум 30 минут (с учетом НЧ)
}

# =========================================================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ ПОТОКА ЧТЕНИЯ
# =========================================================================
stop_reading = False
last_received_lines = []
lines_lock = threading.Lock()


def serial_reader(ser, log_file_obj):
    """Фоновый поток: непрерывно читает ASCII-данные из COM-порта, выводит в консоль и пишет в файл."""
    global stop_reading
    while not stop_reading:
        try:
            if ser.in_waiting > 0:
                raw_line = ser.readline()
                # Декодируем входящий поток как ASCII и убираем \r\n по краям
                line = raw_line.decode("ascii", errors="replace").strip("\r\n")
                
                if line:
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    formatted_output = f"[{timestamp}] {line}"
                    
                    # Вывод на экран
                    print(formatted_output)
                    
                    # Запись в файл с немедленным сбросом буфера на диск
                    log_file_obj.write(formatted_output + "\n")
                    log_file_obj.flush()
                    
                    # Сохраняем чистую строку в буфер для проверки маркеров
                    with lines_lock:
                        last_received_lines.append(line)
                        if len(last_received_lines) > 100:
                            last_received_lines.pop(0)
            else:
                time.sleep(0.01)
        except serial.SerialException as e:
            print(f"\n[ОШИБКА UART] Потеряна связь с портом: {e}")
            stop_reading = True
            break
        except Exception as e:
            print(f"\n[ОШИБКА ЧТЕНИЯ] {e}")


def wait_for_marker(marker, timeout_sec):
    """Блокирует выполнение сценария, пока контроллер не пришлет заданный маркер."""
    start_time = time.time()
    while (time.time() - start_time) < timeout_sec:
        if stop_reading:
            return False
            
        with lines_lock:
            for line in last_received_lines:
                if marker in line:
                    return True
        time.sleep(0.05)
        
    print(f"\n[ТАЙМАУТ] Ошибка: не получено сообщение '{marker}' за {timeout_sec} сек!")
    return False


def main():
    global stop_reading
    
    # 1. Читаем сценарий команд из файла
    try:
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            raw_commands = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except FileNotFoundError:
        print(f"[ОШИБКА] Файл сценария '{COMMANDS_FILE}' не найден!")
        sys.exit(1)

    if not raw_commands:
        print(f"[ОШИБКА] Файл '{COMMANDS_FILE}' пуст.")
        sys.exit(1)

    # 2. Открываем COM-порт и файл логов
    try:
        ser = serial.Serial(
            port=COM_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5
        )
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    except serial.SerialException as e:
        print(f"[ОШИБКА] Не удалось открыть порт {COM_PORT}: {e}")
        sys.exit(1)

    print(f"Подключено к {COM_PORT} ({BAUD_RATE} бод). Режим передачи: ASCII.\nЛог пишется в: {LOG_FILE}\n" + "-"*60)

    with open(LOG_FILE, "w", encoding="utf-8") as log_file:
        reader_thread = threading.Thread(target=serial_reader, args=(ser, log_file), daemon=True)
        reader_thread.start()
        
        # Пауза на случай перезагрузки контроллера при открытии порта
        time.sleep(1.0)

        try:
            # 3. Выполняем команды по списку
            for item in raw_commands:
                # Директива жесткой паузы: SLEEP: 5
                if item.upper().startswith("SLEEP:"):
                    delay = float(item.split(":", 1)[1].strip())
                    print(f"--- Пауза {delay} сек ---")
                    time.sleep(delay)
                    continue

                # Ручная директива ожидания (если понадобится для других нужд): WAIT: маркер, таймаут
                if item.upper().startswith("WAIT:"):
                    params = item.split(":", 1)[1].split(",")
                    marker = params[0].strip()
                    timeout = float(params[1].strip()) if len(params) > 1 else 300.0
                    print(f"--- Ожидание маркера '{marker}' (таймаут {timeout} с) ---")
                    wait_for_marker(marker, timeout)
                    continue

                # Проверка команды по белому списку
                cmd_base = item.split()[0].lower()
                if cmd_base not in VALID_COMMANDS:
                    print(f"[ПРЕДУПРЕЖДЕНИЕ] Неизвестная команда '{item}', отправка пропущена.")
                    continue

                # Кодируем команду строго в ASCII
                try:
                    ascii_payload = (item + LINE_ENDING).encode("ascii")
                except UnicodeEncodeError:
                    print(f"[ОШИБКА КОДИРОВКИ] Команда '{item}' содержит не-ASCII символы и пропущена!")
                    continue

                # Очищаем историю последних строк ПЕРЕД отправкой команды,
                # чтобы не поймать маркер от предыдущего запуска
                with lines_lock:
                    last_received_lines.clear()

                # Отправка ASCII-байтов в контроллер
                msg = f"\n>>> ОТПРАВКА (ASCII): {item}"
                print(msg)
                log_file.write(msg + "\n")
                
                ser.write(ascii_payload)
                ser.flush()

                # Проверяем, требует ли отправленная команда ожидания специального маркера завершения
                if cmd_base in COMMAND_COMPLETION_MARKERS:
                    expected_stop_marker, max_timeout = COMMAND_COMPLETION_MARKERS[cmd_base]
                    print(f"--- Процесс запущен. Ожидание '{expected_stop_marker}' (макс. {max_timeout} с) ---")
                    
                    success = wait_for_marker(expected_stop_marker, max_timeout)
                    if success:
                        print(f"--- Получено '{expected_stop_marker}'. Процедура завершена! ---")
                    else:
                        print("[КРИТИЧЕСКАЯ ОШИБКА] Остановка сценария из-за таймаута процесса.")
                        break
                else:
                    # Для быстрых команд (status, adinit) делаем небольшую стандартную паузу
                    time.sleep(0.3)

            print("\n" + "-"*60 + "\nВыполнение сценария завершено.")
            time.sleep(1.0)

        except KeyboardInterrupt:
            print("\n[ПРЕРВАНО] Выполнение остановлено пользователем (Ctrl+C).")
        finally:
            stop_reading = True
            reader_thread.join(timeout=1.0)
            ser.close()
            print(f"Порт {COM_PORT} закрыт. Данные сохранены в {LOG_FILE}.")


if __name__ == "__main__":
    main()
