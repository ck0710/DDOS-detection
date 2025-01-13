from flask import Flask, render_template, jsonify
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from pykalman import KalmanFilter
import matplotlib.pyplot as plt
import io
import base64
import threading
import time

plt.switch_backend('Agg')

app = Flask(__name__)

# 전역 변수 설정
traffic_data = {"time": [], "traffic": []}
kalman_threshold = None
alert_triggered = False
monitoring = False

def generate_traffic_data(noise_level=0.2, attack=False, attack_magnitude=7):
    base_pattern = np.sin(time.time()) * 5 + 50 + np.random.normal(0, noise_level * 10)
    
    # 공격 시 트래픽 급증
    if attack:
        base_pattern += attack_magnitude + np.random.normal(0, 2)
    
    return base_pattern

# 칼만 필터로 노이즈 추정
def apply_kalman_filter(observed_traffic):
    kf = KalmanFilter(initial_state_mean=0, n_dim_obs=1)
    kf = kf.em(observed_traffic, n_iter=5)
    state_means, _ = kf.filter(observed_traffic)
    return state_means.ravel()

# 딥러닝 모델 생성 및 학습
def build_and_train_model(traffic_data):
    model = Sequential([
        LSTM(64, input_shape=(1, 1), return_sequences=True),
        Dropout(0.2),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    early_stopping = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)
    model.fit(traffic_data.reshape(-1, 1, 1), traffic_data, epochs=10, batch_size=32, callbacks=[early_stopping], verbose=0)
    return model

# 실시간 트래픽 학습 및 DDoS 감지
def monitor_traffic():
    global traffic_data, kalman_threshold, alert_triggered, monitoring

    # 트래픽 데이터 수집 및 학습 (초기 1분)
    accumulated_traffic = []
    for _ in range(60):  # 총 1분 동안 데이터 수집
        traffic = generate_traffic_data()
        accumulated_traffic.append(traffic)
        traffic_data["time"].append(len(accumulated_traffic))
        traffic_data["traffic"].append(traffic)
        time.sleep(1)

    # 학습 후 칼만 필터 적용
    model = build_and_train_model(np.array(accumulated_traffic))
    filtered_traffic = apply_kalman_filter(np.array(accumulated_traffic))
    residuals = np.array(accumulated_traffic) - filtered_traffic
    kalman_threshold = np.mean(residuals) + 2 * np.std(residuals)
    print("트래픽 딥러닝을 완료하였습니다. DDoS 방어를 시작하겠습니다.")

    # 실시간 모니터링 및 DDoS 감지
    time_step = 0
    while monitoring:
        traffic = generate_traffic_data(attack=(time_step >= 40))  # 1분 40초 후 DDoS 공격 시뮬레이션
        traffic_data["time"].append(time_step + 60)  # 기존 데이터 이후 시간 추가
        traffic_data["traffic"].append(traffic)
        
        if len(traffic_data["time"]) > 100:  # 최근 100개 데이터만 유지
            traffic_data["time"].pop(0)
            traffic_data["traffic"].pop(0)
        
        current_residual = traffic - filtered_traffic[time_step % 60]  # 학습된 필터 사용

        if abs(current_residual) > kalman_threshold:
            alert_triggered = True
            break

        time.sleep(1)
        time_step += 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-monitoring', methods=['POST'])
def start_monitoring():
    global monitoring, alert_triggered
    monitoring = True
    alert_triggered = False
    threading.Thread(target=monitor_traffic).start()
    return jsonify({"status": "Monitoring started"})

@app.route('/update-traffic')
def update_traffic():
    fig, ax = plt.subplots()
    ax.plot(traffic_data["time"], traffic_data["traffic"], color='blue')
    ax.set_title('Traffic Analysis')

    # 칼만 필터 임계값을 1분 이후부터 표시
    if kalman_threshold is not None:
        ax.axhline(y=kalman_threshold, color='green', linestyle='--', label="Kalman Threshold")
    
    # 경고 발생 시 빨간색으로 경고 표시
    if alert_triggered:
        ax.text(50, kalman_threshold + 0.5, "DDoS Detected! 5초 후 종료합니다.", color='red', fontsize=12, ha='center')
        ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # 경고 발생 시 5초 후 셧다운
    if alert_triggered:
        threading.Timer(5, stop_monitoring).start()

    return jsonify({'plot_url': plot_url, 'alert': alert_triggered})

def stop_monitoring():
    global monitoring
    monitoring = False

if __name__ == '__main__':
    app.run(debug=True)
