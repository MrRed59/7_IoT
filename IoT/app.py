from bottle import Bottle, run, request, static_file, template
import time
from threading import Thread


app = Bottle()


# Эмуляция GPIO через переменные
START_BUTTON_STATE = False  # Эмулируем состояние кнопки "Старт слива"
FLOW_PULSE_COUNT = 0        # Эмулируем количество импульсов расходомера
RELAY_STATE = False         # Эмулируем состояние реле


# Переменные для отслеживания состояния
flow_rate = 0          # Текущая скорость потока (импульсы/сек)
current_volume = 0.0   # Текущий объём топлива (литры)
nominal_volume = 100.0 # Номинальный объём резервуара (литры)
is_filling = False     # Статус процесса слива
pulse_count = 0        # Количество импульсов от расходомера


# Эмуляция изменения кнопки "Старт слива"
def emulate_button_press():
   global START_BUTTON_STATE
   START_BUTTON_STATE = True
   time.sleep(0.5)
   START_BUTTON_STATE = False


# Эмуляция импульсов расходомера
def emulate_flow_pulses(pulse_count, interval=0.1):
   global FLOW_PULSE_COUNT
   for _ in range(pulse_count):
       FLOW_PULSE_COUNT += 1
       time.sleep(interval / 2)
       FLOW_PULSE_COUNT -= 1
       time.sleep(interval / 2)


# Функция для обновления данных
def update_flow_rate():
   global flow_rate, current_volume, pulse_count, is_filling
   PULSES_PER_LITER = 1000  # Коэффициент расходомера (зависит от модели)
   while True:
       if is_filling:
           start_pulses = FLOW_PULSE_COUNT
           time.sleep(1)
           flow_rate = FLOW_PULSE_COUNT - start_pulses
           current_volume += (flow_rate / PULSES_PER_LITER)
           if current_volume >= nominal_volume:
               is_filling = False
               RELAY_STATE = False  # Остановить слив
       else:
           time.sleep(1)


# Запускаем поток для обновления расхода
thread = Thread(target=update_flow_rate)
thread.daemon = True
thread.start()


# Веб-интерфейс
@app.route('/')
def index():
   return template('<h1>Слив топлива из бензовоза на АЗС</h1>\
                    <p>Текущая скорость потока: {{flow_rate}}</p>\
                    <p>Текущий объём: {{current_volume}} литров</p>\
                    <p>Номинальный объём: {{nominal_volume}} литров</p>\
                    <p>Статус: {{"Слив идёт" if is_filling else "Слив остановлен"}}</p>\
                    <button onclick="startFilling()">Начать слив</button>\
                    <button onclick="stopFilling()">Остановить слив</button>\
                    <button onclick="emulateButton()">Тест кнопка</button>\
                    <button onclick="emulateFlow()">Тест расходомер</button>\
                    <script>\
                        function startFilling() { fetch("/start", { method: "POST" }).then(res => res.json()).then(console.log); }\
                        function stopFilling() { fetch("/stop", { method: "POST" }).then(res => res.json()).then(console.log); }\
                        function emulateButton() { fetch("/emulate_button", { method: "POST" }).then(res => res.json()).then(console.log); }\
                        function emulateFlow() { fetch("/emulate_flow", { method: "POST", body: JSON.stringify({ pulses: 50 }), headers: { "Content-Type": "application/json" }}).then(res => res.json()).then(console.log); }\
                    </script>',
                    flow_rate=flow_rate,
                    current_volume=current_volume,
                    nominal_volume=nominal_volume,
                    is_filling=is_filling)


@app.post('/start')
def start_filling():
   global is_filling, RELAY_STATE
   if not is_filling:
       is_filling = True
       RELAY_STATE = True  # Начать слив
   return {"status": "started"}


@app.post('/stop')
def stop_filling():
   global is_filling, RELAY_STATE
   is_filling = False
   RELAY_STATE = False  # Остановить слив
   return {"status": "stopped"}


@app.post('/emulate_button')
def emulate_button():
   emulate_button_press()
   return {"status": "button pressed"}


@app.post('/emulate_flow')
def emulate_flow():
   try:
       data = request.json
       pulses = data.get('pulses', 10)
       emulate_flow_pulses(pulses)
       return {"status": f"{pulses} pulses sent"}
   except Exception as e:
       return {"error": str(e)}


if __name__ == '__main__':
   run(app, host='127.0.0.1', port=5000)


