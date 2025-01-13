Real-Time Traffic Monitoring and DDoS Detection System

This project aims to address the increasing problem of DDoS (Distributed Denial-of-Service) attacks, which can overload websites with fake traffic and make them inaccessible. The system combines deep learning with the Kalman filter to detect unusual traffic patterns and potential DDoS attacks in real time.

🔍 How the System Works
Traffic Data Monitoring: The system collects traffic data from websites to analyze the flow of visitors.
Deep Learning Model: The collected data is processed using a deep learning model (LSTM) to predict normal traffic patterns.
Kalman Filter: The Kalman filter is used to remove noise from the data, making it easier to detect irregular spikes in traffic.
DDoS Detection: When traffic exceeds a certain threshold, the system triggers an alert, indicating a possible DDoS attack.
💡 Advantages
Real-Time Detection: The system can detect potential DDoS attacks within a minute, allowing website administrators to respond quickly.
Noise Filtering: The Kalman filter improves accuracy by filtering out random fluctuations in traffic data.
User-Friendly Interface: The Flask-based interface displays traffic data visually, making it easy for users to monitor website activity.
Cost-Effective: Unlike commercial DDoS prevention tools, this system is designed to be free and accessible to smaller websites.
Social Responsibility: The project includes a detailed user guide to help non-experts easily set up and use the system.
⚠️ Limitations
Initial Setup Time: The system requires initial data collection and training, which takes about a minute.
False Positives: The system may trigger alerts for non-malicious traffic spikes, such as during marketing campaigns or popular content releases.
Resource Usage: Running a deep learning model continuously can be resource-intensive, which may not be suitable for all servers.
Advanced Threats: The system may not detect highly sophisticated attacks that mimic normal traffic patterns.
