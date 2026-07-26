import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
import datetime

# 페이지 설정
st.set_page_config(page_title="TJ 꿈틀꿈틀", page_icon="🐍", layout="wide")

# -------------------------------------------------------------
# 🚫 [상단 툴바 및 기본 메뉴 숨기기 CSS]
# -------------------------------------------------------------
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;} /* 우측 햄버거 메뉴 및 Share 숨기기 */
    header {visibility: hidden;}    /* 상단 GitHub, Edit 연필 아이콘 툴바 숨기기 */
    footer {visibility: hidden;}    /* 하단 Streamlit 워터마크 숨기기 */
    
    /* 체크모양 버튼 테두리 없애서 글자처럼 보이게 만들기 */
    button[title="View fullscreen"] {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# -------------------------------------------------------------
# 🎮 [HTML/JS 게임 엔진 생성]
# -------------------------------------------------------------
GAME_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            display: flex; flex-direction: column; align-items: center; 
            background-color: #2c3e50; color: white; 
            font-family: 'Malgun Gothic', sans-serif; 
            margin: 0; padding: 10px; height: 1100px; overflow: hidden; 
            touch-action: manipulation; /* 모바일 더블탭 줌 방지 */
        }
        
        /* 모바일 반응형 캔버스 컨테이너 */
        .canvas-container { 
            position: relative; 
            width: 100%; 
            max-width: 600px; 
            aspect-ratio: 1 / 1; 
        }
        canvas { 
            width: 100%; height: 100%; /* 컨테이너 크기에 맞춰 자동 축소/확대 */
            background-color: #34495e; 
            border: 3px solid #ecf0f1; 
            box-sizing: border-box;
            box-shadow: 0 0 15px rgba(0,0,0,0.5); 
        }
        #blindOverlay { 
            position: absolute; top: 0; left: 0; 
            width: 100%; height: 100%; 
            background-color: rgba(10, 15, 25, 0.98); 
            display: none; pointer-events: none; 
            justify-content: center; align-items: center; 
            font-size: 5vw; font-weight: bold; color: #7f8c8d; z-index: 10; 
        }
        
        .ui-container { display: flex; gap: 15px; margin-bottom: 10px; align-items: center; flex-wrap: wrap; justify-content: center; }
        .setup-container, .restart-container { margin-bottom: 20px; display: flex; gap: 10px; justify-content: center;}
        input { padding: 10px; font-size: 16px; border-radius: 5px; text-align: center; border: 1px solid #bdc3c7; max-width: 150px;}
        button.start-btn { padding: 10px 20px; font-size: 16px; font-weight: bold; background-color: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button.start-btn:hover { background-color: #c0392b; }
        
        #scoreBoard, #livesBoard, #timerBoard { font-size: 20px; font-weight: bold; }
        #livesBoard { color: #ff7675; }
        #timerBoard { color: #e67e22; }
        
        #itemEffect { font-size: 16px; color: #f1c40f; height: 24px; margin-bottom: 10px; font-weight: bold; text-align: center; }
        .info-text { font-size: 12px; color: #bdc3c7; margin-top: 10px; text-align: center; }

        /* 모바일 온스크린 컨트롤러 (D-Pad) */
        .mobile-controls {
            display: flex; flex-direction: column; align-items: center; margin-top: 20px; gap: 10px;
        }
        .ctrl-row { display: flex; gap: 20px; }
        .ctrl-btn {
            width: 70px; height: 70px; font-size: 30px; 
            border-radius: 15px; background-color: #7f8c8d; color: white; 
            border: 2px solid #95a5a6; box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
            touch-action: none; cursor: pointer; user-select: none;
            display: flex; justify-content: center; align-items: center;
        }
        .ctrl-btn:active { background-color: #95a5a6; transform: translateY(3px); box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
        .pause-btn { background-color: #f39c12; border-color: #f1c40f; font-size: 24px; border-radius: 50%; width: 60px; height: 60px; margin-top: 5px; }
        .pause-btn:active { background-color: #e67e22; }
    </style>
</head>
<body>
    <div class="setup-container" id="setupContainer">
        <input type="text" id="nicknameInput" placeholder="닉네임 입력!" maxlength="10">
        <button id="startBtn" class="start-btn">게임 시작</button>
    </div>

    <div class="restart-container" id="restartContainer" style="display: none;">
        <button id="restartBtn" class="start-btn" style="background-color: #3498db;">🔄 다시 도전</button>
    </div>

    <div class="ui-container">
        <div id="scoreBoard">점수: <span id="currentScore">0</span></div>
        <div id="livesBoard">목숨: <span id="heartDisplay">❤️❤️❤️</span></div>
        <div id="timerBoard">⏳ <span id="foodTimerDisplay">10</span>초</div>
    </div>
    <div id="itemEffect"></div>
    
    <div class="canvas-container">
        <canvas id="gameCanvas" width="600" height="600"></canvas>
        <div id="blindOverlay">👁️ 암흑 상태!</div>
    </div>
    
    <!-- 모바일/마우스 겸용 온스크린 컨트롤러 -->
    <div class="mobile-controls">
        <button id="btnUp" class="ctrl-btn">⬆️</button>
        <div class="ctrl-row">
            <button id="btnLeft" class="ctrl-btn">⬅️</button>
            <button id="btnPause" class="ctrl-btn pause-btn">⏸️</button>
            <button id="btnRight" class="ctrl-btn">➡️</button>
        </div>
        <button id="btnDown" class="ctrl-btn">⬇️</button>
    </div>
    
    <div class="info-text">[PC: 방향키/스페이스바/P] [모바일: 화면 버튼 터치]</div>

    <script>
        function sendToStreamlit(type, data) {
            const msg = { isStreamlitMessage: true, type: type };
            if (data) Object.assign(msg, data);
            window.parent.postMessage(msg, "*");
        }

        // 모바일 컨트롤러 공간을 위해 높이를 1100으로 넉넉하게 잡음
        function setHeight() { sendToStreamlit("streamlit:setFrameHeight", { height: 1100 }); }
        window.addEventListener("load", function() { sendToStreamlit("streamlit:componentReady", { apiVersion: 1 }); setHeight(); });
        window.addEventListener("message", function(event) { if (event.data && event.data.type === "streamlit:render") setHeight(); });

        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const gridSize = 20;
        
        let snake, normalFoods, hiddenFruits;
        let dx, dy, score, nickname, gameInterval, lives;
        let isCountingDown = false, isGameOver = false, isStarted = false;
        
        let baseSpeed = 100;
        let speedMod = 1;
        let isReversedControls = false;
        let snakeSizeMod = 1; 
        
        let blindTimeout = null;
        let controlTimeout = null;
        let sizeTimeout = null;
        
        let hungerTimer = 10;
        let hungerInterval = null;

        let changingDirection = false;

        let cloverSpawned = false;
        let isGiantCloverActive = false;
        let giantCloverBlocks = [];
        let cloverTimeout = null;
        
        let isPaused = false;
        let pauseUsed = false;
        
        let nextBonusScore = 500;
        let isBonusTime = false;
        let bonusFoods = [];
        let bonusTimeTimeout = null;
        
        let gridTriggered = false;
        let isGridTime = false;
        let gridTimeout = null;

        function initGame() {
            snake = [{ x: 300, y: 300 }]; dx = 0; dy = -gridSize;
            score = 0; lives = 3; isGameOver = false;
            baseSpeed = 100; speedMod = 1; isReversedControls = false; snakeSizeMod = 1;
            changingDirection = false;
            
            hungerTimer = 10;
            if (hungerInterval) clearInterval(hungerInterval);
            
            cloverSpawned = false;
            isGiantCloverActive = false;
            giantCloverBlocks = [];
            if (cloverTimeout) clearTimeout(cloverTimeout);
            
            isPaused = false;
            pauseUsed = false;
            
            nextBonusScore = 500;
            isBonusTime = false;
            bonusFoods = [];
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            
            gridTriggered = false;
            isGridTime = false;
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

        function startGameSequence() { initGame(); startCountdown(); }

        function startCountdown() {
            isCountingDown = true;
            let count = 3; 
            let countInterval = setInterval(() => {
                drawScreenWithText(count > 0 ? count : "시작!");
                count--;
                if (count < -1) {
                    clearInterval(countInterval); isCountingDown = false;
                    updateSpeed();
                    startHungerTimer();
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
                    effectDisplay.innerText = "⚠️ 아사 위기! 몸통 2칸 감소!"; 
                    effectDisplay.style.color = "#e74c3c";
                    
                    setTimeout(() => { 
                        if(effectDisplay.innerText.includes("아사") && !isBonusTime && !isGridTime && !isGiantCloverActive) {
                            effectDisplay.innerText = ""; 
                        }
                    }, 2000);
                    
                    hungerTimer = 10;
                    document.getElementById("foodTimerDisplay").innerText = hungerTimer;
                }
            }, 1000);
        }

        function startHungerTimer() {
            hungerTimer = 10;
            document.getElementById("foodTimerDisplay").innerText = hungerTimer;
            resumeHungerTimer();
        }

        function resetHungerTimer() {
            hungerTimer = 10;
            document.getElementById("foodTimerDisplay").innerText = hungerTimer;
        }

        function updateSpeed() {
            if(gameInterval) clearInterval(gameInterval);
            gameInterval = setInterval(main, baseSpeed * speedMod);
        }

        function updateGameDifficulty() {
            document.getElementById("currentScore").innerText = score;
            
            baseSpeed = Math.max(40, 100 - (score / 50) * 0.5);
            updateSpeed();
            
            let targetFoodCount = Math.min(5, 1 + Math.floor(score / 100));
            while(normalFoods.length < targetFoodCount) {
                normalFoods.push(generateValidPosition());
            }
            if (normalFoods.length === 0) normalFoods.push(generateValidPosition());
        }

        function drawScreenWithText(text) {
            clearCanvas(); drawNormalFoods(); drawSnake();
            ctx.fillStyle = "rgba(0, 0, 0, 0.5)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "white"; ctx.font = "bold 50px 'Malgun Gothic'";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(text, canvas.width / 2, canvas.height / 2);
        }

        function drawGrid() {
            ctx.strokeStyle = "rgba(255, 255, 255, 0.15)"; 
            ctx.lineWidth = 1;
            for(let x = 0; x <= canvas.width; x += gridSize) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for(let y = 0; y <= canvas.height; y += gridSize) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }
        }

        function main() {
            changingDirection = false; 
            
            if (checkCollision()) { handleDeath(); return; }
            clearCanvas(); 
            
            if (isGridTime) drawGrid();
            
            if (isBonusTime) {
                ctx.fillStyle = "rgba(241, 196, 15, 0.1)"; 
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.font = "bold 100px 'Malgun Gothic'";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = "rgba(241, 196, 15, 0.4)";
                ctx.fillText("BONUS!", canvas.width / 2, canvas.height / 2);
            }
            
            drawNormalFoods(); 
            drawHiddenFruits(); 
            drawGiantClover(); 
            drawBonusFoods(); 
            advanceSnake(); 
            drawSnake();
        }

        function handleDeath() {
            lives--;
            if (lives === 2) {
                reduceSnakeBody(3);
                alert(`앗! 첫 번째 충돌! (몸통 3칸 축소)`); resetSnakePosition();
            } else if (lives === 1) {
                reduceSnakeBody(3);
                alert(`위험합니다! 두 번째 충돌! (몸통 3칸 축소)`); resetSnakePosition();
            } else if (lives <= 0) {
                updateUI(); endGame();
            }
        }

        function reduceSnakeBody(count) {
            if (snake.length > count) { snake = snake.slice(0, snake.length - count); } 
            else { snake = [snake[0]]; }
        }

        function resetSnakePosition() {
            clearInterval(gameInterval);
            if(hungerInterval) clearInterval(hungerInterval);
            
            document.getElementById("blindOverlay").style.display = "none";
            isReversedControls = false; 
            
            snakeSizeMod = 1;
            if(sizeTimeout) clearTimeout(sizeTimeout);
            
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            isBonusTime = false;
            bonusFoods = [];
            
            if(gridTimeout) clearTimeout(gridTimeout);
            isGridTime = false;
            
            isGiantCloverActive = false;
            giantCloverBlocks = [];
            if(cloverTimeout) clearTimeout(cloverTimeout);
            
            updateUI();
            
            const headDiffX = 300 - snake[0].x;
            const headDiffY = 300 - snake[0].y;
            snake.forEach(part => { part.x += headDiffX; part.y += headDiffY; });
            dx = 0; dy = -gridSize;
            
            setTimeout(() => { 
                if(!isGameOver && !isPaused) {
                    updateSpeed(); 
                    startHungerTimer();
                }
            }, 1000);
        }

        function endGame() {
            clearInterval(gameInterval); 
            if(hungerInterval) clearInterval(hungerInterval); 
            if(cloverTimeout) clearTimeout(cloverTimeout);
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            if(gridTimeout) clearTimeout(gridTimeout);
            
            isGameOver = true; isStarted = false;
            
            document.getElementById("blindOverlay").style.display = "none";
            document.getElementById("restartContainer").style.display = "flex";
            alert(`게임 종료! 최종 점수: ${score}점`);
            sendToStreamlit("streamlit:setComponentValue", { 
                value: { nickname: nickname, score: score, timestamp: Date.now() } 
            });
        }

        function clearCanvas() { ctx.fillStyle = "#34495e"; ctx.fillRect(0, 0, canvas.width, canvas.height); }
        
        function drawSnake() { 
            snake.forEach((part, index) => { 
                let isHead = (index === 0);
                let isTail = (index === snake.length - 1 && snake.length > 1);

                if (isHead) ctx.fillStyle = isReversedControls ? "#e74c3c" : "#27ae60"; 
                else ctx.fillStyle = isReversedControls ? "#c0392b" : "#2ecc71";

                let currentDrawSize = (gridSize - 1) * snakeSizeMod;
                let offset = (gridSize - currentDrawSize) / 2;

                if (isTail) {
                    let tailSize = currentDrawSize * 0.6;
                    let tailOffset = (gridSize - tailSize) / 2;
                    ctx.fillRect(part.x + tailOffset, part.y + tailOffset, tailSize, tailSize);
                } else {
                    ctx.fillRect(part.x + offset, part.y + offset, currentDrawSize, currentDrawSize); 
                }

                if (isHead) {
                    ctx.fillStyle = "white";
                    let cx = part.x + 10;
                    let cy = part.y + 10;
                    
                    let eyeDist = 4 * snakeSizeMod;
                    let eyeOffset = 4 * snakeSizeMod;
                    let eyeRadius = 3.5 * snakeSizeMod;
                    let pupilRadius = 1.5 * snakeSizeMod;
                    
                    let e1x, e1y, e2x, e2y, px, py;
                    
                    if (dx > 0) {
                        e1x = cx + eyeOffset; e1y = cy - eyeDist; e2x = cx + eyeOffset; e2y = cy + eyeDist; px = 2 * snakeSizeMod; py = 0;
                    } else if (dx < 0) {
                        e1x = cx - eyeOffset; e1y = cy - eyeDist; e2x = cx - eyeOffset; e2y = cy + eyeDist; px = -2 * snakeSizeMod; py = 0;
                    } else if (dy > 0) {
                        e1x = cx - eyeDist; e1y = cy + eyeOffset; e2x = cx + eyeDist; e2y = cy + eyeOffset; px = 0; py = 2 * snakeSizeMod;
                    } else {
                        e1x = cx - eyeDist; e1y = cy - eyeOffset; e2x = cx + eyeDist; e2y = cy - eyeOffset; px = 0; py = -2 * snakeSizeMod;
                    }
                    
                    ctx.beginPath(); ctx.arc(e1x, e1y, eyeRadius, 0, Math.PI*2); ctx.fill();
                    ctx.beginPath(); ctx.arc(e2x, e2y, eyeRadius, 0, Math.PI*2); ctx.fill();
                    
                    ctx.fillStyle = "black";
                    ctx.beginPath(); ctx.arc(e1x + px, e1y + py, pupilRadius, 0, Math.PI*2); ctx.fill();
                    ctx.beginPath(); ctx.arc(e2x + px, e2y + py, pupilRadius, 0, Math.PI*2); ctx.fill();
                }
            }); 
        }

        function drawNormalFoods() { 
            ctx.fillStyle = "#e74c3c"; 
            normalFoods.forEach(food => ctx.fillRect(food.x, food.y, gridSize, gridSize)); 
        }
        
        function drawHiddenFruits() {
            ctx.font = "20px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            hiddenFruits.forEach(fruit => {
                ctx.fillText(fruit.emoji, fruit.x + (gridSize / 2), fruit.y + (gridSize / 2) + 2);
            });
        }

        function drawGiantClover() {
            if (isGiantCloverActive) {
                ctx.save();
                ctx.beginPath();
                ctx.rect(200, 200, 200, 200);
                ctx.clip();
                
                ctx.font = "200px Arial"; 
                ctx.textAlign = "center"; 
                ctx.textBaseline = "middle";
                ctx.fillText("🍀", 300, 315); 
                
                ctx.restore(); 
                
                ctx.fillStyle = "#34495e";
                for (let r = 0; r < 10; r++) {
                    for (let c = 0; c < 10; c++) {
                        let bx = 200 + c * gridSize;
                        let by = 200 + r * gridSize;
                        let isEaten = !giantCloverBlocks.some(b => b.x === bx && b.y === by);
                        if (isEaten) {
                            ctx.fillRect(bx, by, gridSize, gridSize);
                        }
                    }
                }
            }
        }
        
        function drawBonusFoods() {
            if (!isBonusTime) return;
            ctx.font = "18px Arial"; 
            ctx.textAlign = "center"; 
            ctx.textBaseline = "middle";
            bonusFoods.forEach(food => {
                ctx.fillText("⭐️", food.x + (gridSize / 2), food.y + (gridSize / 2) + 2);
            });
        }
        
        function advanceSnake() { 
            let head = { x: snake[0].x + dx, y: snake[0].y + dy }; 
            
            snake.unshift(head); 
            
            let hitRange = (snakeSizeMod > 1.2) ? gridSize : 0;
            let ateSomething = false;

            if (score >= 250 && !gridTriggered) {
                gridTriggered = true;
                isGridTime = true;
                
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🌐 250점 달성! 10초간 격자가 표시됩니다!";
                effectDisplay.style.color = "#3498db";
                
                gridTimeout = setTimeout(() => {
                    isGridTime = false;
                    if (!isGameOver && !isPaused && !isBonusTime && !isGiantCloverActive) effectDisplay.innerText = "";
                }, 10000); 
            }

            if (snake.length >= 30 && !cloverSpawned) {
                cloverSpawned = true;
                isGiantCloverActive = true;
                giantCloverBlocks = [];
                
                for (let r = 0; r < 10; r++) {
                    for (let c = 0; c < 10; c++) {
                        giantCloverBlocks.push({ x: 200 + c * gridSize, y: 200 + r * gridSize });
                    }
                }
                
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🍀 정중앙에 대형 클로버밭 등장! (5초)"; 
                effectDisplay.style.color = "#2ecc71";

                cloverTimeout = setTimeout(() => {
                    isGiantCloverActive = false;
                    giantCloverBlocks = [];
                    if (!isGameOver && !isPaused && !isGridTime && !isBonusTime) {
                        effectDisplay.innerText = "";
                    }
                }, 5000); 
            }

            if (isGiantCloverActive) {
                for (let i = giantCloverBlocks.length - 1; i >= 0; i--) {
                    let f = giantCloverBlocks[i];
                    if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                        score += 10; 
                        giantCloverBlocks.splice(i, 1); 
                        updateGameDifficulty();
                        resetHungerTimer();
                        ateSomething = true;
                    }
                }
            }

            if (isBonusTime) {
                for (let i = bonusFoods.length - 1; i >= 0; i--) {
                    let f = bonusFoods[i];
                    if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                        score += 10;
                        bonusFoods.splice(i, 1);
                        updateGameDifficulty();
                        resetHungerTimer();
                        ateSomething = true;
                    }
                }
            }

            for (let i = normalFoods.length - 1; i >= 0; i--) {
                let f = normalFoods[i];
                if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                    score += 10;
                    normalFoods.splice(i, 1);
                    updateGameDifficulty();
                    resetHungerTimer();
                    if (hiddenFruits.length < 3 && Math.random() < 0.4) spawnHiddenFruit();
                    ateSomething = true;
                }
            }
            
            for (let i = hiddenFruits.length - 1; i >= 0; i--) {
                let f = hiddenFruits[i];
                if (Math.abs(f.x - head.x) <= hitRange && Math.abs(f.y - head.y) <= hitRange) {
                    let fruit = hiddenFruits.splice(i, 1)[0];
                    applyHiddenFruitEffect(fruit.type);
                    resetHungerTimer();
                    ateSomething = true;
                }
            }

            if (!ateSomething) {
                snake.pop(); 
            }
            
            if (score >= nextBonusScore && !isBonusTime) {
                let spawnCount = 40; 
                if (nextBonusScore === 1000) spawnCount = 50;
                else if (nextBonusScore === 1500) spawnCount = 60;
                else if (nextBonusScore >= 2000) spawnCount = 80;
                
                nextBonusScore = Math.floor(score / 500) * 500 + 500; 
                isBonusTime = true;
                bonusFoods = [];
                
                for (let i = 0; i < spawnCount; i++) {
                    bonusFoods.push(generateValidPosition());
                }
                
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = `🎉 보너스 타임! 10초간 별이 ${spawnCount}개 쏟아집니다!`; 
                effectDisplay.style.color = "#f1c40f";
                
                bonusTimeTimeout = setTimeout(() => {
                    isBonusTime = false;
                    bonusFoods = [];
                    if (!isGameOver && !isPaused && !isGridTime && !isGiantCloverActive) {
                        effectDisplay.innerText = "";
                    }
                }, 10000); 
            }
        }

        function applyHiddenFruitEffect(type) {
            const effectDisplay = document.getElementById("itemEffect");
            if (type === 'blind') {
                effectDisplay.innerText = "☁️ 구름! 3초간 눈앞이 캄캄해집니다!"; effectDisplay.style.color = "#7f8c8d";
                document.getElementById("blindOverlay").style.display = "flex";
                if(blindTimeout) clearTimeout(blindTimeout);
                blindTimeout = setTimeout(() => { document.getElementById("blindOverlay").style.display = "none"; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 3000);
            
            } else if (type === 'tunnel') {
                effectDisplay.innerText = "🌀 터널! 지렁이 방향이 거꾸로 뒤집힙니다!"; effectDisplay.style.color = "#9b59b6";
                if (snake.length > 1) {
                    const tail = snake[snake.length - 1];
                    const beforeTail = snake[snake.length - 2];
                    dx = tail.x - beforeTail.x;
                    dy = tail.y - beforeTail.y;
                    snake.reverse();
                } else {
                    dx = -dx; dy = -dy;
                }
            
            } else if (type === 'reverse') {
                effectDisplay.innerText = "🍄 독버섯! 3초간 방향 조작이 반대로!"; effectDisplay.style.color = "#e67e22";
                isReversedControls = true;
                if(controlTimeout) clearTimeout(controlTimeout);
                controlTimeout = setTimeout(() => { isReversedControls = false; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 3000);
                
            } else if (type === 'caterpillar') {
                if (Math.random() < 0.5) {
                    effectDisplay.innerText = "🐛 왕꿈틀이! 먹이 싹쓸이! (5초)"; effectDisplay.style.color = "#2ecc71";
                    snakeSizeMod = 1.6; 
                } else {
                    effectDisplay.innerText = "🐛 꼬마 애벌레! 콩알만해집니다!"; effectDisplay.style.color = "#f1c40f";
                    snakeSizeMod = 0.5; 
                }
                if(sizeTimeout) clearTimeout(sizeTimeout);
                sizeTimeout = setTimeout(() => { snakeSizeMod = 1; if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);

            } else if (type === 'bonus') {
                score += 50; effectDisplay.innerText = "🍎 보너스 +50점!"; effectDisplay.style.color = "#f1c40f";
            } else if (type === 'slow') {
                effectDisplay.innerText = "🐢 바나나! 느릿느릿~ (5초)"; effectDisplay.style.color = "#3498db";
                speedMod = 1.6; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'fast') {
                effectDisplay.innerText = "⚡ 포도! 아주 빠르게! (5초)"; effectDisplay.style.color = "#9b59b6";
                speedMod = 0.5; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'penalty') {
                score = Math.max(0, score - 30); effectDisplay.innerText = "💀 오렌지! 감점 -30점!"; effectDisplay.style.color = "#e74c3c";
            } else if (type === 'super') {
                score += 100; effectDisplay.innerText = "🍓 딸기! 슈퍼 보너스 +100점!"; effectDisplay.style.color = "#ff7675";
            }
            
            updateGameDifficulty(); 
            setTimeout(() => { if(!['slow','fast','blind','reverse','caterpillar'].includes(type) && !isBonusTime && !isGridTime && !isGiantCloverActive) effectDisplay.innerText = ""; }, 2500);
        }

        function spawnHiddenFruit() {
            let pos = generateValidPosition();
            let fruit = { x: pos.x, y: pos.y, emoji: '❓', type: '', id: Date.now() };
            const rand = Math.random();
            
            if (rand < 0.12) { fruit.type = 'blind'; }
            else if (rand < 0.24) { fruit.type = 'tunnel'; }
            else if (rand < 0.36) { fruit.type = 'reverse'; }
            else if (rand < 0.48) { fruit.type = 'caterpillar'; } 
            else if (rand < 0.60) { fruit.type = 'bonus'; }
            else if (rand < 0.70) { fruit.type = 'slow'; }
            else if (rand < 0.80) { fruit.type = 'fast'; }
            else if (rand < 0.90) { fruit.type = 'penalty'; }
            else { fruit.type = 'super'; }
            
            hiddenFruits.push(fruit);
            
            setTimeout(() => { 
                hiddenFruits = hiddenFruits.filter(f => f.id !== fruit.id); 
            }, 8000);
        }
        
        function generateValidPosition() {
            let newPos;
            while (true) {
                newPos = { 
                    x: Math.floor(Math.random() * (canvas.width/gridSize)) * gridSize, 
                    y: Math.floor(Math.random() * (canvas.height/gridSize)) * gridSize 
                };
                if (!snake.some(part => part.x === newPos.x && part.y === newPos.y)) break;
            }
            return newPos;
        }
        
        function checkCollision() { 
            const head = { x: snake[0].x + dx, y: snake[0].y + dy };
            
            if (head.x < 0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height) return true; 
            
            for (let i = 0; i < snake.length - 1; i++) { 
                if (snake[i].x === head.x && snake[i].y === head.y) return true; 
            } 
            return false; 
        }

        // --- 컨트롤 함수 공통 모듈화 ---
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
                isPaused = true;
                pauseUsed = true; 
                clearInterval(gameInterval);
                if (hungerInterval) clearInterval(hungerInterval);
                
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)"; 
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "white"; 
                ctx.font = "bold 50px 'Malgun Gothic'";
                ctx.textAlign = "center"; 
                ctx.textBaseline = "middle";
                ctx.fillText("⏸️ 일시정지", canvas.width / 2, canvas.height / 2 - 20);
                
                ctx.font = "20px 'Malgun Gothic'";
                ctx.fillStyle = "#bdc3c7";
                ctx.fillText("다시 누르면 재개됩니다.", canvas.width / 2, canvas.height / 2 + 30);
                ctx.fillText("(게임당 1번만 사용 가능!)", canvas.width / 2, canvas.height / 2 + 60);
            } else if (isPaused) {
                isPaused = false;
                updateSpeed();
                resumeHungerTimer();
            }
        }

        // 1. 물리적 키보드 리스너
        window.addEventListener("keydown", function(e) {
            if (e.keyCode === 32 && !isStarted && !isCountingDown) { e.preventDefault(); triggerStart(); return; }
            if (e.keyCode === 80) { togglePause(); return; }
            if([37, 38, 39, 40, 32, 80].indexOf(e.keyCode) > -1) {
                e.preventDefault(); 
                setDirection(e.keyCode);
            }
        }, false);

        // 2. 모바일 온스크린 버튼 리스너 (touchstart 및 mousedown 대응)
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
# 파일 폴더 생성 및 컴포넌트 선언 (캐시 방지 v32)
# -------------------------------------------------------------
component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_v32")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(GAME_HTML)

snake_game = components.declare_component("snake_v32", path=component_dir)

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
st.title("🐍 TJ Random Speed Rush 🎮 ")
st.info(" 🏆최고의 점수에 도전해보자구요!! 게임가이드 보고 시작하기!! ")

# 모바일 호환을 위해 레이아웃 비율을 약간 조정했습니다.
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
            st.success(f"🎉 {nickname}님! {score}점 기록 완료!")
            st.rerun()

with col2:
    with st.expander("📖 게임 가이드 보기", expanded=False):
        tab1, tab2, tab3 = st.tabs(["🕹️ 설명", "🎁 아이템", "⚠️ 주의사항"])
        
        with tab1:
            st.markdown("""
            * **조작 방법**: 키보드 방향키 (PC) 또는 화면 하단 십자 버튼 (모바일)
            * **게임 시작/부활**: 닉네임 입력 후 `[Space Bar]` 또는 `[게임 시작]` 버튼 터치
            * **일시정지**: 게임 중 위급할 때 **`[P]` 키 또는 온스크린 `[⏸️]` 버튼**을 누르면 일시정지됩니다. (단, 1게임당 **딱 1번만** 사용 가능!)
            * **난이도 상승 (Speed Rush!)**: 
              * 점수가 **50점** 오를 때마다 속도가 **0.5씩 아주 조금씩** 빨라집니다.
              * 점수가 **100점** 오를 때마다 기본 먹이 개수가 증가합니다. (최대 5개)
            * **목숨(하트) 시스템**: 총 **3개(❤️❤️❤️)**의 목숨이 주어집니다.
              * 충돌 시 점수 감점 없이 **몸통만 3칸 줄어든 채** 중앙에서 부활합니다.
            * 🌐 **250점 격자 버프!**: 250점을 돌파하면 **10초간** 맵에 길을 찾기 쉽게 도와주는 반투명 격자가 나타납니다.
            * 🎉 **500점 돌파 피버 타임!**: 점수가 500단위에 도달하면 **10초간** 맵에 ⭐️(보너스 별)이 가득 차오르는 피버 타임이 발동합니다!
            """)
            
        with tab2:
            st.markdown("""
            **물음표(❓) 상자** 안에는 아래 아이템 중 하나가 숨겨져 있습니다. (클로버 제외)
            
            | 아이템 | 효과 설명 |
            | :--- | :--- |
            | 🍀 **대형 클로버밭** | 몸통이 **30칸**이 될 때 딱 한 번 맵 정중앙에 화면 절반만 한 대형 클로버(10x10 격자)가 **5초간** 나타납니다. **지나가는 자리마다 클로버를 갉아먹으며 1칸당 10점씩 획득!** |
            | 🍎 **사과** | 점수 **+50점** 획득 |
            | 🍓 **딸기** | 점수 **+100점** 획득 |
            | 🍌 **바나나** | 5초간 속도 **대폭 감소** |
            | 🍇 **포도** | 5초간 속도 **급상승** |
            | ☁️ **구름** | 3초간 눈앞이 캄캄해짐 |
            | 🌀 **터널** | 머리와 꼬리가 뒤바뀌며 **방향 즉시 반전** |
            | 🍄 **독버섯** | 3초간 **방향키 조작 반대** |
            | 🐛 **애벌레** | 5초간 랜덤으로 **왕꿈틀이(싹쓸이 버프)** 또는 꼬마 변신 |
            | 🍊 **오렌지** | 점수 **-30점** 감점 |
            """)
            
        with tab3:
            st.markdown("""
            1. **⏳ 10초 굶주림(아사) 타이머 주의!**
               * 10초 안에 먹이를 먹지 못하면 **몸통이 2칸 깎여 나갑니다.** 
            2. **🐛 왕꿈틀이 싹쓸이 모드**
               * 애벌레를 먹고 거대해졌을 땐, 주변을 스치기만 해도 모든 먹이를 진공청소기처럼 싹쓸이로 먹을 수 있습니다!
            3. **💥 전략적 충돌 (몸통 다이어트)**
               * 갇힐 위기라면 벽에 박으세요! 죽어도 점수는 깎이지 않고 **몸통만 3칸 다이어트** 됩니다.
            """)

    # ---------------------------------------------------------
    # 🏆 실시간 TOP 10 & 🛠️ 숨겨진 관리자 도구 (✅ 버튼)
    # ---------------------------------------------------------
    if "admin_mode" not in st.session_state:
        st.session_state.admin_mode = False

    title_col, btn_col = st.columns([0.85, 0.15])
    with title_col:
        st.subheader("🏆 실시간 TOP 10")
    with btn_col:
        st.write("") # 약간 아래로 내리기 위한 여백
        if st.button("✅", help="관리자 도구"):
            st.session_state.admin_mode = not st.session_state.admin_mode

    # 관리자 버튼 클릭 시 나타나는 비밀 메뉴
    if st.session_state.admin_mode:
        with st.container():
            st.markdown("#### 🛠️ 관리자 도구")
            admin_password = st.text_input("관리자 비밀번호를 입력하세요", type="password")
            if admin_password == "880610":
                st.success("✅ 관리자 인증 완료!")
                if st.button("🚨 랭킹 데이터 전체 초기화"):
                    if os.path.exists(SCORE_FILE):
                        os.remove(SCORE_FILE)
                        st.success("데이터가 성공적으로 삭제되었습니다.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.info("삭제할 랭킹 데이터가 없습니다.")
            elif admin_password != "":
                st.error("❌ 비밀번호가 틀렸습니다.")
            st.markdown("---")

    scores = load_scores()
    
    if not scores:
        st.write("첫 기록을 남겨보세요!")
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