from bottle import Bottle, run, request, static_file, template
import time
from threading import Thread


app = Bottle()


# Эмуляция GPIO через переменные
START_BUTTON_STATE = False  # Эмулируем состояние кнопки "Старт слива"
FLOW_PULSE_COUNT = 0        # Эмулируем количество импульсов расходомера
RELAY_STATE = False         # Эмулируем состояние реле


# Переменные для отслеживания состояния
flow_rate = 0          # Текущая скорость потока (импульсы/сек)
current_volume = 0.0   # Текущий объём топлива (литры)
nominal_volume = 100.0 # Номинальный объём резервуара (литры)
is_filling = False     # Статус процесса слива
pulse_count = 0        # Количество импульсов от расходомера


# Эмуляция изменения кнопки "Старт слива"
def emulate_button_press():
   global START_BUTTON_STATE
   START_BUTTON_STATE = True
   time.sleep(0.5)
   START_BUTTON_STATE = False


# Эмуляция импульсов расходомера
def emulate_flow_pulses(pulse_count, interval=0.1):
   global FLOW_PULSE_COUNT
   for _ in range(pulse_count):
       FLOW_PULSE_COUNT += 1
       time.sleep(interval / 2)
       FLOW_PULSE_COUNT -= 1
       time.sleep(interval / 2)


# Функция для обновления данных
def update_flow_rate():
   global flow_rate, current_volume, pulse_count, is_filling
   PULSES_PER_LITER = 1000  # Коэффициент расходомера (зависит от модели)
   while True:
       if is_filling:
           start_pulses = FLOW_PULSE_COUNT
           time.sleep(1)
           flow_rate = FLOW_PULSE_COUNT - start_pulses
           current_volume += (flow_rate / PULSES_PER_LITER)
           if current_volume >= nominal_volume:
               is_filling = False
               RELAY_STATE = False  # Остановить слив
       else:
           time.sleep(1)


# Запускаем поток для обновления расхода
thread = Thread(target=update_flow_rate)
thread.daemon = True
thread.start()


# Веб-интерфейс
@app.route('/')
def index():
   return template('<h1>Слив топлива из бензовоза на АЗС</h1>\
                    <p>Текущая скорость потока: {{flow_rate}}</p>\
                    <p>Текущий объём: {{current_volume}} литров</p>\
                    <p>Номинальный объём: {{nominal_volume}} литров</p>\
                    <p>Статус: {{"Слив идёт" if is_filling else "Слив остановлен"}}</p>\
                    <button onclick="startFilling()">Начать слив</button>\
                    <button onclick="stopFilling()">Остановить слив</button>\
                    <button onclick="emulateButton()">Тест кнопка</button>\
                    <button onclick="emulateFlow()">Тест расходомер</button>\
                    <script>\
                        function startFilling() { fetch("/start", { method: "POST" }).then(res => res.json()).then(console.log); }\
                        function stopFilling() { fetch("/stop", { method: "POST" }).then(res => res.json()).then(console.log); }\
                        function emulateButton() { fetch("/emulate_button", { method: "POST" }).then(res => res.json()).then(console.log); }\
                        function emulateFlow() { fetch("/emulate_flow", { method: "POST", body: JSON.stringify({ pulses: 50 }), headers: { "Content-Type": "application/json" }}).then(res => res.json()).then(console.log); }\
                    </script>',
                    flow_rate=flow_rate,
                    current_volume=current_volume,
                    nominal_volume=nominal_volume,
                    is_filling=is_filling)


@app.post('/start')
def start_filling():
   global is_filling, RELAY_STATE
   if not is_filling:
       is_filling = True
       RELAY_STATE = True  # Начать слив
   return {"status": "started"}


@app.post('/stop')
def stop_filling():
   global is_filling, RELAY_STATE
   is_filling = False
   RELAY_STATE = False  # Остановить слив
   return {"status": "stopped"}


@app.post('/emulate_button')
def emulate_button():
   emulate_button_press()
   return {"status": "button pressed"}


@app.post('/emulate_flow')
def emulate_flow():
   try:
       data = request.json
       pulses = data.get('pulses', 10)
       emulate_flow_pulses(pulses)
       return {"status": f"{pulses} pulses sent"}
   except Exception as e:
       return {"error": str(e)}


if __name__ == '__main__':
   run(app, host='127.0.0.1', port=5000)