from http.server import HTTPServer, BaseHTTPRequestHandler
from arduino.app_utils import App, Bridge
import json
import time


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/data":

            try:
                data = {
                    "voltage": float(Bridge.call("get_voltage")),
                    "current": float(Bridge.call("get_current")),
                    "power": float(Bridge.call("get_power")),
                    "energy": float(Bridge.call("get_energy")),
                    "frequency": float(Bridge.call("get_frequency")),
                    "pf": float(Bridge.call("get_pf")),
                    "rpm": float(Bridge.call("get_rpm")),
                    "temperature": float(Bridge.call("get_temperature")),
                    "noise": int(float(Bridge.call("get_noise"))),
                    "vibration": int(float(Bridge.call("get_vibration"))),
                    "humidity": int(float(Bridge.call("get_humidity")))
                }

                response = json.dumps(data)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()

                self.wfile.write(response.encode())

            except Exception as e:

                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                self.wfile.write(
                    json.dumps({"error": str(e)}).encode()
                )

            return


        if self.path == "/":

            html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Induction Motor · Digital Twin</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>

:root{
  --bg:#0a0d12;
  --bg-alt:#0e1218;
  --panel:#131822;
  --panel-2:#161d29;
  --border:#232c3a;
  --text:#e9eef5;
  --text-dim:#7c8797;
  --text-faint:#4b5566;
  --amber:#ffb020;
  --cyan:#38d9c9;
  --red:#ff5d4a;
  --green:#4fd67a;
  --blue:#5b9dff;
  --violet:#a48bff;
  --track:#1c2432;
  --radius:14px;
  --mono: 'IBM Plex Mono', monospace;
  --sans: 'Space Grotesk', sans-serif;
}

*{box-sizing:border-box;}

