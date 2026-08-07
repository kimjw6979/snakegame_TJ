import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
import datetime

# 페이지 설정
st.set_page_config(page_title="TJ 네온 스피드 러시", page_icon="🐍", layout="wide")

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
# 🎮 [HTML/JS 최신 네온 트렌드 게임 엔진]
# -------------------------------------------------------------
GAME_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        /* 트렌디한 다크/네온 테마 (사이버펑크 & 글래스모피즘) */
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
            background-image: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
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
            background-color: #0b1120; 
            border-radius: 16px;
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.15), inset 0 0 20px rgba(0,0,0,0.8);
            border: 2px solid rgba(16, 185, 129, 0.3);
            box-sizing: border-box;
        }

        #blindOverlay { 
            position: absolute; top: 0; left: 0; 
            width: 100%; height: 100%; 
            background-color: rgba(11, 17, 32, 0.98); 
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
        input:focus { border-color: var(--neon-green); box-shadow: 0 0 10px var(--neon-green); }

        button.start-btn { 
            padding: 12px 24px; font-size: 16px; font-weight: 800; 
            background: linear-gradient(135deg, #10b981, #059669); 
            color: white; border: none; border-radius: 12px; cursor: pointer; 
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); transition: transform 0.1s, box-shadow 0.2s;
        }
        button.start-btn:active { transform: scale(0.95); }
        
        #scoreBoard { color: var(--neon-green); text-shadow: 0 0 10px var(--neon-green); }
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
            background: rgba(16, 185, 129, 0.4); color: white; border-color: var(--neon-green);
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
        <input type="text" id="nicknameInput" placeholder="닉네임 입력!" maxlength="10">
        <button id="startBtn" class="start-btn">⚡ GAME START</button>
    </div>

    <div class="restart-container" id="restartContainer" style="display: none;">
        <button id="restartBtn" class="start-btn" style="background: linear-gradient(135deg, #3b82f6, #2563eb);">🔄 RETRY</button>
    </div>

    <div class="ui-container">
        <div id="scoreBoard">SCORE: <span id="currentScore">0</span></div>
        <div id="livesBoard">LIFE: <span id="heartDisplay">❤️❤️❤️</span></div>
        <div id="timerBoard">⏳ <span id="foodTimerDisplay">10</span>s</div>
    </div>
    <div id="itemEffect"></div>
    
    <div class="canvas-container">
        <canvas id="gameCanvas" width="600" height="600"></canvas>
        <div id="blindOverlay">SYSTEM MALFUNCTION... 👁️</div>
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

        function initGame() {
            snake = [{ x: 300, y: 300 }]; dx = 0; dy = -gridSize;
            score = 0; lives = 3; isGameOver = false; particles = [];
            baseSpeed = 100; speedMod = 1; isReversedControls = false; snakeSizeMod = 1;
            changingDirection = false;
            
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
            document.getElementById("heartDisplay").innerText = "❤️".repeat(lives);
            document.getElementById("foodTimerDisplay").innerText = hungerTimer;
            if (!isBonusTime && !isGridTime && !isGiantCloverActive) document.getElementById("itemEffect").innerText = "";
        }

        document.getElementById("startBtn").addEventListener("click", triggerStart);
        document.getElementById("restartBtn").addEventListener("click", triggerStart);

        function triggerStart() {
            const inputVal = document.getElementById("nicknameInput").value.trim();
            if (document.getElementById("setupContainer").style.display !== "none") {
                if (!inputVal) { alert("⚠️ 게임 시작을 위해 닉네임을 입력해주세요!"); return; }
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
            let count = 3; 
            let countInterval = setInterval(() => {
                drawScreenWithText(count > 0 ? count : "START!");
                count--;
                if (count < -1) {
                    clearInterval(countInterval); isCountingDown = false;
                    lastRenderTime = performance.now();
                    accumulator = 0;
                    requestAnimationFrame(gameLoop); 
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
                    reduceSnakeBody(2);
                    const effectDisplay = document.getElementById("itemEffect");
                    effectDisplay.innerText = "⚠️ SYSTEM WARNING: 에너지 고갈! 몸통 감소!"; 
                    effectDisplay.style.color = "var(--neon-red)";
                    setTimeout(() => { if(effectDisplay.innerText.includes("에너지") && !isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 2000);
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

        function drawScreenWithText(text) {
            clearCanvas(); renderFrame(true);
            ctx.fillStyle = "rgba(11, 17, 32, 0.7)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "var(--neon-green)"; ctx.font = "bold 60px 'Pretendard'";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.shadowBlur = 20; ctx.shadowColor = "var(--neon-green)";
            ctx.fillText(text, canvas.width / 2, canvas.height / 2);
            ctx.shadowBlur = 0;
        }

        function clearCanvas() { ctx.clearRect(0, 0, canvas.width, canvas.height); }

        function drawGrid() {
            ctx.strokeStyle = "rgba(16, 185, 129, 0.15)"; ctx.lineWidth = 1;
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
            if (isGridTime) drawGrid();
            
            if (isBonusTime) {
                ctx.fillStyle = "rgba(251, 191, 36, 0.05)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.font = "bold 90px 'Pretendard'"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
                ctx.fillStyle = "rgba(251, 191, 36, 0.2)";
                ctx.fillText("FEVER!", canvas.width / 2, canvas.height / 2);
            }
            
            drawGiantClover(); 
            drawNormalFoods(); 
            drawHiddenFruits(); 
            drawBonusFoods(); 
            updateAndDrawParticles(); 
            drawSnakePath(); // 디테일이 추가된 뱀 머리 호출
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
                if(isPaused) { } else { p.x += p.vx; p.y += p.vy; p.life -= 0.05; }
                if(p.life <= 0) { particles.splice(i, 1); continue; }
                ctx.globalAlpha = p.life;
                ctx.fillStyle = p.color;
                ctx.shadowBlur = 10; ctx.shadowColor = p.color;
                ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI*2); ctx.fill();
                ctx.shadowBlur = 0; ctx.globalAlpha = 1.0;
            }
        }

        // --- 🐍 [NEW] 네온 뱀 머리 퀄리티 업그레이드 ---
        function drawSnakePath() {
            if (snake.length === 0) return;
            
            let strokeColor = isReversedControls ? "var(--neon-red)" : "var(--neon-green)";
            let w = Math.max(4, (gridSize - 4) * snakeSizeMod);

            // 1. 몸통 그리기
            ctx.beginPath();
            ctx.moveTo(snake[0].x + gridSize/2, snake[0].y + gridSize/2);
            for(let i=1; i<snake.length; i++) {
                ctx.lineTo(snake[i].x + gridSize/2, snake[i].y + gridSize/2);
            }
            
            ctx.lineCap = "round"; ctx.lineJoin = "round";
            ctx.lineWidth = w;
            ctx.strokeStyle = strokeColor;
            
            ctx.shadowBlur = 15;
            ctx.shadowColor = strokeColor;
            ctx.stroke();
            ctx.shadowBlur = 0;
            
            // 2. ✨ 진짜 뱀 머리 그리기 (이동 방향에 따라 회전)
            let headX = snake[0].x + gridSize/2;
            let headY = snake[0].y + gridSize/2;

            ctx.save();
            ctx.translate(headX, headY);

            // 현재 이동 방향(dx, dy)을 기준으로 캔버스 회전
            let angle = 0;
            if (dx > 0) angle = 0;                  // 오른쪽
            else if (dx < 0) angle = Math.PI;       // 왼쪽
            else if (dy > 0) angle = Math.PI / 2;   // 아래
            else if (dy < 0) angle = -Math.PI / 2;  // 위
            ctx.rotate(angle);

            // 머리 윤곽 (살짝 납작한 타원형)
            ctx.fillStyle = strokeColor;
            ctx.shadowBlur = 15;
            ctx.shadowColor = strokeColor;
            ctx.beginPath();
            ctx.ellipse(0, 0, w * 0.7, w * 0.55, 0, 0, Math.PI * 2);
            ctx.fill();

            // 하얀색 눈
            ctx.fillStyle = "#ffffff";
            ctx.shadowBlur = 5;
            ctx.shadowColor = "#ffffff";
            
            ctx.beginPath(); // 왼쪽 눈
            ctx.arc(w * 0.2, -w * 0.25, w * 0.15, 0, Math.PI*2); 
            ctx.fill();
            
            ctx.beginPath(); // 오른쪽 눈
            ctx.arc(w * 0.2, w * 0.25, w * 0.15, 0, Math.PI*2); 
            ctx.fill();

            // 까만색 동공 (뱀 특유의 세로로 찢어진 눈)
            ctx.fillStyle = "#000000";
            ctx.shadowBlur = 0;
            ctx.fillRect(w * 0.15, -w * 0.35, w * 0.05, w * 0.2); // 왼쪽 동공
            ctx.fillRect(w * 0.15, w * 0.15, w * 0.05, w * 0.2);  // 오른쪽 동공

            // 갈라지며 낼름거리는 붉은 혀
            ctx.strokeStyle = "var(--neon-red)";
            ctx.lineWidth = 1.5;
            ctx.shadowBlur = 5;
            ctx.shadowColor = "var(--neon-red)";
            
            ctx.beginPath();
            ctx.moveTo(w * 0.7, 0);         // 입에서 출발
            ctx.lineTo(w * 1.2, 0);         // 혀 기둥
            ctx.lineTo(w * 1.4, -w * 0.15); // 위쪽으로 갈라짐
            ctx.moveTo(w * 1.2, 0);         // 다시 갈라지는 곳으로
            ctx.lineTo(w * 1.4, w * 0.15);  // 아래쪽으로 갈라짐
            ctx.stroke();

            ctx.restore(); // 회전 및 좌표축 복구
        }

        function drawNormalFoods() { 
            ctx.fillStyle = "var(--neon-red)"; 
            ctx.shadowBlur = 15; ctx.shadowColor = "var(--neon-red)";
            normalFoods.forEach(food => {
                ctx.beginPath(); ctx.arc(food.x + gridSize/2, food.y + gridSize/2, gridSize/2 - 2, 0, Math.PI*2); ctx.fill();
            });
            ctx.shadowBlur = 0;
        }
        
        function drawHiddenFruits() {
            ctx.font = "20px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            hiddenFruits.forEach(fruit => {
                ctx.fillText("📦", fruit.x + (gridSize / 2), fruit.y + (gridSize / 2) + 2); 
            });
        }

        function drawGiantClover() {
            if (isGiantCloverActive) {
                ctx.save();
                ctx.beginPath(); ctx.rect(200, 200, 200, 200); ctx.clip();
                ctx.font = "180px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
                ctx.fillText("🍀", 300, 310); 
                ctx.restore(); 
                
                ctx.fillStyle = "#0b1120";
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
            ctx.font = "18px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            bonusFoods.forEach(food => { ctx.fillText("⭐️", food.x + (gridSize / 2), food.y + (gridSize / 2) + 2); });
        }
        
        function advanceSnake() { 
            let head = { x: snake[0].x + dx, y: snake[0].y + dy }; 
            snake.unshift(head); 
            
            let hitRange = (snakeSizeMod > 1.2) ? gridSize : 0;
            let ateSomething = false;

            if (score >= 250 && !gridTriggered) {
                gridTriggered = true; isGridTime = true;
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🌐 시스템 해킹! 10초간 스캐닝 그리드 활성화!";
                effectDisplay.style.color = "var(--neon-blue)";
                gridTimeout = setTimeout(() => { isGridTime = false; if (!isGameOver && !isPaused && !isBonusTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 10000); 
            }

            if (snake.length >= 30 && !cloverSpawned) {
                cloverSpawned = true; isGiantCloverActive = true; giantCloverBlocks = [];
                for (let r = 0; r < 10; r++) { for (let c = 0; c < 10; c++) { giantCloverBlocks.push({ x: 200 + c * gridSize, y: 200 + r * gridSize }); } }
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🍀 데이터 덩어리 발견! 정중앙 5초간 출현!"; 
                effectDisplay.style.color = "var(--neon-green)";
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
                        createParticles(f.x, f.y, "var(--neon-green)");
                    }
                }
            }

            if (isBonusTime) {
                for (let i = bonusFoods.length - 1; i >= 0; i--) {
                    let f = bonusFoods[i];
                    if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                        score += 10; bonusFoods.splice(i, 1); updateGameDifficulty(); resetHungerTimer(); ateSomething = true;
                        createParticles(f.x, f.y, "var(--neon-gold)");
                    }
                }
            }

            for (let i = normalFoods.length - 1; i >= 0; i--) {
                let f = normalFoods[i];
                if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                    score += 10; normalFoods.splice(i, 1); updateGameDifficulty(); resetHungerTimer();
                    if (hiddenFruits.length < 3 && Math.random() < 0.4) spawnHiddenFruit();
                    ateSomething = true;
                    createParticles(f.x, f.y, "var(--neon-red)");
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
                effectDisplay.innerText = `🎉 FEVER TIME! 별 조각 ${spawnCount}개 드랍!`; effectDisplay.style.color = "var(--neon-gold)";
                bonusTimeTimeout = setTimeout(() => {
                    isBonusTime = false; bonusFoods = [];
                    if (!isGameOver && !isPaused && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = "";
                }, 10000); 
            }
        }

        function applyHiddenFruitEffect(type) {
            const effectDisplay = document.getElementById("itemEffect");
            if (type === 'blind') {
                effectDisplay.innerText = "⚠️ 시야 해킹! 3초간 암흑!"; effectDisplay.style.color = "#94a3b8";
                document.getElementById("blindOverlay").style.display = "flex";
                if(blindTimeout) clearTimeout(blindTimeout);
                blindTimeout = setTimeout(() => { document.getElementById("blindOverlay").style.display = "none"; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 3000);
            } else if (type === 'tunnel') {
                effectDisplay.innerText = "🌀 웜홀 진입! 머리와 꼬리 반전!"; effectDisplay.style.color = "#c084fc";
                if (snake.length > 1) { const tail = snake[snake.length - 1]; const beforeTail = snake[snake.length - 2]; dx = tail.x - beforeTail.x; dy = tail.y - beforeTail.y; snake.reverse(); } else { dx = -dx; dy = -dy; }
            } else if (type === 'reverse') {
                effectDisplay.innerText = "☣️ 바이러스 감염! 3초간 조작 반전!"; effectDisplay.style.color = "var(--neon-red)";
                isReversedControls = true;
                if(controlTimeout) clearTimeout(controlTimeout);
                controlTimeout = setTimeout(() => { isReversedControls = false; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 3000);
            } else if (type === 'caterpillar') {
                if (Math.random() < 0.5) { effectDisplay.innerText = "💪 파워업! 아이템 싹쓸이 모드 (5초)"; effectDisplay.style.color = "var(--neon-blue)"; snakeSizeMod = 1.8; } 
                else { effectDisplay.innerText = "📉 꼬마 변신! 콩알만해집니다!"; effectDisplay.style.color = "var(--neon-gold)"; snakeSizeMod = 0.5; }
                if(sizeTimeout) clearTimeout(sizeTimeout);
                sizeTimeout = setTimeout(() => { snakeSizeMod = 1; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'bonus') {
                score += 50; effectDisplay.innerText = "💎 보너스 코인 +50점!"; effectDisplay.style.color = "var(--neon-gold)";
            } else if (type === 'slow') {
                effectDisplay.innerText = "🐢 냉각수 가동! 속도 저하 (5초)"; effectDisplay.style.color = "var(--neon-blue)";
                speedMod = 1.6; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'fast') {
                effectDisplay.innerText = "⚡ 오버클럭! 속도 급상승 (5초)"; effectDisplay.style.color = "#c084fc";
                speedMod = 0.5; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'penalty') {
                score = Math.max(0, score - 30); effectDisplay.innerText = "💀 배드섹터! 감점 -30점!"; effectDisplay.style.color = "var(--neon-red)";
            } else if (type === 'super') {
                score += 100; effectDisplay.innerText = "🚀 잭팟! 슈퍼 보너스 +100점!"; effectDisplay.style.color = "var(--neon-green)";
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

        function handleDeath() {
            lives--;
            if (lives > 0) {
                reduceSnakeBody(3);
                alert(`⚠️ 충돌 발생! 생명력 손실 (현재 목숨: ${lives})`); resetSnakePosition();
            } else {
                updateUI(); endGame();
            }
        }

        function reduceSnakeBody(count) {
            if (snake.length > count) { snake = snake.slice(0, snake.length - count); } else { snake = [snake[0]]; }
        }

        function resetSnakePosition() {
            if(hungerInterval) clearInterval(hungerInterval);
            document.getElementById("blindOverlay").style.display = "none";
            isReversedControls = false; snakeSizeMod = 1;
            if(sizeTimeout) clearTimeout(sizeTimeout);
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            isBonusTime = false; bonusFoods = [];
            if(gridTimeout) clearTimeout(gridTimeout);
            isGridTime = false;
            isGiantCloverActive = false; giantCloverBlocks = [];
            if(cloverTimeout) clearTimeout(cloverTimeout);
            
            updateUI();
            const headDiffX = 300 - snake[0].x; const headDiffY = 300 - snake[0].y;
            snake.forEach(part => { part.x += headDiffX; part.y += headDiffY; });
            dx = 0; dy = -gridSize;
            
            setTimeout(() => { if(!isGameOver && !isPaused) { startHungerTimer(); } }, 1000);
        }

        function endGame() {
            if(hungerInterval) clearInterval(hungerInterval); 
            if(cloverTimeout) clearTimeout(cloverTimeout);
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            if(gridTimeout) clearTimeout(gridTimeout);
            
            isGameOver = true; isStarted = false;
            
            document.getElementById("blindOverlay").style.display = "none";
            document.getElementById("restartContainer").style.display = "flex";
            
            renderFrame(false); 
            ctx.fillStyle = "rgba(11, 17, 32, 0.8)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "var(--neon-red)"; ctx.font = "bold 50px 'Pretendard'";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.shadowBlur = 15; ctx.shadowColor = "var(--neon-red)";
            ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);
            ctx.fillStyle = "white"; ctx.font = "24px 'Pretendard'"; ctx.shadowBlur = 0;
            ctx.fillText(`SCORE : ${score}`, canvas.width / 2, canvas.height / 2 + 30);
            
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
                ctx.fillStyle = "rgba(11, 17, 32, 0.7)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "var(--neon-gold)"; ctx.font = "bold 50px 'Pretendard'"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
                ctx.fillText("⏸️ PAUSE", canvas.width / 2, canvas.height / 2 - 20);
                ctx.fillStyle = "#94a3b8"; ctx.font = "20px 'Pretendard'";
                ctx.fillText("(게임당 1번만 사용 가능!)", canvas.width / 2, canvas.height / 2 + 30);
            } else if (isPaused) {
                isPaused = false;
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
# 파일 폴더 생성 및 컴포넌트 선언 (캐시 방지 v35)
# -------------------------------------------------------------
component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_v35")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(GAME_HTML)

snake_game = components.declare_component("snake_v35", path=component_dir)

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
st.title("⚡ 네온 스피드 러시 (Neon Speed Rush) 🎮")
st.info("🏆 새롭게 업그레이드된 엔진과 세련된 뱀 머리로 스릴을 즐겨보세요!")

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
            st.success(f"🎉 {nickname}님! {score}점 랭킹 등록 완료!")
            st.rerun()

with col2:
    with st.expander("📖 게임 가이드 보기 (업그레이드 완료)", expanded=True):
        tab1, tab2, tab3 = st.tabs(["🕹️ 설명", "📦 아이템", "⚠️ 주의사항"])
        
        with tab1:
            st.markdown("""
            * **조작 방법**: 키보드 방향키 (PC) 또는 화면 하단 십자 버튼 (모바일)
            * **부드러운 엔진 적용!**: 이제 지렁이가 네온 빛을 내며 곡선으로 훨씬 부드럽게 미끄러집니다.
            * **일시정지**: 게임 중 위급할 때 **`[P]` 키 또는 온스크린 `[⏸️]` 버튼**을 누르면 일시정지됩니다. (1게임당 **딱 1번만!**)
            * **난이도 상승 (Speed Rush!)**: 
              * 점수가 **50점** 오를 때마다 속도가 약간씩 상승!
            * **목숨(하트) 시스템**: 총 **3개(❤️❤️❤️)**의 목숨!
              * 충돌 시 점수 감점 없이 **몸통만 3칸 줄어든 채** 중앙에서 부활합니다.
            * 🌐 **250점 스캐닝 그리드!**: 반투명 격자가 나타나 길을 안내해 줍니다.
            * 🎉 **500점 피버 타임!**: 점수가 500단위에 도달하면 **10초간** ⭐️별 조각이 쏟아집니다.
            """)
            
        with tab2:
            st.markdown("""
            **미스터리 상자(📦)** 안에는 아래 효과가 숨겨져 있습니다. 
            
            | 아이템 | 효과 설명 |
            | :--- | :--- |
            | 🍀 **데이터 덩어리** | 몸통 **30칸** 달성 시 화면 중앙에 거대한 클로버 밭 출현! |
            | 💎 **보너스 코인** | 점수 **+50점** 획득 |
            | 🚀 **잭팟 슈퍼** | 점수 **+100점** 획득 |
            | 🐢 **냉각수 가동** | 5초간 속도 **대폭 감소** |
            | ⚡ **오버클럭** | 5초간 속도 **급상승** |
            | ⚠️ **시야 해킹** | 3초간 눈앞이 캄캄해짐 |
            | 🌀 **웜홀 진입** | 머리와 꼬리가 뒤바뀌며 **방향 즉시 반전** |
            | ☣️ **바이러스** | 3초간 **방향키 조작 반대** |
            | 💪 **파워업** | 5초간 랜덤으로 **아이템 싹쓸이 모드** 또는 꼬마 변신 |
            | 💀 **배드섹터** | 점수 **-30점** 감점 |
            """)
            
        with tab3:
            st.markdown("""
            1. **⏳ 10초 에너지 고갈 타이머!**
               * 10초 안에 먹이를 먹지 못하면 **몸통이 2칸 깎여 나갑니다.** 
            2. **💪 파워업 싹쓸이 모드**
               * 파워업 상태일 때는 주변을 스치기만 해도 모든 아이템을 자석처럼 싹쓸이합니다!
            3. **💥 전략적 충돌**
               * 갇힐 위기라면 벽에 박으세요! 게임오버 대신 **몸통만 3칸 다이어트** 됩니다.
            """)

    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False

    title_col, btn_col = st.columns([0.85, 0.15])
    with title_col:
        st.subheader("🏆 명예의 전당 (TOP 10)")
    with btn_col:
        st.write("")
        if st.button("✅", help="관리자 도구"):
            st.session_state.admin_mode = not st.session_state.admin_mode

    if st.session_state.admin_mode:
        with st.container():
            st.markdown("#### 🛠️ 관리자 도구")
            admin_password = st.text_input("관리자 비밀번호를 입력하세요", type="password")
            if admin_password == "880610":
                st.success("✅ 인증 완료!")
                if st.button("🚨 랭킹 데이터 전체 초기화"):
                    if os.path.exists(SCORE_FILE):
                        os.remove(SCORE_FILE)
                        st.success("삭제되었습니다.")
                        time.sleep(1)
                        st.rerun()
            elif admin_password != "":
                st.error("❌ 비밀번호 오류")
            st.markdown("---")

    scores = load_scores()
    
    if not scores:
        st.write("아직 랭킹에 등록된 기록이 없습니다. 첫 번째 주자가 되어보세요!")
    else:
        board_html = "<div style='display: flex; flex-direction: column; gap: 8px;'>"
        for i, s in enumerate(scores):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}위"
            date_str = f" <span style='font-size: 12px; font-weight: normal; color: #888;'>👑 (달성: {s.get('date', '알수없음')})</span>" if i == 0 and "date" in s else ""
            
            board_html += "<div style='border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 8px;'>"
            board_html += f"<div style='font-weight: bold; font-size: 16px; margin-bottom: 2px;'>{medal} | {s['nickname']}{date_str}</div>"
            board_html += f"<div style='font-size: 13px; color: gray;'>Score: {s['score']} pts</div>"
            board_html += "</div>"
            
        board_html += "</div>"
        st.markdown(board_html, unsafe_allow_html=True)
