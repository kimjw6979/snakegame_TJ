import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
import datetime

# 페이지 설정
st.set_page_config(page_title="은하철도 스피드 러시", page_icon="🚂", layout="wide")

# -------------------------------------------------------------
# 🚫 [상단 툴바 및 기본 메뉴 숨기기 CSS]
# -------------------------------------------------------------
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;} 
    header {visibility: hidden;}    
    footer {visibility: hidden;}    
    button[title="View fullscreen"] {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# -------------------------------------------------------------
# 🎮 [HTML/JS 최신 네온 트렌드 게임 엔진 - 스무스 보간 에디션]
# -------------------------------------------------------------
GAME_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        /* 은하철도 우주/네온 테마 */
        :root {
            --bg-color: #0f172a;
            --panel-bg: rgba(30, 41, 59, 0.7);
            --neon-green: #10b981;
            --neon-red: #f43f5e;
            --neon-blue: #3b82f6;
            --neon-gold: #fbbf24;
            --text-main: #f8fafc;
        }

        body { 
            display: flex; flex-direction: column; align-items: center; 
            background-color: var(--bg-color); color: var(--text-main); 
            font-family: 'Pretendard', 'Malgun Gothic', sans-serif; 
            margin: 0; padding: 10px; height: 1100px; overflow: hidden; 
            touch-action: manipulation;
            background-image: radial-gradient(circle at 50% 50%, #1e293b 0%, #050b14 100%);
        }
        
        .canvas-container { 
            position: relative; 
            width: 100%; 
            max-width: 600px; 
            aspect-ratio: 1 / 1; 
            margin-top: 10px;
        }
        
        canvas { 
            width: 100%; height: 100%; 
            background-color: #020617; 
            border-radius: 16px;
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.2), inset 0 0 20px rgba(0,0,0,0.8);
            border: 2px solid rgba(59, 130, 246, 0.3);
            box-sizing: border-box;
        }

        #blindOverlay { 
            position: absolute; top: 0; left: 0; 
            width: 100%; height: 100%; 
            background-color: rgba(2, 6, 23, 0.98); 
            display: none; pointer-events: none; 
            justify-content: center; align-items: center; 
            font-size: 5vw; font-weight: bold; color: #94a3b8; z-index: 10; 
            border-radius: 16px;
        }
        
        /* 글래스모피즘 UI 컨테이너 */
        .ui-container { 
            display: flex; gap: 15px; margin-bottom: 5px; align-items: center; 
            justify-content: center; flex-wrap: wrap;
            background: var(--panel-bg);
            padding: 12px 25px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .setup-container, .restart-container { 
            margin-bottom: 20px; display: flex; gap: 10px; justify-content: center;
        }
        
        input { 
            padding: 12px; font-size: 16px; border-radius: 12px; text-align: center; 
            border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); 
            color: white; max-width: 150px; outline: none; transition: 0.3s;
        }
        input:focus { border-color: var(--neon-gold); box-shadow: 0 0 10px var(--neon-gold); }

        button.start-btn { 
            padding: 12px 24px; font-size: 16px; font-weight: 800; 
            background: linear-gradient(135deg, #fbbf24, #d97706); 
            color: white; border: none; border-radius: 12px; cursor: pointer; 
            box-shadow: 0 4px 15px rgba(251, 191, 36, 0.4); transition: transform 0.1s, box-shadow 0.2s;
        }
        button.start-btn:active { transform: scale(0.95); }
        
        #scoreBoard { color: var(--neon-blue); text-shadow: 0 0 10px var(--neon-blue); }
        #livesBoard { color: var(--neon-red); text-shadow: 0 0 10px var(--neon-red); }
        #timerBoard { color: var(--neon-gold); text-shadow: 0 0 10px var(--neon-gold); }
        #scoreBoard, #livesBoard, #timerBoard { font-size: 18px; font-weight: 800; letter-spacing: 1px;}
        
        #itemEffect { 
            font-size: 16px; color: var(--neon-gold); height: 24px; margin-bottom: 5px; 
            font-weight: bold; text-align: center; text-shadow: 0 0 8px currentColor;
        }

        .info-text { font-size: 12px; color: #64748b; margin-top: 15px; text-align: center; letter-spacing: 1px;}

        /* 모바일 네온 컨트롤러 */
        .controls-wrapper {
            position: relative; display: flex; justify-content: center;
            width: 100%; max-width: 350px; margin-top: 25px;
        }
        .d-pad { display: flex; flex-direction: column; align-items: center; gap: 12px; }
        .d-pad-row { display: flex; gap: 12px; }
        
        .ctrl-btn {
            width: 70px; height: 70px; font-size: 28px; 
            border-radius: 18px; background: rgba(30, 41, 59, 0.8); color: rgba(255,255,255,0.8); 
            border: 1px solid rgba(255,255,255,0.1); 
            box-shadow: 0 8px 0 rgba(15, 23, 42, 0.9), inset 0 2px 2px rgba(255,255,255,0.1); 
            touch-action: none; cursor: pointer; user-select: none;
            display: flex; justify-content: center; align-items: center;
            transition: transform 0.1s, box-shadow 0.1s, background 0.2s;
            backdrop-filter: blur(5px);
        }
        .ctrl-btn:active { 
            background: rgba(251, 191, 36, 0.4); color: white; border-color: var(--neon-gold);
            transform: translateY(8px); box-shadow: 0 0 0 rgba(0,0,0,0); 
        }

        .pause-btn { 
            position: absolute; right: 0px; top: 0px;
            background: rgba(245, 158, 11, 0.8); box-shadow: 0 8px 0 #b45309; 
            font-size: 24px; border-radius: 50%; width: 60px; height: 60px; border:none;
        }
        .pause-btn:active { background: #d97706; transform: translateY(8px); box-shadow: 0 0 0 #b45309; }
    </style>
</head>
<body>
    <div class="setup-container" id="setupContainer">
        <input type="text" id="nicknameInput" placeholder="차장님 성함!" maxlength="10">
        <button id="startBtn" class="start-btn">🚂 은하철도 발차!</button>
    </div>

    <div class="restart-container" id="restartContainer" style="display: none;">
        <button id="restartBtn" class="start-btn" style="background: linear-gradient(135deg, #3b82f6, #2563eb);">🔄 재운행</button>
    </div>

    <div class="ui-container">
        <div id="scoreBoard">승객: <span id="currentScore">0</span>명</div>
        <div id="livesBoard">장갑: <span id="heartDisplay">❤️❤️❤️</span></div>
        <div id="timerBoard">🛤️선로 연결: <span id="foodTimerDisplay">10</span>s</div>
    </div>
    <div id="itemEffect"></div>
    
    <div class="canvas-container">
        <canvas id="gameCanvas" width="600" height="600"></canvas>
        <div id="blindOverlay">성운 진입 중... 👁️</div>
    </div>
    
    <div class="controls-wrapper">
        <div class="d-pad">
            <div class="d-pad-row top">
                <button id="btnUp" class="ctrl-btn">▲</button>
            </div>
            <div class="d-pad-row bottom">
                <button id="btnLeft" class="ctrl-btn">◀</button>
                <button id="btnDown" class="ctrl-btn">▼</button>
                <button id="btnRight" class="ctrl-btn">▶</button>
            </div>
        </div>
        <button id="btnPause" class="ctrl-btn pause-btn">⏸️</button>
    </div>
    
    <div class="info-text">[PC: 방향키/스페이스바/P] [Mobile: 화면 버튼 터치]</div>

    <script>
        function sendToStreamlit(type, data) {
            const msg = { isStreamlitMessage: true, type: type };
            if (data) Object.assign(msg, data);
            window.parent.postMessage(msg, "*");
        }

        function setHeight() { sendToStreamlit("streamlit:setFrameHeight", { height: 1100 }); }
        window.addEventListener("load", function() { sendToStreamlit("streamlit:componentReady", { apiVersion: 1 }); setHeight(); });
        window.addEventListener("message", function(event) { if (event.data && event.data.type === "streamlit:render") setHeight(); });

        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const gridSize = 20;
        
        let snake, normalFoods, hiddenFruits, particles = [];
        let dx, dy, score, nickname, lives;
        let isCountingDown = false, isGameOver = false, isStarted = false;
        let countdownText = ""; 
        
        let baseSpeed = 100;
        let speedMod = 1;
        let isReversedControls = false;
        let snakeSizeMod = 1; 
        
        let blindTimeout = null, controlTimeout = null, sizeTimeout = null;
        let hungerTimer = 10, hungerInterval = null;
        let changingDirection = false;

        let cloverSpawned = false, isGiantCloverActive = false;
        let giantCloverBlocks = [], cloverTimeout = null;
        let isPaused = false, pauseUsed = false;
        let nextBonusScore = 500, isBonusTime = false, bonusFoods = [], bonusTimeTimeout = null;
        let gridTriggered = false, isGridTime = false, gridTimeout = null;

        let lastRenderTime = 0;
        let accumulator = 0;
        let currentTickRate = 100;

        const COLOR_NEON_GREEN = "#10b981";
        const COLOR_NEON_RED = "#f43f5e";
        const COLOR_NEON_GOLD = "#fbbf24";
        const COLOR_NEON_BLUE = "#3b82f6";

        function initGame() {
            // 논리위치(x,y)와 스무스 렌더링용 이전위치(oldX, oldY) 설정
            snake = [{ x: 300, y: 300, oldX: 300, oldY: 300, lastAngle: -Math.PI / 2 }]; 
            dx = 0; dy = -gridSize;
            score = 0; lives = 3; isGameOver = false; particles = [];
            baseSpeed = 100; speedMod = 1; isReversedControls = false; snakeSizeMod = 1;
            changingDirection = false;
            countdownText = "";
            
            startHungerTimer();
            
            cloverSpawned = false; isGiantCloverActive = false; giantCloverBlocks = [];
            if (cloverTimeout) clearTimeout(cloverTimeout);
            
            isPaused = false; pauseUsed = false;
            
            nextBonusScore = 500; isBonusTime = false; bonusFoods = [];
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            
            gridTriggered = false; isGridTime = false;
            if(gridTimeout) clearTimeout(gridTimeout);
            
            document.getElementById("blindOverlay").style.display = "none";
            updateUI();
            
            normalFoods = [generateValidPosition()];
            hiddenFruits = [];
        }

        function updateUI() {
            document.getElementById("currentScore").innerText = score;
            document.getElementById("heartDisplay").innerText = "🛡️".repeat(lives);
            document.getElementById("foodTimerDisplay").innerText = hungerTimer;
            if (!isBonusTime && !isGridTime && !isGiantCloverActive) document.getElementById("itemEffect").innerText = "";
        }

        document.getElementById("startBtn").addEventListener("click", triggerStart);
        document.getElementById("restartBtn").addEventListener("click", triggerStart);

        function triggerStart() {
            const inputVal = document.getElementById("nicknameInput").value.trim();
            if (document.getElementById("setupContainer").style.display !== "none") {
                if (!inputVal) { alert("⚠️ 발차를 위해 차장님(유저) 성함을 입력해주세요!"); return; }
                nickname = inputVal;
            }
            document.getElementById("setupContainer").style.display = "none";
            document.getElementById("restartContainer").style.display = "none";
            isStarted = true;
            startGameSequence();
        }

        function startGameSequence() { 
            initGame(); 
            isCountingDown = true;
            lastRenderTime = performance.now();
            accumulator = 0;
            requestAnimationFrame(gameLoop); // 즉시 렌더링 루프 시작!
            
            let count = 3; 
            let countInterval = setInterval(() => {
                countdownText = count > 0 ? count.toString() : "발차!";
                count--;
                if (count < -1) {
                    clearInterval(countInterval); 
                    isCountingDown = false;
                    countdownText = "";
                    lastRenderTime = performance.now();
                    accumulator = 0;
                }
            }, 800);
        }

        function resumeHungerTimer() {
            if (hungerInterval) clearInterval(hungerInterval);
            hungerInterval = setInterval(() => {
                if (isGameOver || isCountingDown || !isStarted || isPaused) return;
                hungerTimer--;
                document.getElementById("foodTimerDisplay").innerText = hungerTimer;
                
                if (hungerTimer <= 0) {
                    // 타이머 종료 시 객차 4칸 연장 페널티
                    for(let i=0; i<4; i++) {
                        let tail = snake[snake.length-1];
                        // 스무스 이동을 위해 oldX, oldY 도 복사
                        snake.push({x: tail.x, y: tail.y, oldX: tail.x, oldY: tail.y, lastAngle: tail.lastAngle});
                    }
                    
                    const effectDisplay = document.getElementById("itemEffect");
                    effectDisplay.innerText = "⚠️ 선로 이탈 경고! 강제 궤도 수정으로 객차 4량 추가!"; 
                    effectDisplay.style.color = COLOR_NEON_RED; 
                    setTimeout(() => { if(effectDisplay.innerText.includes("이탈") && !isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 2500);
                    
                    hungerTimer = 10;
                    document.getElementById("foodTimerDisplay").innerText = hungerTimer;
                }
            }, 1000);
        }

        function startHungerTimer() { hungerTimer = 10; document.getElementById("foodTimerDisplay").innerText = hungerTimer; resumeHungerTimer(); }
        function resetHungerTimer() { hungerTimer = 10; document.getElementById("foodTimerDisplay").innerText = hungerTimer; }

        function updateSpeed() {
            baseSpeed = Math.max(40, 100 - (score / 50) * 0.5);
            currentTickRate = baseSpeed * speedMod;
        }

        function updateGameDifficulty() {
            document.getElementById("currentScore").innerText = score;
            updateSpeed();
            
            let targetFoodCount = Math.min(5, 1 + Math.floor(score / 100));
            while(normalFoods.length < targetFoodCount) { normalFoods.push(generateValidPosition()); }
            if (normalFoods.length === 0) normalFoods.push(generateValidPosition());
        }

        function gameLoop(currentTime) {
            if (!isStarted || isGameOver) return;

            let deltaTime = currentTime - lastRenderTime;
            if (deltaTime > 200) deltaTime = 200; 
            lastRenderTime = currentTime;

            if (!isPaused && !isCountingDown) {
                accumulator += deltaTime;
                while (accumulator >= currentTickRate) {
                    logicTick(); 
                    accumulator -= currentTickRate;
                }
            }
            
            renderFrame(); 
            requestAnimationFrame(gameLoop);
        }

        function clearCanvas() { ctx.clearRect(0, 0, canvas.width, canvas.height); }

        function drawGrid() {
            ctx.strokeStyle = "rgba(59, 130, 246, 0.15)"; ctx.lineWidth = 1;
            for(let x = 0; x <= canvas.width; x += gridSize) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
            for(let y = 0; y <= canvas.height; y += gridSize) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); }
        }

        function logicTick() {
            changingDirection = false; 
            if (checkCollision()) { handleDeath(); return; }
            advanceSnake(); 
        }

        function renderFrame(skipClear = false) {
            if(!skipClear) clearCanvas();
            
            // 우주 배경의 작은 별들
            ctx.fillStyle = "rgba(255, 255, 255, 0.3)";
            ctx.fillRect(100, 150, 2, 2); ctx.fillRect(400, 50, 2, 2); ctx.fillRect(500, 450, 2, 2); ctx.fillRect(200, 500, 2, 2);

            if (isGridTime) drawGrid();
            
            if (isBonusTime) {
                ctx.fillStyle = "rgba(251, 191, 36, 0.05)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.font = "bold 80px 'Pretendard'"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
                ctx.fillStyle = "rgba(251, 191, 36, 0.15)";
                ctx.fillText("MILKY WAY!", canvas.width / 2, canvas.height / 2);
            }
            
            drawGiantClover(); 
            drawNormalFoods(); 
            drawHiddenFruits(); 
            drawBonusFoods(); 
            
            // 스무스 LERP 값 계산
            let lerp = (isCountingDown || isPaused) ? 1.0 : Math.min(1.0, accumulator / currentTickRate);
            
            drawTrainPath(lerp); 
            updateAndDrawParticles(); 
            
            // 카운트다운/일시정지 문구 렌더링
            if (countdownText) {
                ctx.fillStyle = "rgba(2, 6, 23, 0.6)"; 
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                let isPause = countdownText.includes("일시정지");
                ctx.fillStyle = COLOR_NEON_GOLD; 
                ctx.font = isPause ? "bold 50px 'Pretendard'" : "bold 60px 'Pretendard'";
                ctx.textAlign = "center"; 
                ctx.textBaseline = "middle";
                ctx.shadowBlur = 20; 
                ctx.shadowColor = COLOR_NEON_GOLD;
                ctx.fillText(countdownText, canvas.width / 2, canvas.height / 2 - (isPause ? 20 : 0));
                
                if (isPause) {
                    ctx.fillStyle = "#94a3b8"; 
                    ctx.font = "20px 'Pretendard'";
                    ctx.shadowBlur = 0;
                    ctx.fillText("(운행당 1번만 사용 가능!)", canvas.width / 2, canvas.height / 2 + 30);
                }
                ctx.shadowBlur = 0;
            }
        }

        function createParticles(x, y, color) {
            for(let i=0; i<12; i++) {
                particles.push({
                    x: x + gridSize/2, y: y + gridSize/2,
                    vx: (Math.random() - 0.5) * 8, vy: (Math.random() - 0.5) * 8,
                    life: 1.0, color: color
                });
            }
        }
        
        function updateAndDrawParticles() {
            for(let i = particles.length -1; i >= 0; i--) {
                let p = particles[i];
                if(!isPaused && !isCountingDown) { p.x += p.vx; p.y += p.vy; p.life -= 0.05; }
                if(p.life <= 0) { particles.splice(i, 1); continue; }
                ctx.globalAlpha = p.life;
                ctx.fillStyle = p.color;
                ctx.shadowBlur = 10; ctx.shadowColor = p.color;
                ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI*2); ctx.fill();
                ctx.shadowBlur = 0; ctx.globalAlpha = 1.0;
            }
        }

        // --- 🚂 은하철도 999 스무스 렌더링 ---
        function drawTrainPath(lerp) {
            if (snake.length === 0) return;
            
            let strokeColor = isReversedControls ? COLOR_NEON_RED : COLOR_NEON_BLUE;
            let w = Math.max(4, (gridSize - 4) * snakeSizeMod);

            // 보간된 시각적 좌표 생성
            let vSnake = snake.map(part => {
                return {
                    x: part.oldX !== undefined ? part.oldX + (part.x - part.oldX) * lerp : part.x,
                    y: part.oldY !== undefined ? part.oldY + (part.y - part.oldY) * lerp : part.y,
                    origPart: part
                };
            });

            // 1. 객차(꼬리) 그리기
            for (let i = vSnake.length - 1; i >= 1; i--) {
                let part = vSnake[i];
                let prev = vSnake[i-1];
                
                ctx.save();
                ctx.translate(part.x + gridSize/2, part.y + gridSize/2);
                
                let dY = prev.y - part.y;
                let dX = prev.x - part.x;
                let angle = part.origPart.lastAngle || 0;
                // 완전히 겹쳐있지 않으면 각도 업데이트
                if (Math.abs(dX) > 0.01 || Math.abs(dY) > 0.01) {
                    angle = Math.atan2(dY, dX);
                    part.origPart.lastAngle = angle; 
                }
                ctx.rotate(angle);
                
                // 연결고리
                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(w*0.5, 0); ctx.lineTo(w*1.0, 0);
                ctx.stroke();

                // 객차 본체
                ctx.fillStyle = "#1e293b";
                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = 1.5;
                ctx.shadowBlur = 5;
                ctx.shadowColor = strokeColor;
                
                ctx.beginPath();
                ctx.rect(-w*0.4, -w*0.35, w*0.9, w*0.7);
                ctx.fill(); ctx.stroke();
                
                // 창문 불빛
                ctx.fillStyle = COLOR_NEON_GOLD;
                ctx.shadowBlur = 8;
                ctx.shadowColor = COLOR_NEON_GOLD;
                ctx.fillRect(-w*0.2, -w*0.15, w*0.2, w*0.3);
                ctx.fillRect(w*0.1, -w*0.15, w*0.2, w*0.3);

                ctx.restore();
            }
            
            // 2. 증기기관차 (머리) 그리기
            let headX = vSnake[0].x + gridSize/2;
            let headY = vSnake[0].y + gridSize/2;

            ctx.save();
            ctx.translate(headX, headY);

            // 헤드의 각도는 사용자 조작에 즉시 반응
            let headAngle = 0;
            if (dx > 0) headAngle = 0;                  // 오른쪽
            else if (dx < 0) headAngle = Math.PI;       // 왼쪽
            else if (dy > 0) headAngle = Math.PI / 2;   // 아래
            else if (dy < 0) headAngle = -Math.PI / 2;  // 위
            ctx.rotate(headAngle);

            ctx.fillStyle = "#0f172a";
            ctx.strokeStyle = COLOR_NEON_GOLD;
            ctx.lineWidth = 2;
            ctx.shadowBlur = 10;
            ctx.shadowColor = COLOR_NEON_GOLD;

            ctx.beginPath();
            ctx.rect(-w*0.4, -w*0.35, w*1.0, w*0.7);
            ctx.fill(); ctx.stroke();

            ctx.beginPath();
            ctx.rect(-w*0.6, -w*0.45, w*0.4, w*0.9);
            ctx.fill(); ctx.stroke();
            
            ctx.fillStyle = COLOR_NEON_BLUE;
            ctx.shadowBlur = 5;
            ctx.shadowColor = COLOR_NEON_BLUE;
            ctx.fillRect(-w*0.45, -w*0.25, w*0.15, w*0.5);

            ctx.fillStyle = "#1e293b";
            ctx.strokeStyle = COLOR_NEON_GOLD;
            ctx.beginPath();
            ctx.rect(w*0.2, -w*0.55, w*0.25, w*0.2);
            ctx.fill(); ctx.stroke();

            ctx.fillStyle = "#334155";
            ctx.shadowBlur = 0;
            ctx.beginPath();
            ctx.moveTo(w*0.6, -w*0.3);
            ctx.lineTo(w*0.9, 0);
            ctx.lineTo(w*0.6, w*0.3);
            ctx.closePath();
            ctx.fill(); ctx.stroke();

            ctx.fillStyle = "#ffffff";
            ctx.shadowBlur = 15;
            ctx.shadowColor = COLOR_NEON_GOLD;
            ctx.beginPath();
            ctx.arc(w*0.6, 0, w*0.15, 0, Math.PI*2);
            ctx.fill();

            ctx.globalAlpha = 0.25;
            ctx.fillStyle = COLOR_NEON_GOLD;
            ctx.beginPath();
            ctx.moveTo(w*0.7, 0);
            ctx.lineTo(w*3.5, -w*1.5);
            ctx.lineTo(w*3.5, w*1.5);
            ctx.fill();
            ctx.globalAlpha = 1.0;

            // 스무스 좌표계에서 파티클(연기) 생성
            if (!isPaused && !isCountingDown && !isGameOver && Math.random() < 0.3) {
                particles.push({
                    x: headX, 
                    y: headY,
                    vx: -dx * 0.1 + (Math.random()-0.5)*1.5,
                    vy: -dy * 0.1 + (Math.random()-0.5)*1.5,
                    life: 1.0, 
                    color: "rgba(200, 210, 220, 0.6)"
                });
            }

            ctx.restore(); 
        }

        // --- 🛤️ 선로(기찻길) 렌더링 ---
        function drawNormalFoods() { 
            ctx.strokeStyle = "rgba(255, 255, 255, 0.9)"; // 밝은 빛깔
            ctx.lineWidth = 1.5;
            ctx.shadowBlur = 10;
            ctx.shadowColor = COLOR_NEON_BLUE; // 푸른 네온 궤도 빛
            
            normalFoods.forEach(food => {
                let fx = food.x;
                let fy = food.y;
                
                ctx.beginPath();
                ctx.moveTo(fx + 6, fy + 3); ctx.lineTo(fx + 6, fy + 17);
                ctx.moveTo(fx + 14, fy + 3); ctx.lineTo(fx + 14, fy + 17);
                ctx.moveTo(fx + 4, fy + 6); ctx.lineTo(fx + 16, fy + 6);
                ctx.moveTo(fx + 4, fy + 10); ctx.lineTo(fx + 16, fy + 10);
                ctx.moveTo(fx + 4, fy + 14); ctx.lineTo(fx + 16, fy + 14);
                ctx.stroke();
            });
            ctx.shadowBlur = 0;
        }
        
        // --- 🎁 눈에 확 띄는 밝은 네온 물음표 상자 렌더링 ---
        function drawHiddenFruits() {
            hiddenFruits.forEach(fruit => {
                let fx = fruit.x;
                let fy = fruit.y;
                
                let time = performance.now() / 200; 
                let glow = 15 + Math.sin(time) * 5;
                
                ctx.shadowBlur = glow;
                ctx.shadowColor = "#f472b6"; 
                ctx.fillStyle = "rgba(244, 114, 182, 0.4)";
                ctx.strokeStyle = "#fbcfe8"; 
                ctx.lineWidth = 2;
                
                ctx.beginPath();
                ctx.rect(fx + 2, fy + 2, gridSize - 4, gridSize - 4);
                ctx.fill();
                ctx.stroke();
                
                ctx.shadowBlur = 0; 
                ctx.fillStyle = "#ffffff"; 
                ctx.font = "bold 14px Arial";
                ctx.textAlign = "center"; 
                ctx.textBaseline = "middle";
                ctx.fillText("?", fx + gridSize/2, fy + gridSize/2 + 1);
            });
        }

        function drawGiantClover() {
            if (isGiantCloverActive) {
                ctx.save();
                ctx.beginPath(); ctx.rect(200, 200, 200, 200); ctx.clip();
                ctx.font = "180px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
                ctx.fillText("🌌", 300, 310); 
                ctx.restore(); 
                
                ctx.fillStyle = "#020617";
                for (let r = 0; r < 10; r++) {
                    for (let c = 0; c < 10; c++) {
                        let bx = 200 + c * gridSize; let by = 200 + r * gridSize;
                        let isEaten = !giantCloverBlocks.some(b => b.x === bx && b.y === by);
                        if (isEaten) ctx.fillRect(bx, by, gridSize, gridSize);
                    }
                }
            }
        }
        
        function drawBonusFoods() {
            if (!isBonusTime) return;
            ctx.font = "20px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.shadowBlur = 15;
            ctx.shadowColor = COLOR_NEON_GOLD;
            bonusFoods.forEach(food => { 
                ctx.fillText("⭐️", food.x + (gridSize / 2), food.y + (gridSize / 2) + 2); 
            });
            ctx.shadowBlur = 0;
        }
        
        function advanceSnake() { 
            // 이동 전 현재 위치를 oldX, oldY에 저장
            snake.forEach(part => {
                part.oldX = part.x;
                part.oldY = part.y;
            });

            let head = { 
                x: snake[0].x + dx, 
                y: snake[0].y + dy, 
                oldX: snake[0].x, 
                oldY: snake[0].y, 
                lastAngle: snake[0].lastAngle 
            }; 
            snake.unshift(head); 
            
            let hitRange = (snakeSizeMod > 1.2) ? gridSize : 0;
            let ateSomething = false;

            if (score >= 250 && !gridTriggered) {
                gridTriggered = true; isGridTime = true;
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🌐 항법 컴퓨터 가동! 우주 궤도 10초간 표시!";
                effectDisplay.style.color = COLOR_NEON_BLUE;
                gridTimeout = setTimeout(() => { isGridTime = false; if (!isGameOver && !isPaused && !isBonusTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 10000); 
            }

            if (snake.length >= 30 && !cloverSpawned) {
                cloverSpawned = true; isGiantCloverActive = true; giantCloverBlocks = [];
                for (let r = 0; r < 10; r++) { for (let c = 0; c < 10; c++) { giantCloverBlocks.push({ x: 200 + c * gridSize, y: 200 + r * gridSize }); } }
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🌌 안드로메다 정거장 출현! 중앙으로 집결!"; 
                effectDisplay.style.color = COLOR_NEON_GREEN;
                cloverTimeout = setTimeout(() => {
                    isGiantCloverActive = false; giantCloverBlocks = [];
                    if (!isGameOver && !isPaused && !isGridTime && !isBonusTime) effectDisplay.innerText = "";
                }, 5000); 
            }

            if (isGiantCloverActive) {
                for (let i = giantCloverBlocks.length - 1; i >= 0; i--) {
                    let f = giantCloverBlocks[i];
                    if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                        score += 10; giantCloverBlocks.splice(i, 1); updateGameDifficulty(); resetHungerTimer(); ateSomething = true;
                        createParticles(f.x, f.y, COLOR_NEON_GREEN);
                    }
                }
            }

            if (isBonusTime) {
                for (let i = bonusFoods.length - 1; i >= 0; i--) {
                    let f = bonusFoods[i];
                    if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                        score += 10; bonusFoods.splice(i, 1); updateGameDifficulty(); resetHungerTimer(); ateSomething = true;
                        createParticles(f.x, f.y, COLOR_NEON_GOLD);
                    }
                }
            }

            for (let i = normalFoods.length - 1; i >= 0; i--) {
                let f = normalFoods[i];
                if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                    score += 10; normalFoods.splice(i, 1); updateGameDifficulty(); resetHungerTimer();
                    if (hiddenFruits.length < 3 && Math.random() < 0.4) spawnHiddenFruit();
                    ateSomething = true;
                    createParticles(f.x, f.y, COLOR_NEON_BLUE);
                }
            }
            
            for (let i = hiddenFruits.length - 1; i >= 0; i--) {
                let f = hiddenFruits[i];
                if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                    let fruit = hiddenFruits.splice(i, 1)[0]; applyHiddenFruitEffect(fruit.type); resetHungerTimer(); ateSomething = true;
                    createParticles(f.x, f.y, "#9b59b6");
                }
            }

            if (!ateSomething) { snake.pop(); }
            
            if (score >= nextBonusScore && !isBonusTime) {
                let spawnCount = 40; 
                if (nextBonusScore === 1000) spawnCount = 50; else if (nextBonusScore === 1500) spawnCount = 60; else if (nextBonusScore >= 2000) spawnCount = 80;
                nextBonusScore = Math.floor(score / 500) * 500 + 500; 
                isBonusTime = true; bonusFoods = [];
                for (let i = 0; i < spawnCount; i++) { bonusFoods.push(generateValidPosition()); }
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = `🎉 유성우 접근! 별 조각 ${spawnCount}개 드랍!`; effectDisplay.style.color = COLOR_NEON_GOLD;
                bonusTimeTimeout = setTimeout(() => {
                    isBonusTime = false; bonusFoods = [];
                    if (!isGameOver && !isPaused && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = "";
                }, 10000); 
            }
        }

        function applyHiddenFruitEffect(type) {
            const effectDisplay = document.getElementById("itemEffect");
            if (type === 'blind') {
                effectDisplay.innerText = "⚠️ 암흑 성운 진입! 3초간 시야 차단!"; effectDisplay.style.color = "#94a3b8";
                document.getElementById("blindOverlay").style.display = "flex";
                if(blindTimeout) clearTimeout(blindTimeout);
                blindTimeout = setTimeout(() => { document.getElementById("blindOverlay").style.display = "none"; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 3000);
            } else if (type === 'tunnel') {
                effectDisplay.innerText = "🌀 블랙홀 진입! 기수 반전!"; effectDisplay.style.color = "#c084fc";
                if (snake.length > 1) { const tail = snake[snake.length - 1]; const beforeTail = snake[snake.length - 2]; dx = tail.x - beforeTail.x; dy = tail.y - beforeTail.y; snake.reverse(); } else { dx = -dx; dy = -dy; }
            } else if (type === 'reverse') {
                effectDisplay.innerText = "☣️ 중력 이상! 3초간 조작 반전!"; effectDisplay.style.color = COLOR_NEON_RED;
                isReversedControls = true;
                if(controlTimeout) clearTimeout(controlTimeout);
                controlTimeout = setTimeout(() => { isReversedControls = false; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 3000);
            } else if (type === 'caterpillar') {
                if (Math.random() < 0.5) { effectDisplay.innerText = "💪 전방위 실드! 주변 선로 싹쓸이 (5초)"; effectDisplay.style.color = COLOR_NEON_BLUE; snakeSizeMod = 1.8; } 
                else { effectDisplay.innerText = "📉 초공간 도약! 기차가 작아집니다!"; effectDisplay.style.color = COLOR_NEON_GOLD; snakeSizeMod = 0.5; }
                if(sizeTimeout) clearTimeout(sizeTimeout);
                sizeTimeout = setTimeout(() => { snakeSizeMod = 1; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'bonus') {
                score += 50; effectDisplay.innerText = "💎 우주 광석 획득 +50명!"; effectDisplay.style.color = COLOR_NEON_GOLD;
            } else if (type === 'slow') {
                effectDisplay.innerText = "🐢 우주 기류 탑승! 속도 저하 (5초)"; effectDisplay.style.color = COLOR_NEON_BLUE;
                speedMod = 1.6; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'fast') {
                effectDisplay.innerText = "⚡ 하이퍼 드라이브! 속도 급상승 (5초)"; effectDisplay.style.color = "#c084fc";
                speedMod = 0.5; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'penalty') {
                score = Math.max(0, score - 30); effectDisplay.innerText = "💀 우주 해적 조우! 승객 -30명!"; effectDisplay.style.color = COLOR_NEON_RED;
            } else if (type === 'super') {
                score += 100; effectDisplay.innerText = "🚀 메텔의 가호! 슈퍼 보너스 +100명!"; effectDisplay.style.color = COLOR_NEON_GREEN;
            }
            updateGameDifficulty(); 
            setTimeout(() => { if(!['slow','fast','blind','reverse','caterpillar'].includes(type) && !isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 2500);
        }

        function spawnHiddenFruit() {
            let pos = generateValidPosition();
            let fruit = { x: pos.x, y: pos.y, type: '', id: Date.now() };
            const rand = Math.random();
            if (rand < 0.12) fruit.type = 'blind'; else if (rand < 0.24) fruit.type = 'tunnel'; else if (rand < 0.36) fruit.type = 'reverse'; else if (rand < 0.48) fruit.type = 'caterpillar'; else if (rand < 0.60) fruit.type = 'bonus'; else if (rand < 0.70) fruit.type = 'slow'; else if (rand < 0.80) fruit.type = 'fast'; else if (rand < 0.90) fruit.type = 'penalty'; else fruit.type = 'super';
            hiddenFruits.push(fruit);
            setTimeout(() => { hiddenFruits = hiddenFruits.filter(f => f.id !== fruit.id); }, 8000);
        }
        
        function generateValidPosition() {
            let newPos;
            while (true) {
                newPos = { x: Math.floor(Math.random() * (canvas.width/gridSize)) * gridSize, y: Math.floor(Math.random() * (canvas.height/gridSize)) * gridSize };
                if (!snake.some(part => part.x === newPos.x && part.y === newPos.y)) break;
            } return newPos;
        }
        
        function checkCollision() { 
            const head = { x: snake[0].x + dx, y: snake[0].y + dy };
            if (head.x < 0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height) return true; 
            for (let i = 0; i < snake.length - 1; i++) { if (snake[i].x === head.x && snake[i].y === head.y) return true; } 
            return false; 
        }

        // [버그수정] 리스폰 중 발생하던 로직 충돌 및 카운트다운 개선
        function handleDeath() {
            lives--;
            if (lives > 0) {
                reduceSnakeBody(3);
                isCountingDown = true; 
                if(hungerInterval) clearInterval(hungerInterval);
                
                countdownText = "💥 장갑 손상! 비상 복구중...";
                
                setTimeout(() => {
                    resetSnakePosition(); // 꼬이지 않게 일자로 재배치
                    let count = 3;
                    let countInterval = setInterval(() => {
                        countdownText = count > 0 ? count.toString() : "재발차!";
                        count--;
                        if (count < -1) {
                            clearInterval(countInterval); 
                            isCountingDown = false;
                            countdownText = "";
                            lastRenderTime = performance.now();
                            accumulator = 0;
                            startHungerTimer();
                        }
                    }, 800);
                }, 1500);
            } else {
                updateUI(); endGame();
            }
        }

        function reduceSnakeBody(count) {
            if (snake.length > count) { snake = snake.slice(0, snake.length - count); } else { snake = [snake[0]]; }
        }

        // [버그수정] 자기 꼬리를 다시 물지 않도록 일자로 세팅
        function resetSnakePosition() {
            document.getElementById("blindOverlay").style.display = "none";
            isReversedControls = false; snakeSizeMod = 1;
            if(sizeTimeout) clearTimeout(sizeTimeout);
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            isBonusTime = false; bonusFoods = [];
            if(gridTimeout) clearTimeout(gridTimeout);
            isGridTime = false;
            isGiantCloverActive = false; giantCloverBlocks = [];
            if(cloverTimeout) clearTimeout(cloverTimeout);
            
            let len = snake.length;
            snake = [];
            // 중앙부터 아래로 일자로 배치시켜 부활 시 자폭 방지
            for(let i=0; i<len; i++) {
                snake.push({
                    x: 300, 
                    y: 300 + i*gridSize, 
                    oldX: 300, 
                    oldY: 300 + i*gridSize,
                    lastAngle: -Math.PI / 2
                });
            }
            dx = 0; dy = -gridSize;
            
            updateUI();
        }

        function endGame() {
            if(hungerInterval) clearInterval(hungerInterval); 
            if(cloverTimeout) clearTimeout(cloverTimeout);
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            if(gridTimeout) clearTimeout(gridTimeout);
            
            isGameOver = true; isStarted = false;
            countdownText = "";
            
            document.getElementById("blindOverlay").style.display = "none";
            document.getElementById("restartContainer").style.display = "flex";
            
            renderFrame(false); 
            ctx.fillStyle = "rgba(2, 6, 23, 0.8)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = COLOR_NEON_RED; ctx.font = "bold 50px 'Pretendard'";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.shadowBlur = 15; ctx.shadowColor = COLOR_NEON_RED;
            ctx.fillText("운행 종료 (GAME OVER)", canvas.width / 2, canvas.height / 2 - 20);
            ctx.fillStyle = "white"; ctx.font = "24px 'Pretendard'"; ctx.shadowBlur = 0;
            ctx.fillText(`탑승 승객 : ${score}명`, canvas.width / 2, canvas.height / 2 + 30);
            
            sendToStreamlit("streamlit:setComponentValue", { value: { nickname: nickname, score: score, timestamp: Date.now() } });
        }

        function setDirection(keyCode) {
            if (isCountingDown || isGameOver || isPaused) return;
            if (changingDirection) return;

            let LEFT = 37, UP = 38, RIGHT = 39, DOWN = 40;
            if (isReversedControls) { LEFT = 39; RIGHT = 37; UP = 40; DOWN = 38; }
            
            if (keyCode === LEFT && dx === 0) { dx = -gridSize; dy = 0; changingDirection = true; }
            if (keyCode === UP && dy === 0) { dx = 0; dy = -gridSize; changingDirection = true; }
            if (keyCode === RIGHT && dx === 0) { dx = gridSize; dy = 0; changingDirection = true; }
            if (keyCode === DOWN && dy === 0) { dx = 0; dy = gridSize; changingDirection = true; }
        }

        function togglePause() {
            if (isCountingDown || isGameOver || !isStarted) return;
            if (!isPaused && !pauseUsed) {
                isPaused = true; pauseUsed = true; 
                if (hungerInterval) clearInterval(hungerInterval);
                countdownText = "⏸️ 일시정지";
            } else if (isPaused) {
                isPaused = false;
                countdownText = "";
                lastRenderTime = performance.now();
                resumeHungerTimer();
            }
        }

        window.addEventListener("keydown", function(e) {
            if (e.keyCode === 32 && !isStarted && !isCountingDown) { e.preventDefault(); triggerStart(); return; }
            if (e.keyCode === 80) { togglePause(); return; }
            if([37, 38, 39, 40, 32, 80].indexOf(e.keyCode) > -1) { e.preventDefault(); setDirection(e.keyCode); }
        }, false);

        const setupButtonListener = (id, action) => {
            const btn = document.getElementById(id);
            const handleAction = (e) => { e.preventDefault(); action(); };
            btn.addEventListener('touchstart', handleAction, {passive: false});
            btn.addEventListener('mousedown', handleAction);
        };
        setupButtonListener('btnUp', () => setDirection(38));
        setupButtonListener('btnDown', () => setDirection(40));
        setupButtonListener('btnLeft', () => setDirection(37));
        setupButtonListener('btnRight', () => setDirection(39));
        setupButtonListener('btnPause', () => togglePause());
    </script>
</body>
</html>
"""

# -------------------------------------------------------------
# 파일 폴더 생성 및 컴포넌트 선언 (캐시 방지 v41)
# -------------------------------------------------------------
component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_v41")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(GAME_HTML)

snake_game = components.declare_component("snake_v41", path=component_dir)

# -------------------------------------------------------------
# 랭킹 시스템 및 파일 관리
# -------------------------------------------------------------
SCORE_FILE = "snake_scores.json"

def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_score(nickname, score):
    scores = load_scores()
    kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    date_str = kst_now.strftime("%Y-%m-%d %H:%M")
    
    existing_user = next((item for item in scores if item["nickname"] == nickname), None)
    if existing_user:
        if score > existing_user["score"]:
            existing_user["score"] = score
            existing_user["date"] = date_str  
    else:
        scores.append({"nickname": nickname, "score": score, "date": date_str})
    
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)

# -------------------------------------------------------------
# 🏁 스트림릿 메인 화면 레이아웃
# -------------------------------------------------------------
st.title("⚡ 은하철도 스피드 러시 (Galaxy Express) 🚂")
st.info("🏆 999호의 차장이 되어 끝없는 우주 궤도를 질주하세요!")

col_empty, col1, col2 = st.columns([0.05, 2.3, 1.65])

with col_empty:
    st.empty() 

with col1:
    result = snake_game()
    
    if result and isinstance(result, dict):
        nickname = result.get("nickname")
        score = result.get("score")
        ts = result.get("timestamp")
        
        if "last_ts" not in st.session_state or st.session_state["last_ts"] != ts:
            save_score(nickname, score)
            st.session_state["last_ts"] = ts
            st.success(f"🎉 {nickname} 차장님! {score}명 탑승 완료 (랭킹 등록)!")
            st.rerun()

with col2:
    with st.expander("📖 게임 가이드 보기 (은하철도 999 모드)", expanded=True):
        tab1, tab2, tab3 = st.tabs(["🕹️ 설명", "📦 수화물(아이템)", "⚠️ 주의사항"])
        
        with tab1:
            st.markdown("""
            * **조작 방법**: 키보드 방향키 (PC) 또는 화면 하단 십자 버튼 (모바일)
            * **우주 열차 출발!**: 증기기관차가 헤드라이트를 비추며 매끄럽게 우주 궤도를 달립니다.
            * **일시정지**: 운행 중 위급할 때 **`[P]` 키 또는 온스크린 `[⏸️]` 버튼**을 누르면 정차합니다. (1게임당 **딱 1번만!**)
            * **하이퍼 스피드!**: 
              * 승객을 **50명(점수)** 태울 때마다 열차 속도가 서서히 빨라집니다!
            * **장갑(목숨) 시스템**: 총 **3겹(🛡️🛡️🛡️)**의 열차 장갑!
              * 소행성과 충돌 시 게임오버 대신 **객차(꼬리)만 3칸 터져나가며** 3초 대기 후 부활합니다.
            * 🌐 **250명 달성 스캐닝 그리드!**: 반투명 우주 궤도(격자)가 10초간 나타나 길을 안내합니다.
            * 🎉 **500명 달성 유성우!**: 점수가 500단위에 도달하면 **10초간** ⭐️별 조각이 무더기로 쏟아집니다.
            """)
            
        with tab2:
            st.markdown("""
            **미스터리 수화물(빛나는 핑크색 [?] 상자)** 안에는 아래 이벤트가 숨겨져 있습니다. 
            
            | 아이템 | 효과 설명 |
            | :--- | :--- |
            | 🌌 **안드로메다 정거장** | 꼬리 **30칸** 달성 시 화면 중앙에 거대한 은하수 역 출현! |
            | 💎 **우주 광석** | 승객 **+50명(점수)** 탑승 |
            | 🚀 **메텔의 가호** | 승객 **+100명(점수)** 특급 보너스 |
            | 🐢 **우주 기류 탑승** | 5초간 속도 **대폭 감소** |
            | ⚡ **하이퍼 드라이브** | 5초간 속도 **급상승** |
            | ⚠️ **암흑 성운** | 3초간 눈앞이 캄캄해짐 (시야 암전) |
            | 🌀 **블랙홀 진입** | 기관차와 꼬리가 뒤바뀌며 **방향 즉시 반전** |
            | ☣️ **중력 이상** | 3초간 **방향키 조작 반대** |
            | 💪 **전방위 실드** | 5초간 랜덤으로 **아이템 싹쓸이 자석 모드** 또는 초공간 도약(기체 축소) |
            | 💀 **해적 조우** | 승객 **-30명** 하차 (감점) |
            """)
            
        with tab3:
            st.markdown("""
            1. **🛤️ 10초 선로(에너지) 고갈 타이머!**
               * 10초 안에 선로를 이어가지 못하면 열차가 경로를 이탈하며, 강제 궤도 수정 페널티로 **꼬리(객차)가 4칸 강제로 늘어납니다.** (꼬리가 길어질수록 갇힐 위험이 커집니다!)
            2. **💪 쉴드 전개 자석 모드**
               * 쉴드 전개 상태일 때는 주변을 스치기만 해도 선로와 아이템을 자석처럼 싹쓸이합니다!
            3. **💥 꼬리 자르기 전략**
               * 갇힐 위기라면 차라리 벽이나 꼬리에 박으세요! 게임오버 대신 **객차만 3량 버리면서** 살아남을 수 있습니다.
            """)

    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False

    title_col, btn_col = st.columns([0.85, 0.15])
    with title_col:
        st.subheader("🏆 명예의 전당 (우수 차장 TOP 10)")
    with btn_col:
        st.write("")
        if st.button("✅", help="관리자 도구"):
            st.session_state.admin_mode = not st.session_state.admin_mode

    if st.session_state.admin_mode:
        with st.container():
            st.markdown("#### 🛠️ 은하철도 관리국")
            admin_password = st.text_input("국장 비밀번호를 입력하세요", type="password")
            if admin_password == "880610":
                st.success("✅ 인증 완료!")
                if st.button("🚨 랭킹 데이터 전체 초기화"):
                    if os.path.exists(SCORE_FILE):
                        os.remove