html,body{
  margin:0;
  padding:0;
  background:
    radial-gradient(ellipse 900px 500px at 15% -10%, #14202a 0%, transparent 60%),
    radial-gradient(ellipse 700px 500px at 110% 10%, #1a1424 0%, transparent 55%),
    var(--bg);
  color:var(--text);
  font-family:var(--sans);
  min-height:100vh;
}

::selection{ background:var(--amber); color:#161200; }

.wrap{
  max-width:1240px;
  margin:0 auto;
  padding:22px 22px 60px;
}


.topbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
  padding-bottom:20px;
  border-bottom:1px solid var(--border);
  margin-bottom:26px;
  flex-wrap:wrap;
}

.brand{
  display:flex;
  align-items:center;
  gap:12px;
}

.brand-mark{
  width:38px;height:38px;
  border-radius:9px;
  background:linear-gradient(145deg,var(--cyan),#1c8c81);
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 0 1px rgba(56,217,201,.25), 0 0 24px -6px rgba(56,217,201,.6);
  flex:none;
}
.brand-mark svg{width:20px;height:20px;}

.brand-text h1{
  font-size:17px;
  margin:0;
  font-weight:600;
  letter-spacing:0.2px;
}
.brand-text p{
  margin:2px 0 0;
  font-size:12.5px;
  color:var(--text-dim);
}

.topbar-right{
  display:flex;
  align-items:center;
  gap:14px;
}

.status-pill{
  display:flex;
  align-items:center;
  gap:8px;
  font-family:var(--mono);
  font-size:12px;
  color:var(--text-dim);
  padding:7px 12px;
  border:1px solid var(--border);
  border-radius:100px;
  background:var(--panel);
}
.status-dot{
  width:8px;height:8px;border-radius:50%;
  background:var(--green);
  box-shadow:0 0 8px 1px var(--green);
}
.status-dot.err{ background:var(--red); box-shadow:0 0 8px 1px var(--red); animation:none; }
.status-dot.live{ animation:pulse-dot 1.6s ease-in-out infinite; }

@keyframes pulse-dot{
  0%,100%{ opacity:1; }
  50%{ opacity:.35; }
}

.btn{
  font-family:var(--sans);
  font-weight:600;
  font-size:13.5px;
  color:#101418;
  background:var(--amber);
  border:none;
  padding:10px 18px;
  border-radius:9px;
  cursor:pointer;
  letter-spacing:0.2px;
  transition:transform .15s ease, box-shadow .15s ease;
  box-shadow:0 0 0 1px rgba(255,176,32,.35), 0 6px 18px -8px rgba(255,176,32,.7);
}
.btn:hover{ transform:translateY(-1px); }
.btn:active{ transform:translateY(0); }
.btn.ghost{
  background:transparent;
  color:var(--text);
  border:1px solid var(--border);
  box-shadow:none;
}
.btn.ghost:hover{ border-color:var(--text-faint); }


.hero{
  position:relative;
  border:1px solid var(--border);
  border-radius:20px;
  background:linear-gradient(180deg,var(--panel-2),var(--panel));
  padding:34px 30px;
  display:grid;
  grid-template-columns:220px 1fr;
  gap:36px;
  align-items:center;
  overflow:hidden;
  margin-bottom:22px;
}

.hero::before{
  content:"";
  position:absolute;
  inset:0;
  background:
    repeating-linear-gradient(0deg, rgba(255,255,255,.025) 0 1px, transparent 1px 26px),
    repeating-linear-gradient(90deg, rgba(255,255,255,.025) 0 1px, transparent 1px 26px);
  mask-image:radial-gradient(ellipse 600px 300px at 20% 40%, black, transparent 75%);
  pointer-events:none;
}

.rotor-stage{
  position:relative;
  width:200px;height:200px;
  display:flex;align-items:center;justify-content:center;
}

.rotor-stage-sm{
  width:104px;height:104px;
}
.rotor-stage-sm #rotor-group{
  width:80px;height:80px;
}

.rotor-ring{
  position:absolute;
  inset:0;
  border-radius:50%;
  border:2px solid var(--border);
  box-shadow:inset 0 0 30px rgba(0,0,0,.5);
}

.rotor-ring::after{
  content:"";
  position:absolute; inset:10px;
  border-radius:50%;
  border:1px dashed #2a3444;
}

#rotor-group{
  width:150px;height:150px;
  animation:spin 4s linear infinite;
  animation-play-state:paused;
  transform-origin:50% 50%;
}

@keyframes spin{
  to{ transform:rotate(360deg); }
}

.rotor-hub{
  fill:#0d1219;
  stroke:var(--cyan);
  stroke-width:2;
}

.rotor-blade{
  fill:url(#bladeGrad);
  opacity:.92;
}

.hero-info{
  min-width:0;
}

.hero-eyebrow{
  color:var(--cyan);
  font-family:var(--mono);
  font-size:12px;
  margin-bottom:8px;
  display:flex;
  align-items:center;
  gap:8px;
}
.hero-eyebrow .line{
  width:22px;height:1px;background:var(--cyan);
  opacity:.5;
}

.hero-value{
  display:flex;
  align-items:baseline;
  gap:10px;
  flex-wrap:wrap;
}
.hero-value .num{
  font-family:var(--mono);
  font-size:clamp(46px,7vw,74px);
  font-weight:600;
  line-height:1;
  color:var(--text);
  letter-spacing:-1px;
  font-variant-numeric:tabular-nums;
}
.hero-value .unit{
  font-size:20px;
  color:var(--text-dim);
  font-family:var(--mono);
}

.hero-sub{
  margin-top:14px;
  color:var(--text-dim);
  font-size:14px;
  max-width:480px;
  line-height:1.5;
}

.hero-mini-stats{
  margin-top:20px;
  display:flex;
  gap:26px;
  flex-wrap:wrap;
}
.hero-mini-stats div{
  font-family:var(--mono);
}
.hero-mini-stats .l{
  font-size:11px;
  color:var(--text-faint);
  margin-bottom:3px;
}
.hero-mini-stats .v{
  font-size:16px;
  color:var(--text);
}


.grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(228px,1fr));
  gap:16px;
}

.card{
  border:1px solid var(--border);
  background:var(--panel);
  border-radius:var(--radius);
  padding:18px 18px 16px;
  min-height:210px;
  display:flex;
  flex-direction:column;
  position:relative;
}

.card-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  margin-bottom:6px;
}

.card-title{
  font-size:13px;
  color:var(--text-dim);
  font-weight:500;
}

.card-tag{
  font-family:var(--mono);
  font-size:10.5px;
  color:var(--text-faint);
  border:1px solid var(--border);
  padding:2px 6px;
  border-radius:5px;
}

.card-body{
  flex:1;
  display:flex;
  align-items:center;
  justify-content:center;
  position:relative;
}

.card-readout{
  text-align:center;
}
.card-readout .num{
  font-family:var(--mono);
  font-size:26px;
  font-weight:600;
  font-variant-numeric:tabular-nums;
}
.card-readout .unit{
  font-family:var(--mono);
  font-size:12px;
  color:var(--text-dim);
  margin-left:3px;
}

