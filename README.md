# TAC-Dynamics
AIoT-based predictive maintenance and digital twin system for industrial induction motors using Arduino UNO Q, multi-sensor monitoring, real-time visualization, and VFD-based adaptive control.
## System Flowchart

```mermaid
flowchart TD

    A([Start])

    A --> B[Three Phase Induction Motor]

    B --> C1[PZEM-004T<br/>Voltage, Current, Power,<br/>Energy, Frequency, PF]
    B --> C2[DS18B20<br/>Temperature]
    B --> C3[Hall Effect Sensor<br/>Pulse / RPM]
    B --> C4[Vibration Sensor<br/>Vibration Frequency]
    B --> C5[Sound Sensor<br/>Noise / dB]
    B --> C6[HR202 Humidity Sensor<br/>Humidity]

    C1 --> D[Arduino UNO Q 2GB]
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    C6 --> D

    D --> E[Sensor Data Processing]

    E --> E1[Calculate RPM]
    E --> E2[Process PZEM Data]
    E --> E3[Read Temperature]
    E --> E4[Calculate Noise]
    E --> E5[Calculate Vibration]
    E --> E6[Read Humidity]

    E1 --> F[Motor Condition Analysis]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F

    F --> G{Motor Condition}

    G -->|GOOD| H1[Normal Operation]
    G -->|MODERATE| H2[Warning / Monitor]
    G -->|BAD| H3[Maintenance Required]
    G -->|STOPPED| H4[Motor Stopped]

    D --> I[Arduino RouterBridge]

    I --> J[Python HTTP Server]

    J --> K[JSON Sensor Data]

    K --> L[Browser-Based Digital Twin]

    L --> M[Real-Time Dashboard]
    L --> N[Graphs & Trends]
    L --> O[Motor Condition]

    M --> P[Predictive Maintenance]
    N --> P
    O --> P

    P --> Q[Adaptive Control]
    Q --> R[VFD]
    R --> B
```
