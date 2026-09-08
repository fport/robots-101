# Interactive lab

Try three concepts without installing Python. Calculations happen in your browser; there is no physics server or robot connection. **The two-link drawing below is a teaching model, not a SO-101 digital twin or MuJoCo simulation.**

## 1. Two joints, one endpoint

The first link is 18 cm and the second 14 cm. `q2` is relative to the first link. Set `q2=0`, then change `q1`: both links rotate together. Next hold q1 fixed and change q2.

<div class="lab-panel" id="kinematics-lab">
<svg viewBox="0 0 480 320" role="img" aria-label="Two-joint planar teaching arm">
<defs><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#344524" stroke-width="0.7"/></pattern></defs>
<rect width="480" height="320" fill="url(#grid)"/>
<path d="M30 245H455M240 295V20" stroke="#82966b" stroke-width="1" stroke-dasharray="4 5"/>
<text x="446" y="263" fill="#c1d2a7" font-size="13">x</text><text x="252" y="28" fill="#c1d2a7" font-size="13">y</text>
<polyline id="arm-links" points="240,245 310,160 330,80" stroke="#b6ff00" stroke-width="15" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
<circle cx="240" cy="245" r="12" fill="#edf4e4"/><circle id="elbow-dot" cx="310" cy="160" r="11" fill="#e0ff91"/><circle id="tip-dot" cx="330" cy="80" r="8" fill="#edf4e4"/>
<text x="15" y="307" fill="#c1d2a7" font-size="11">PLANAR FK · L₁ 18 cm · L₂ 14 cm · no physics or collisions</text>
</svg>
<div class="lab-controls">
<label for="joint-a">Shoulder angle q₁ (degrees)<input type="range" id="joint-a" min="-20" max="160" value="65"></label>
<label for="joint-b">Elbow angle q₂ (degrees)<input type="range" id="joint-b" min="-150" max="150" value="-55"></label>
</div>
<div class="lab-result" id="arm-result" aria-live="polite"></div>
</div>

**Experiment:** straighten the arm to reach 32 cm. Fold it to bring the tip toward the base. Consider different joint configurations reaching the same point; explain why inverse kinematics can have more than one solution. This drawing ignores self/table collisions.

## 2. How much data will you record?

Estimate raw storage and demonstration duration for 640×480 RGB images. Two cameras do not double the number of action rows: each time step has two images.

<div class="lab-panel" id="dataset-planner">
<div class="lab-controls">
<label for="episodes">Episode count<input type="number" id="episodes" min="1" value="50"></label>
<label for="seconds">Episode duration (s)<input type="number" id="seconds" min="1" value="20"></label>
<label for="fps">Recording FPS<input type="number" id="fps" min="1" value="30"></label>
<label for="cameras">Camera count<input type="number" id="cameras" min="1" value="2"></label>
</div>
<div class="lab-result" id="dataset-result" aria-live="polite"></div>
</div>

**Experiment:** 50 episodes × 20 seconds × 30 FPS gives 30,000 time steps. If resetting takes another 20 seconds per episode, total table time approximately doubles. Six hundred neighboring frames from one demonstration are not six hundred independent successful demonstrations.

## 3. Action sequences and latency

A VLA can predict several future actions per call. How many you execute affects when you need another observation and prediction.

<div class="lab-panel" id="chunk-lab">
<div class="lab-controls">
<label for="control-hz">Control frequency (Hz)<input type="range" id="control-hz" min="5" max="60" value="30"></label>
<label for="chunk-steps">Executed action count<input type="range" id="chunk-steps" min="1" max="50" value="10"></label>
<label for="latency-ms">Model latency (ms)<input type="range" id="latency-ms" min="10" max="1500" step="10" value="150"></label>
</div>
<div class="lab-result" id="chunk-result" aria-live="polite"></div>
</div>

**Experiment:** fifty commands at 30 Hz cover about 1.67 seconds. If the object slips during that interval, older predictions may still execute. A shorter horizon allows more frequent feedback but may empty the queue if inference cannot keep up. This calculator explains the time budget; it does not implement RTC or guarantee real-time control.

<noscript>Interactive calculations need JavaScript. You can still read the explanations and explore the same concepts in the Python examples.</noscript>
