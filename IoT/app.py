from bottle import Bottle, run, request, template
import time
from threading import Thread
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

app = Bottle()

#распиновка
REAL_VOLUME_PIN = 17
FLOW_RATE_PIN = 27
PUMP_STATE_PIN = 22

if GPIO:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(REAL_VOLUME_PIN, GPIO.IN)
    GPIO.setup(FLOW_RATE_PIN, GPIO.IN)
    GPIO.setup(PUMP_STATE_PIN, GPIO.OUT)

# Переменные для отслеживания состояния
received_volume = 0.0
nominal_volume = 100.0 # Номинальный объем цистерны
real_volume = 0.0  # Реальный объём
analog_flow_rate = 0.0  # Аналоговый сигнал расходомера (л/с)
is_filling = False
pump_state = False  # Состояние насоса

def read_real_volume():
    # Читает реальный объём из GPIO.
    if GPIO:
        return GPIO.input(REAL_VOLUME_PIN)
    return 0.0

def read_flow_rate():
    # Читает расход из GPIO.
    if GPIO:
        return GPIO.input(FLOW_RATE_PIN)
    return 0.0

def set_pump_state(state):
    # Устанавливает состояние насоса.
    global pump_state
    pump_state = state
    if GPIO:
        GPIO.output(PUMP_STATE_PIN, GPIO.HIGH if state else GPIO.LOW)

def update_flow_rate():
    # Обновляет текущий объём в зависимости от состояния слива.
    global received_volume, real_volume, analog_flow_rate, is_filling
    while True:
        if is_filling:
            time.sleep(1)
            analog_flow_rate = read_flow_rate()
            real_volume = read_real_volume()
            increment = analog_flow_rate
            received_volume += increment
            if real_volume >= nominal_volume:  # Остановка по реальному объёму
                is_filling = False
                set_pump_state(False)
        else:
            time.sleep(1)

# Запускаем поток для обновления расхода
thread = Thread(target=update_flow_rate)
thread.daemon = True
thread.start()

@app.route('/')
def index():
    # Главная страница.
    return template('''<h1>Управление системой слива</h1>
        <p>Принятый объём: {{received_volume}} литров</p>
        <button onclick="resetVolume()">Обнулить</button>
        <p>Номинальный объём: {{nominal_volume}} литров</p>
        <p>Реальный объём: {{real_volume}} литров</p>
        <p>Расход: {{analog_flow_rate}} л/с</p>
        <p>Статус: {{status}}</p>
        <p>Состояние насоса: {{pump_state}}</p>
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
            async function resetVolume() {
                await fetch("/reset", { method: "POST" });
                updatePage();
            }
            async function updatePage() {
                const response = await fetch("/status");
                const data = await response.json();
                document.body.innerHTML = `<h1>Управление системой слива</h1>
                    <p>Принятый объём: ${data.received_volume} литров</p>
                    <button onclick="resetVolume()">Обнулить</button>
                    <p>Номинальный объём: ${data.nominal_volume} литров</p>
                    <p>Реальный объём: ${data.real_volume} литров</p>
                    <p>Расход: ${data.analog_flow_rate} л/с</p>
                    <p>Статус: ${data.is_filling ? 'Слив идёт' : 'Слив остановлен'}</p>
                    <p>Состояние насоса: ${data.pump_state ? 'Включён' : 'Выключен'}</p>
                    <button onclick="startFilling()">Начать слив</button>
                    <button onclick="stopFilling()">Остановить слив</button>`;
            }
            setInterval(updatePage, 2000);
        </script>''', 
        received_volume=received_volume, 
        nominal_volume=nominal_volume, 
        real_volume=real_volume, 
        analog_flow_rate=analog_flow_rate, 
        status="Слив идёт" if is_filling else "Слив остановлен",
        pump_state="Включён" if pump_state else "Выключен"
    )

@app.post('/start')
def start_filling():
    # Начинает процесс слива.
    global is_filling
    is_filling = True
    set_pump_state(True)
    return {"status": "started"}

@app.post('/stop')
def stop_filling():
    # Останавливает процесс слива.
    global is_filling
    is_filling = False
    set_pump_state(False)
    return {"status": "stopped"}

@app.post('/reset')
def reset_volume():
    # Обнуляет принятый объём.
    global received_volume
    received_volume = 0.0
    return {"status": "reset"}

@app.get('/status')
def get_status():
    # Возвращает текущий статус системы.
    return {
        "received_volume": received_volume,
        "nominal_volume": nominal_volume,
        "real_volume": real_volume,
        "analog_flow_rate": analog_flow_rate,
        "is_filling": is_filling,
        "pump_state": pump_state
    }

if __name__ == '__main__':
    run(app, host='127.0.0.1', port=5000)

if GPIO:
    GPIO.cleanup()
