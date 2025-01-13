from bottle import Bottle, run, request, template
import time
from threading import Thread

app = Bottle()

# Эмуляция GPIO через переменные
START_BUTTON_STATE = False
ANALOG_FLOW_RATE = 0.0  # Аналоговый сигнал расходомера (л/с)
RELAY_STATE = False
PUMP_STATE = False  # Состояние насоса

# Переменные для отслеживания состояния
received_volume = 0.0
nominal_volume = 100.0
real_volume = 0.0  # Реальный объём
is_filling = False

# Установка расхода напрямую в коде
DEFAULT_FLOW_RATE = 2.0  # Установленный расход в литрах/секунду
ANALOG_FLOW_RATE = DEFAULT_FLOW_RATE

def update_flow_rate():
    """Обновляет текущий объём в зависимости от состояния слива."""
    global received_volume, real_volume, ANALOG_FLOW_RATE, is_filling, RELAY_STATE, PUMP_STATE
    while True:
        if is_filling and ANALOG_FLOW_RATE > 0:
            time.sleep(1)
            increment = ANALOG_FLOW_RATE
            received_volume += increment
            real_volume += increment  # Увеличиваем реальный объём
            if real_volume >= nominal_volume:  # Остановка по реальному объёму
                is_filling = False
                RELAY_STATE = False  # Остановить слив при достижении номинального объёма
                PUMP_STATE = False
        else:
            time.sleep(1)

# Запускаем поток для обновления расхода
thread = Thread(target=update_flow_rate)
thread.daemon = True
thread.start()

@app.route('/')
def index():
    """Главная страница."""
    return template('''<h1>Управление системой слива</h1>
        <p>Принятый объём: {{received_volume}} литров</p>
        <button onclick="resetVolume()">Обнулить</button>
        <p>Номинальный объём: {{nominal_volume}} литров</p>
        <p>Реальный объём: {{real_volume}} литров</p>
        <p>Текущая скорость потока: {{analog_flow_rate}} л/с</p>
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
                    <p>Текущая скорость потока: ${data.analog_flow_rate} л/с</p>
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
        analog_flow_rate=ANALOG_FLOW_RATE, 
        status="Слив идёт" if is_filling else "Слив остановлен",
        pump_state="Включён" if PUMP_STATE else "Выключен"
    )

@app.post('/start')
def start_filling():
    """Начинает процесс слива."""
    global is_filling, RELAY_STATE, PUMP_STATE
    is_filling = True
    RELAY_STATE = True
    PUMP_STATE = True
    return {"status": "started"}

@app.post('/stop')
def stop_filling():
    """Останавливает процесс слива."""
    global is_filling, RELAY_STATE, PUMP_STATE
    is_filling = False
    RELAY_STATE = False
    PUMP_STATE = False
    return {"status": "stopped"}

@app.post('/reset')
def reset_volume():
    """Обнуляет принятый объём."""
    global received_volume
    received_volume = 0.0
    return {"status": "reset"}

@app.get('/status')
def get_status():
    """Возвращает текущий статус системы."""
    return {
        "received_volume": received_volume,
        "nominal_volume": nominal_volume,
        "real_volume": real_volume,
        "analog_flow_rate": ANALOG_FLOW_RATE,
        "is_filling": is_filling,
        "pump_state": PUMP_STATE
    }

if __name__ == '__main__':
    run(app, host='127.0.0.1', port=5000)
