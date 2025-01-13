from bottle import Bottle, run, request, template
import time
from threading import Thread

app = Bottle()

# Эмуляция GPIO через переменные
START_BUTTON_STATE = False
FLOW_PULSE_COUNT = 0
RELAY_STATE = False

# Переменные для отслеживания состояния
flow_rate = 0
current_volume = 0.0
nominal_volume = 100.0
is_filling = False

# Функция для обновления данных
def update_flow_rate():
    global flow_rate, current_volume, is_filling
    PULSES_PER_LITER = 1000
    while True:
        if is_filling:
            start_pulses = FLOW_PULSE_COUNT
            time.sleep(1)
            flow_rate = FLOW_PULSE_COUNT - start_pulses
            current_volume += flow_rate / PULSES_PER_LITER
            if current_volume >= nominal_volume:
                is_filling = False
                RELAY_STATE = False
        else:
            time.sleep(1)

thread = Thread(target=update_flow_rate)
thread.daemon = True
thread.start()

# Веб-интерфейс
@app.route('/')
def index():
    return template('''<h1>Управление системой слива</h1>
        <p>Текущая скорость потока: {{flow_rate}} имп./сек</p>
        <p>Текущий объём: {{current_volume}} литров</p>
        <p>Номинальный объём: {{nominal_volume}} литров</p>
        <p>Статус: {{status}}</p>
        <button onclick="startFilling()">Начать слив</button>
        <button onclick="stopFilling()">Остановить слив</button>
        <script>
            async function startFilling() {
                await fetch("/start", { method: "POST" });
                updatePage();
            }
            async function stopFilling() {
                await fetch("/stop", { method: "POST" });
                updatePage();
            }
            async function updatePage() {
                const response = await fetch("/status");
                const data = await response.json();
                document.body.innerHTML = `<h1>Управление системой слива</h1>
                    <p>Текущая скорость потока: ${data.flow_rate} имп./сек</p>
                    <p>Текущий объём: ${data.current_volume} литров</p>
                    <p>Номинальный объём: ${data.nominal_volume} литров</p>
                    <p>Статус: ${data.is_filling ? 'Слив идёт' : 'Слив остановлен'}</p>
                    <button onclick="startFilling()">Начать слив</button>
                    <button onclick="stopFilling()">Остановить слив</button>`;
            }
            setInterval(updatePage, 2000);
        </script>''', 
        flow_rate=flow_rate, 
        current_volume=current_volume, 
        nominal_volume=nominal_volume, 
        status="Слив идёт" if is_filling else "Слив остановлен"
    )

@app.post('/start')
def start_filling():
    global is_filling, RELAY_STATE
    is_filling = True
    RELAY_STATE = True
    return {"status": "started"}

@app.post('/stop')
def stop_filling():
    global is_filling, RELAY_STATE
    is_filling = False
    RELAY_STATE = False
    return {"status": "stopped"}

@app.get('/status')
def get_status():
    return {
        "flow_rate": flow_rate,
        "current_volume": current_volume,
        "nominal_volume": nominal_volume,
        "is_filling": is_filling
    }

if __name__ == '__main__':
    run(app, host='127.0.0.1', port=5000)