.gauge-wrap{ width:100%; display:flex; flex-direction:column; align-items:center; gap:6px; }
.gauge-svg{ width:150px; height:96px; }
.gauge-needle{ transition:transform .35s cubic-bezier(.4,1.4,.4,1); transform-origin:75px 78px; }
.gauge-svg-lg{ width:230px; height:148px; }
.gauge-stage{ width:200px; display:flex; align-items:center; justify-content:center; }

.pbar-wrap{ width:100%; }
.pbar-track{
  width:100%;height:14px;border-radius:8px;
  background:var(--track);
  overflow:hidden;
  border:1px solid var(--border);
}
.pbar-fill{
  height:100%;
  width:0%;
  border-radius:8px;
  background:linear-gradient(90deg,#a06600,var(--amber));
  box-shadow:0 0 12px -1px rgba(255,176,32,.7);
  transition:width .4s ease;
}
.pbar-label{
  display:flex;justify-content:space-between;
  margin-top:8px;
}

.odometer{
  display:flex;
  gap:3px;
  font-family:var(--mono);
}
.odo-digit{
  width:22px;height:34px;
  background:var(--track);
  border:1px solid var(--border);
  border-radius:5px;
  display:flex;align-items:center;justify-content:center;
  font-size:19px;
  font-weight:600;
  overflow:hidden;
  position:relative;
}
.odo-digit span{
  display:block;
  transition:transform .35s ease;
}
.odo-dot{
  align-self:flex-end;
  color:var(--text-faint);
  font-size:22px;
  padding:0 1px 4px;
}

.wave-card canvas{
  width:100%;
  height:86px;
  display:block;
}

.phase-svg{ width:130px;height:130px; }
.phase-needle{ transition:transform .35s ease; transform-origin:65px 65px; }

.thermo-wrap{
  display:flex;
  align-items:center;
  gap:16px;
}
.thermo-body{
  width:20px;
  height:110px;
  border-radius:10px;
  background:var(--track);
  border:1px solid var(--border);
  position:relative;
  overflow:hidden;
  display:flex;
  align-items:flex-end;
}
.thermo-fill{
  width:100%;
  height:10%;
  background:linear-gradient(180deg,var(--red),#ff9a3a);
  transition:height .4s ease, background .4s ease;
}
.thermo-bulb{
  width:34px;height:34px;
  border-radius:50%;
  background:var(--red);
  margin-top:-8px;
  box-shadow:0 0 14px -2px var(--red);
}

.ring-svg{ width:110px;height:110px; }
.ring-fg{
  transition:stroke-dashoffset .4s ease, stroke .4s ease;
  transform:rotate(-90deg);
  transform-origin:55px 55px;
}

.spectrum{
  display:flex;
  align-items:flex-end;
  gap:5px;
  height:80px;
}
.spectrum .bar{
  width:9px;
  border-radius:3px 3px 0 0;
  background:linear-gradient(180deg,var(--violet),#5a3ecb);
  transition:height .12s ease;
}

.spectrum.vib .bar{
  background:linear-gradient(180deg,var(--amber),#c2410c);
}

.card-footer{
  margin-top:10px;
  font-family:var(--mono);
  font-size:11px;
  color:var(--text-faint);
  text-align:center;
}


#analytics{ display:none; }

.analytics-head{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:18px;
  flex-wrap:wrap;
  gap:12px;
}
.analytics-head h2{
  margin:0;
  font-size:19px;
  font-weight:600;
}
.analytics-head p{
  margin:4px 0 0;
  color:var(--text-dim);
  font-size:13px;
}

.chart-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:16px;
}

.chart-card{
  border:1px solid var(--border);
  background:var(--panel);
  border-radius:var(--radius);
  padding:16px 16px 12px;
}
.chart-card-head{
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  margin-bottom:6px;
}
.chart-card-head .name{
  font-size:12.5px;
  color:var(--text-dim);
}
.chart-card-head .now{
  font-family:var(--mono);
  font-size:15px;
}
.chart-card canvas{
  width:100%;
  height:110px;
  display:block;
}
.chart-empty{
  color:var(--text-faint);
  font-size:12px;
  font-family:var(--mono);
  text-align:center;
  padding:36px 0;
}

@media (max-width:700px){
  .hero{ grid-template-columns:1fr; text-align:center; }
  .hero-mini-stats{ justify-content:center; }
  .rotor-stage{ margin:0 auto; }
  .thermo-wrap{ justify-content:center; }
}

</style>
</head>
<body>

<div class="wrap">

  <div class="topbar">
    <div class="brand">
      <div class="brand-mark">
        <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="#062521" stroke-width="2"/><path d="M12 3v4M12 17v4M3 12h4M17 12h4" stroke="#062521" stroke-width="2" stroke-linecap="round"/></svg>
      </div>
      <div class="brand-text">
        <h1>Induction Motor — Digital Twin</h1>
        <p>Arduino UNO Q · real-time monitoring</p>
      </div>
    </div>
    <div class="topbar-right">
      <div class="status-pill"><span class="status-dot" id="status-dot"></span><span id="status-text">connecting…</span></div>
      <button class="btn" id="view-toggle">View Analytics</button>
    </div>
  </div>

    <div id="home">

    <div class="hero">
      <div class="gauge-stage">
        <svg class="gauge-svg gauge-svg-lg" viewBox="0 0 150 90">
          <path d="M15 78 A60 60 0 0 1 135 78" fill="none" stroke="#1c2432" stroke-width="10" stroke-linecap="round"/>
          <path d="M15 78 A60 60 0 0 1 135 78" fill="none" stroke="#ffb020" stroke-width="10" stroke-linecap="round" stroke-dasharray="188.5" stroke-dashoffset="0" id="gauge-voltage-arc" opacity="0.9"/>
          <line class="gauge-needle" id="gauge-voltage-needle" x1="75" y1="78" x2="75" y2="26" stroke="#e9eef5" stroke-width="3.5" stroke-linecap="round"/>
          <circle cx="75" cy="78" r="6" fill="#e9eef5"/>
        </svg>
      </div>

      <div class="hero-info">
        <div class="hero-eyebrow"><span class="line"></span>SUPPLY VOLTAGE</div>
        <div class="hero-value">
          <span class="num" id="v-voltage">0.0</span>
          <span class="unit">V</span>
        </div>
        <div class="hero-sub">Live line voltage feeding the motor windings, read straight off the sensor.</div>
        <div class="hero-mini-stats">
          <div><div class="l">CURRENT</div><div class="v" id="mini-current">0.000 A</div></div>
          <div><div class="l">POWER</div><div class="v" id="mini-power">0.0 W</div></div>
          <div><div class="l">LAST UPDATE</div><div class="v" id="mini-time">—</div></div>
        </div>
      </div>
    </div>

    <div class="grid">

            <div class="card">
        <div class="card-head"><span class="card-title">Rotor Speed</span><span class="card-tag">0–3000 RPM</span></div>
        <div class="card-body">
          <div style="display:flex;flex-direction:column;align-items:center;gap:10px;">
            <div class="rotor-stage rotor-stage-sm">
              <div class="rotor-ring"></div>
              <svg id="rotor-group" viewBox="0 0 150 150">
                <defs>
                  <linearGradient id="bladeGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#38d9c9"/>
                    <stop offset="100%" stop-color="#1c6e66"/>
                  </linearGradient>
                </defs>
                <g id="blade-set">
                  <ellipse class="rotor-blade" cx="75" cy="30" rx="10" ry="26"/>
                  <ellipse class="rotor-blade" cx="75" cy="30" rx="10" ry="26" transform="rotate(60 75 75)"/>
                  <ellipse class="rotor-blade" cx="75" cy="30" rx="10" ry="26" transform="rotate(120 75 75)"/>
                  <ellipse class="rotor-blade" cx="75" cy="30" rx="10" ry="26" transform="rotate(180 75 75)"/>
                  <ellipse class="rotor-blade" cx="75" cy="30" rx="10" ry="26" transform="rotate(240 75 75)"/>
                  <ellipse class="rotor-blade" cx="75" cy="30" rx="10" ry="26" transform="rotate(300 75 75)"/>
                </g>
                <circle class="rotor-hub" cx="75" cy="75" r="16"/>
              </svg>
            </div>
            <div class="card-readout"><span class="num" id="v-rpm">0</span><span class="unit">RPM</span></div>
          </div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Current</span><span class="card-tag">0–20A</span></div>
        <div class="card-body">
          <div class="gauge-wrap">
            <svg class="gauge-svg" viewBox="0 0 150 90">
              <path d="M15 78 A60 60 0 0 1 135 78" fill="none" stroke="#1c2432" stroke-width="10" stroke-linecap="round"/>
              <path d="M15 78 A60 60 0 0 1 135 78" fill="none" stroke="#38d9c9" stroke-width="10" stroke-linecap="round" stroke-dasharray="188.5" id="gauge-current-arc" opacity="0.85"/>
              <line class="gauge-needle" id="gauge-current-needle" x1="75" y1="78" x2="75" y2="26" stroke="#e9eef5" stroke-width="3" stroke-linecap="round"/>
              <circle cx="75" cy="78" r="5" fill="#e9eef5"/>
            </svg>
            <div class="card-readout"><span class="num" id="v-current">0.000</span><span class="unit">A</span></div>
          </div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Power</span><span class="card-tag">0–3000W</span></div>
        <div class="card-body">
          <div class="pbar-wrap">
            <div class="card-readout" style="margin-bottom:14px;"><span class="num" id="v-power">0.0</span><span class="unit">W</span></div>
            <div class="pbar-track"><div class="pbar-fill" id="bar-power"></div></div>
          </div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Energy</span><span class="card-tag">kWh</span></div>
        <div class="card-body">
          <div style="display:flex;flex-direction:column;align-items:center;gap:10px;">
            <div class="odometer" id="odometer"></div>
            <div class="card-footer">cumulative consumption</div>
          </div>
        </div>
      </div>

            <div class="card wave-card">
        <div class="card-head"><span class="card-title">Frequency</span><span class="card-tag">Hz</span></div>
        <div class="card-body" style="flex-direction:column;">
          <canvas id="wave-frequency"></canvas>
          <div class="card-readout" style="margin-top:8px;"><span class="num" id="v-frequency">0.0</span><span class="unit">Hz</span></div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Power Factor</span><span class="card-tag">cos φ</span></div>
        <div class="card-body">
          <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
            <svg class="phase-svg" viewBox="0 0 130 130">
              <circle cx="65" cy="65" r="55" fill="none" stroke="#1c2432" stroke-width="1.5"/>
              <line x1="65" y1="65" x2="120" y2="65" stroke="#4b5566" stroke-width="2" stroke-dasharray="3 4"/>
              <line class="phase-needle" id="phase-needle" x1="65" y1="65" x2="120" y2="65" stroke="#4fd67a" stroke-width="3" stroke-linecap="round"/>
              <circle cx="65" cy="65" r="4" fill="#e9eef5"/>
            </svg>
            <div class="card-readout"><span class="num" id="v-pf">0.00</span></div>
          </div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Temperature</span><span class="card-tag">°C</span></div>
        <div class="card-body">
          <div class="thermo-wrap">
            <div class="thermo-body"><div class="thermo-fill" id="thermo-fill"></div></div>
            <div>
              <div class="thermo-bulb" id="thermo-bulb" style="margin-bottom:8px;"></div>
              <div class="card-readout"><span class="num" id="v-temperature">0.0</span><span class="unit">°C</span></div>
            </div>
          </div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Humidity Sensor</span><span class="card-tag">ADC</span></div>
        <div class="card-body">
          <div style="position:relative;display:flex;align-items:center;justify-content:center;">
            <svg class="ring-svg" viewBox="0 0 110 110">
              <circle cx="55" cy="55" r="46" fill="none" stroke="#1c2432" stroke-width="9"/>
              <circle class="ring-fg" id="ring-humidity" cx="55" cy="55" r="46" fill="none" stroke="#5b9dff" stroke-width="9" stroke-linecap="round" stroke-dasharray="289" stroke-dashoffset="289"/>
            </svg>
            <div class="card-readout" style="position:absolute;"><span class="num" id="v-humidity">0</span></div>
          </div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Noise Sensor</span><span class="card-tag">ADC</span></div>
        <div class="card-body">
          <div style="display:flex;flex-direction:column;align-items:center;gap:10px;">
            <div class="spectrum" id="spectrum"></div>
            <div class="card-readout"><span class="num" id="v-noise">0</span></div>
          </div>
        </div>
      </div>

            <div class="card">
        <div class="card-head"><span class="card-title">Vibration Sensor</span><span class="card-tag">ADC</span></div>
        <div class="card-body">
          <div style="display:flex;flex-direction:column;align-items:center;gap:10px;">
            <div class="spectrum vib" id="spectrum-vib"></div>
            <div class="card-readout"><span class="num" id="v-vibration">0</span></div>
          </div>
        </div>
      </div>

    </div>
  </div>

    <div id="analytics">
    <div class="analytics-head">
      <div>
        <h2>Analytics</h2>
        <p>History is recorded locally in this browser whenever a reading changes.</p>
      </div>
      <button class="btn ghost" id="clear-history">Clear history</button>
    </div>
    <div class="chart-grid" id="chart-grid"></div>
  </div>

</div>

<script>


const PARAMS = [
  { key:"voltage",     label:"Voltage",      unit:"V",   decimals:1, color:"#ffb020", min:0, max:300  },
  { key:"current",     label:"Current",      unit:"A",   decimals:3, color:"#38d9c9", min:0, max:20   },
  { key:"power",       label:"Power",        unit:"W",   decimals:1, color:"#ffb020", min:0, max:3000 },
  { key:"energy",      label:"Energy",       unit:"kWh", decimals:3, color:"#4fd67a", min:0, max:9999 },
  { key:"frequency",   label:"Frequency",    unit:"Hz",  decimals:2, color:"#5b9dff", min:0, max:70   },
  { key:"pf",          label:"Power Factor", unit:"",    decimals:2, color:"#4fd67a", min:0, max:1    },
  { key:"rpm",         label:"Rotor Speed",  unit:"RPM", decimals:0, color:"#38d9c9", min:0, max:3000 },
  { key:"temperature", label:"Temperature",  unit:"°C",  decimals:1, color:"#ff5d4a", min:0, max:120  },
  { key:"humidity",    label:"Humidity",     unit:"ADC", decimals:0, color:"#5b9dff", min:0, max:4095 },
  { key:"noise",       label:"Noise",        unit:"ADC", decimals:0, color:"#a48bff", min:0, max:4095 },
  { key:"vibration",   label:"Vibration",    unit:"ADC", decimals:0, color:"#ff8a3d", min:0, max:4095 }
];

const STORAGE_KEY = "motorTwinHistory";
const MAX_POINTS = 300;
const POLL_MS = 500;

let lastValues = {};
let history = loadHistory();

function loadHistory(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    if(raw) return JSON.parse(raw);
  }catch(e){ console.log("history load failed", e); }
  const h = {};
  PARAMS.forEach(p => h[p.key] = []);
  return h;
}

function saveHistory(){
  try{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  }catch(e){ console.log("history save failed", e); }
}


function poll(){
  fetch("/data")
    .then(r => r.json())
    .then(data => {
      if(data.error){ throw new Error(data.error); }

      let changed = false;
      const now = Date.now();

      PARAMS.forEach(p => {
        const v = data[p.key];
        if(lastValues[p.key] !== v){
          if(!history[p.key]) history[p.key] = [];
          history[p.key].push({ t: now, v: v });
          if(history[p.key].length > MAX_POINTS){
            history[p.key].splice(0, history[p.key].length - MAX_POINTS);
          }
          lastValues[p.key] = v;
          changed = true;
        }
      });

      if(changed) saveHistory();

      renderHome(data);
      setStatus(true);

      if(viewMode === "analytics") renderCharts();
    })
    .catch(err => {
      setStatus(false);
      console.log(err);
    });
}

function setStatus(ok){
  const dot = document.getElementById("status-dot");
  const text = document.getElementById("status-text");
  if(ok){
    dot.className = "status-dot live";
    text.textContent = "live";
  }else{
    dot.className = "status-dot err";
    text.textContent = "connection error";
  }
}


function fmt(v, d){ return Number(v).toFixed(d); }

function renderHome(data){

  document.getElementById("v-rpm").textContent = fmt(data.rpm, 0);
  updateRotor(data.rpm);
  document.getElementById("mini-time").textContent = new Date().toLocaleTimeString();

  document.getElementById("v-voltage").textContent = fmt(data.voltage,1);
  updateGauge("voltage", data.voltage, 0, 300);
  document.getElementById("mini-current").textContent = fmt(data.current,3) + " A";
  document.getElementById("mini-power").textContent = fmt(data.power,1) + " W";

  document.getElementById("v-current").textContent = fmt(data.current,3);
  updateGauge("current", data.current, 0, 20);

  document.getElementById("v-power").textContent = fmt(data.power,1);
  const pPct = Math.max(0, Math.min(100, (data.power/3000)*100));
  document.getElementById("bar-power").style.width = pPct + "%";

  updateOdometer(data.energy);

  document.getElementById("v-frequency").textContent = fmt(data.frequency,1);
  freqState.freq = data.frequency;

  document.getElementById("v-pf").textContent = fmt(data.pf,2);
  updatePhase(data.pf);

  document.getElementById("v-temperature").textContent = fmt(data.temperature,1);
  updateThermo(data.temperature);

  document.getElementById("v-humidity").textContent = data.humidity;
  updateRing(data.humidity, 4095);

  document.getElementById("v-noise").textContent = data.noise;
  noiseState.level = data.noise;

  document.getElementById("v-vibration").textContent = data.vibration;
  vibState.level = data.vibration;
}

const rotorEl = document.getElementById("rotor-group");
function updateRotor(rpm){
  const maxRpm = 3000;
  const clamped = Math.max(0, Math.min(rpm, maxRpm));
  const duration = clamped < 1 ? 6 : Math.max(0.25, 6 - (clamped/maxRpm)*5.75);
  rotorEl.style.animationDuration = duration + "s";
  rotorEl.style.animationPlayState = clamped > 1 ? "running" : "paused";
}

function updateGauge(name, value, min, max){
  const needle = document.getElementById("gauge-" + name + "-needle");
  const arc = document.getElementById("gauge-" + name + "-arc");
  const pct = Math.max(0, Math.min(1, (value-min)/(max-min)));
  const angle = -90 + pct*180;
  needle.setAttribute("transform", "rotate(" + angle + " 75 78)");
  const total = 188.5;
  arc.setAttribute("stroke-dashoffset", total - pct*total);
}

function updateOdometer(energy){
  const str = Number(energy).toFixed(3);
  const container = document.getElementById("odometer");
  const chars = str.split("");
  if(container.children.length !== chars.length){
    container.innerHTML = "";
    chars.forEach(() => {
      const d = document.createElement("div");
      d.className = "odo-digit";
      d.innerHTML = "<span></span>";
      container.appendChild(d);
    });
  }
  chars.forEach((ch, i) => {
    const el = container.children[i];
    if(ch === "."){
      el.className = "odo-digit odo-dot-cell";
      el.style.background = "transparent";
      el.style.border = "none";
      el.querySelector("span").textContent = ".";
      return;
    }
    const span = el.querySelector("span");
    if(span.textContent !== ch){
      span.style.transform = "translateY(-6px)";
      span.style.opacity = "0";
      setTimeout(() => {
        span.textContent = ch;
        span.style.transform = "translateY(6px)";
        requestAnimationFrame(() => {
          span.style.transform = "translateY(0)";
          span.style.opacity = "1";
        });
      }, 120);
    }
  });
}

function updatePhase(pf){
  const clamped = Math.max(0, Math.min(1, pf));
  const angleDeg = Math.acos(clamped) * (180/Math.PI);
  const needle = document.getElementById("phase-needle");
  needle.setAttribute("transform", "rotate(" + (-angleDeg) + " 65 65)");
}

function updateThermo(temp){
  const pct = Math.max(2, Math.min(100, (temp/120)*100));
  const fill = document.getElementById("thermo-fill");
  const bulb = document.getElementById("thermo-bulb");
  fill.style.height = pct + "%";
  let color = "#4fd67a";
  if(temp > 45 && temp <= 70) color = "#ffb020";
  if(temp > 70) color = "#ff5d4a";
  fill.style.background = "linear-gradient(180deg," + color + ",#ff9a3a)";
  bulb.style.background = color;
  bulb.style.boxShadow = "0 0 14px -2px " + color;
}

function updateRing(value, max){
  const pct = Math.max(0, Math.min(1, value/max));
  const circumference = 2 * Math.PI * 46;
  const ring = document.getElementById("ring-humidity");
  ring.setAttribute("stroke-dasharray", circumference);
  ring.setAttribute("stroke-dashoffset", circumference - pct*circumference);
}

const spectrumEl = document.getElementById("spectrum");
const vibSpectrumEl = document.getElementById("spectrum-vib");
const BAR_COUNT = 9;
function initSpectrum(el){
  for(let i=0;i<BAR_COUNT;i++){
    const b = document.createElement("div");
    b.className = "bar";
    b.style.height = "4px";
    el.appendChild(b);
  }
}
initSpectrum(spectrumEl);
initSpectrum(vibSpectrumEl);
const noiseState = { level: 0 };
const vibState = { level: 0 };
function drawSpectrum(el, state){
  const bars = el.children;
  const base = Math.max(0, Math.min(1, state.level/4095));
  for(let i=0;i<bars.length;i++){
    const jitter = Math.random()*0.7 + 0.3;
    const centerFactor = 1 - Math.abs(i - (BAR_COUNT-1)/2)/((BAR_COUNT-1)/2)*0.4;
    const h = Math.max(4, base*80*jitter*centerFactor);
    bars[i].style.height = h + "px";
  }
}
function animateSpectrum(){
  drawSpectrum(spectrumEl, noiseState);
  drawSpectrum(vibSpectrumEl, vibState);
  requestAnimationFrame(animateSpectrum);
}
requestAnimationFrame(animateSpectrum);

const freqCanvas = document.getElementById("wave-frequency");
const freqCtx = freqCanvas.getContext("2d");
const freqState = { freq: 0, phase: 0 };
function sizeCanvas(canvas){
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * devicePixelRatio;
  canvas.height = rect.height * devicePixelRatio;
}
function drawWave(){
  if(freqCanvas.width === 0) sizeCanvas(freqCanvas);
  const w = freqCanvas.width, h = freqCanvas.height;
  freqCtx.clearRect(0,0,w,h);
  freqCtx.beginPath();
  const amp = h*0.32;
  const cycles = Math.max(1, freqState.freq/6);
  for(let x=0; x<=w; x++){
    const y = h/2 + Math.sin((x/w)*Math.PI*2*cycles + freqState.phase) * amp;
    if(x===0) freqCtx.moveTo(x,y); else freqCtx.lineTo(x,y);
  }
  freqCtx.strokeStyle = "#5b9dff";
  freqCtx.lineWidth = 2*devicePixelRatio;
  freqCtx.stroke();
  freqState.phase += 0.12 + freqState.freq*0.01;
  requestAnimationFrame(drawWave);
}
requestAnimationFrame(drawWave);
window.addEventListener("resize", () => sizeCanvas(freqCanvas));


let viewMode = "home";
const homeEl = document.getElementById("home");
const analyticsEl = document.getElementById("analytics");
const toggleBtn = document.getElementById("view-toggle");
const chartGrid = document.getElementById("chart-grid");

PARAMS.forEach(p => {
  const card = document.createElement("div");
  card.className = "chart-card";
  card.innerHTML =
    '<div class="chart-card-head"><span class="name">' + p.label + '</span>' +
    '<span class="now" id="chart-now-' + p.key + '">—</span></div>' +
    '<canvas id="chart-canvas-' + p.key + '"></canvas>';
  chartGrid.appendChild(card);
});

toggleBtn.addEventListener("click", () => {
  if(viewMode === "home"){
    viewMode = "analytics";
    homeEl.style.display = "none";
    analyticsEl.style.display = "block";
    toggleBtn.textContent = "Back to Dashboard";
    renderCharts();
  }else{
    viewMode = "home";
    homeEl.style.display = "block";
    analyticsEl.style.display = "none";
    toggleBtn.textContent = "View Analytics";
  }
});

document.getElementById("clear-history").addEventListener("click", () => {
  history = {};
  PARAMS.forEach(p => history[p.key] = []);
  saveHistory();
  renderCharts();
});

function renderCharts(){
  PARAMS.forEach(p => {
    const points = history[p.key] || [];
    const canvas = document.getElementById("chart-canvas-" + p.key);
    const nowEl = document.getElementById("chart-now-" + p.key);

    if(points.length === 0){
      nowEl.textContent = "—";
      const ctx = canvas.getContext("2d");
      sizeCanvas(canvas);
      ctx.clearRect(0,0,canvas.width,canvas.height);
      return;
    }

    const last = points[points.length-1];
    nowEl.textContent = fmt(last.v, p.decimals) + (p.unit ? " " + p.unit : "");

    sizeCanvas(canvas);
    const ctx = canvas.getContext("2d");
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0,0,w,h);

    const values = points.map(pt => pt.v);
    let min = Math.min(...values), max = Math.max(...values);
    if(min === max){ min -= 1; max += 1; }
    const pad = (max-min)*0.1;
    min -= pad; max += pad;

    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    for(let i=1;i<3;i++){
      const y = (h/3)*i;
      ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke();
    }

    ctx.beginPath();
    points.forEach((pt, i) => {
      const x = (i/(points.length-1 || 1)) * w;
      const y = h - ((pt.v - min)/(max-min)) * h;
      if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    });
    ctx.strokeStyle = p.color;
    ctx.lineWidth = 2*devicePixelRatio;
    ctx.lineJoin = "round";
    ctx.stroke();

    ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
    ctx.fillStyle = p.color + "22";
    ctx.fill();
  });
}


poll();
setInterval(poll, POLL_MS);

</script>
</body>
</html>
"""

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(html.encode())

            return


        self.send_response(404)
        self.end_headers()



server = HTTPServer(("0.0.0.0", 8080), Handler)

print("======================================")
print("INDUCTION MOTOR WEB SERVER")
print("WEB SERVER STARTED ON PORT 8080")
print("======================================")


def loop():

    server.handle_request()


App.run(user_loop=loop)
