# TAC-Dynamics
AIoT-based predictive maintenance and digital twin system for industrial induction motors using Arduino UNO Q, multi-sensor monitoring, real-time visualization, and VFD-based adaptive control.

## System Flowchart

```mermaid
flowchart TD

    A([Start])

    A --> B[Three-Phase Induction Motor]

    B --> C1[PZEM-004T<br/>Voltage • Current • Power<br/>Energy • Frequency • PF]
    B --> C2[DS18B20<br/>Motor Temperature]
    B --> C3[Inductive Proximity Sensor<br/>Motor Speed / RPM]
    B --> C4[Hall-Effect Sensor<br/>Rotational / Magnetic Sensing]
    B --> C5[Vibration Sensor<br/>Mechanical Condition]
    B --> C6[Sound Sensor<br/>Noise / Acoustic Condition]
    B --> C7[Humidity Sensor<br/>Environmental Condition]

    C1 --> D[Arduino UNO Q<br/>Edge Computing]
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    C6 --> D
    C7 --> D

    D --> E[Data Acquisition & Processing]

    E --> F[Motor Condition Analysis]

    F --> G{Motor Condition}

    G -->|GOOD| H1[Normal Operation]
    G -->|MODERATE| H2[Warning / Continue Monitoring]
    G -->|BAD| H3[Maintenance Required]
    G -->|STOPPED| H4[Motor Stopped]

    D --> I[Arduino RouterBridge]

    I --> J[Python HTTP Server]

    J --> K[JSON Data API<br/>GET /data]

    K --> L[Browser-Based Digital Twin]

    L --> M[Real-Time Monitoring]
    L --> N[Graphs & Historical Trends]
    L --> O[Motor Condition Display]

    M --> P[Predictive Maintenance]
    N --> P
    O --> P

    P --> Q[Adaptive Control Decision]

    Q --> R[VFD]
    R --> B
```

## System Algorithm

```mermaid
flowchart TD

    A([Start])

    A --> B[Initialize Arduino UNO Q]

    B --> C[Initialize Sensors<br/>PZEM • DS18B20 • Proximity • Hall<br/>Vibration • Sound • Humidity]

    C --> D[Initialize Serial / I2C / RouterBridge]

    D --> E[Read Motor Electrical Parameters]

    E --> E1[Voltage]
    E --> E2[Current]
    E --> E3[Power]
    E --> E4[Energy]
    E --> E5[Frequency]
    E --> E6[Power Factor]

    E1 --> F[Read Motor Condition Sensors]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F

    F --> F1[Temperature]
    F --> F2[RPM / Speed]
    F --> F3[Vibration]
    F --> F4[Noise]
    F --> F5[Humidity]

    F1 --> G[Process Sensor Data]
    F2 --> G
    F3 --> G
    F4 --> G
    F5 --> G

    G --> H[Calculate Motor Condition Score]

    H --> I{RPM = 0?}

    I -->|Yes| J[Condition = STOPPED]
    I -->|No| K[Evaluate Operating Parameters]

    K --> L{Condition Score}

    L -->|0–3| M[GOOD]
    L -->|4–7| N[MODERATE]
    L -->|8 or More| O[BAD]

    J --> P[Update LCD & Serial Output]
    M --> P
    N --> P
    O --> P

    P --> Q[Publish Sensor Values<br/>through RouterBridge]

    Q --> R[Python HTTP Server]

    R --> S{GET /data Request?}

    S -->|No| R
    S -->|Yes| T[Call Bridge Functions]

    T --> U[Create JSON Response]

    U --> V[Send HTTP 200 Response]

    V --> W[Browser Digital Twin]

    W --> X[Display Real-Time Values]

    X --> Y[Store History Locally]

    Y --> Z[Display Graphs & Trends]

    Z --> AA[Predictive Maintenance Analysis]

    AA --> AB[Adaptive Control / VFD]

    AB --> AC([Repeat Monitoring Loop])

    AC --> E
```
