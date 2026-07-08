import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
import datetime

# 기존에 있던 페이지 설정 코드
st.set_page_config(page_title="TJ 꿈틀꿈틀", page_icon="🐍", layout="wide")

# -------------------------------------------------------------
# 🚫 [상단 툴바 및 기본 메뉴 숨기기 CSS]
# -------------------------------------------------------------
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;} /* 우측 햄버거 메뉴 및 Share 숨기기 */
    header {visibility: hidden;}    /* 상단 GitHub, Edit 연필 아이콘 툴바 숨기기 */
    footer {visibility: hidden;}    /* 하단 Streamlit 워터마크 숨기기 */
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
    <style>
        body { display: flex; flex-direction: column; align-items: center; background-color: #2c3e50; color: white; font-family: 'Malgun Gothic', sans-serif; margin: 0; padding: 10px; height: 900px; overflow: hidden; }
        
        .canvas-container { position: relative; width: 600px; height: 600px; }
        canvas { background-color: #34495e; border: 3px solid #ecf0f1; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
        #blindOverlay { position: absolute; top: 3px; left: 3px; width: 600px; height: 600px; background-color: rgba(10, 15, 25, 0.98); display: none; pointer-events: none; justify-content: center; align-items: center; font-size: 30px; font-weight: bold; color: #7f8c8d; z-index: 10; }
        
        .ui-container { display: flex; gap: 20px; margin-bottom: 10px; align-items: center; }
        .setup-container, .restart-container { margin-bottom: 20px; display: flex; gap: 10px; justify-content: center;}
        input { padding: 10px; font-size: 16px; border-radius: 5px; text-align: center; border: 1px solid #bdc3c7;}
        button { padding: 10px 20px; font-size: 16px; font-weight: bold; background-color: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #c0392b; }
        #scoreBoard, #livesBoard { font-size: 22px; font-weight: bold; }
        #livesBoard { color: #ff7675; }
        #timerBoard { font-size: 22px; font-weight: bold; color: #e67e22; }
        
        #itemEffect { font-size: 18px; color: #f1c40f; height: 24px; margin-bottom: 10px; font-weight: bold; }
        .info-text { font-size: 12px; color: #bdc3c7; margin-top: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="setup-container" id="setupContainer">
        <input type="text" id="nicknameInput" placeholder="닉네임 입력 필수!" maxlength="10">
        <button id="startBtn">게임 시작 (Space)</button>
    </div>

    <div class="restart-container" id="restartContainer" style="display: none;">
        <button id="restartBtn" style="background-color: #3498db;">🔄 다시 도전 (Space)</button>
    </div>

    <div class="ui-container">
        <div id="scoreBoard">점수: <span id="currentScore">0</span></div>
        <div id="livesBoard">목숨: <span id="heartDisplay">❤️❤️❤️</span></div>
        <div id="timerBoard">⏳ <span id="foodTimerDisplay">10</span>초</div>
    </div>
    <div id="itemEffect"></div>
    
    <div class="canvas-container">
        <canvas id="gameCanvas" width="600" height="600"></canvas>
        <div id="blindOverlay">👁️ 암흑 상태 (앞이 보이지 않습니다!)</div>
    </div>
    <div class="info-text">[Space Bar]: 시작/재도전 | [P]: 일시정지 (게임당 1회)</div>

    <script>
        function sendToStreamlit(type, data) {
            const msg = { isStreamlitMessage: true, type: type };
            if (data) Object.assign(msg, data);
            window.parent.postMessage(msg, "*");
        }

        function setHeight() { sendToStreamlit("streamlit:setFrameHeight", { height: 900 }); }
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
        
        let warpGate = { active: false, p1: {x: 0, y: 0}, p2: {x: 0, y: 0} };
        let warpTimeout = null;
        let warpScheduleTimeout = null;
        let hitWarpCooldown = 0; 

        // 🍀 클로버, ⏸️ 일시정지, 🌟 보너스 타임, 🌐 격자 이벤트 변수
        let clover = null;
        let cloverSpawned = false;
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
            
            hungerTimer = 10;
            if (hungerInterval) clearInterval(hungerInterval);
            
            clover = null;
            cloverSpawned = false;
            if (cloverTimeout) clearTimeout(cloverTimeout);
            
            isPaused = false;
            pauseUsed = false;
            
            // 보너스 및 격자 이벤트 초기화
            nextBonusScore = 500;
            isBonusTime = false;
            bonusFoods = [];
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            
            gridTriggered = false;
            isGridTime = false;
            if(gridTimeout) clearTimeout(gridTimeout);
            
            if(warpTimeout) clearTimeout(warpTimeout);
            if(warpScheduleTimeout) clearTimeout(warpScheduleTimeout);
            warpGate.active = false;
            hitWarpCooldown = 0;
            
            document.getElementById("blindOverlay").style.display = "none";
            updateUI();
            
            normalFoods = [generateValidPosition()];
            hiddenFruits = [];
            
            scheduleWarpGate();
        }

        function updateUI() {
            document.getElementById("currentScore").innerText = score;
            document.getElementById("heartDisplay").innerText = "❤️".repeat(lives);
            document.getElementById("foodTimerDisplay").innerText = hungerTimer;
            if (!isBonusTime && !isGridTime) document.getElementById("itemEffect").innerText = "";
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
                        if(effectDisplay.innerText.includes("아사") && !isBonusTime && !isGridTime) {
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
            baseSpeed = Math.max(40, 100 - Math.floor(score / 50) * 5);
            updateSpeed();
            
            let targetFoodCount = Math.min(5, 1 + Math.floor(score / 100));
            while(normalFoods.length < targetFoodCount) {
                normalFoods.push(generateValidPosition());
            }
            if (normalFoods.length === 0) normalFoods.push(generateValidPosition());
        }
        
        function scheduleWarpGate() {
            warpScheduleTimeout = setTimeout(() => {
                if(!isGameOver && isStarted && !isPaused) {
                    let portals = generateFarPortals();
                    warpGate.p1 = portals[0];
                    warpGate.p2 = portals[1];
                    warpGate.active = true;
                    
                    warpTimeout = setTimeout(() => {
                        warpGate.active = false;
                        scheduleWarpGate();
                    }, 10000);
                }
            }, Math.random() * 10000 + 10000); 
        }
        
        function generateFarPortals() {
            let p1, p2;
            let isHorizontal = Math.random() < 0.5;
            let maxIdx = (canvas.width / gridSize) - 3; 
            
            while (true) {
                if (isHorizontal) {
                    let leftX = Math.floor(Math.random() * 3) + 1;
                    let rightX = maxIdx - Math.floor(Math.random() * 3);
                    let y1 = Math.floor(Math.random() * (maxIdx - 3)) + 2;
                    let y2 = Math.floor(Math.random() * (maxIdx - 3)) + 2;
                    p1 = { x: leftX * gridSize, y: y1 * gridSize };
                    p2 = { x: rightX * gridSize, y: y2 * gridSize };
                } else {
                    let topY = Math.floor(Math.random() * 3) + 1;
                    let bottomY = maxIdx - Math.floor(Math.random() * 3);
                    let x1 = Math.floor(Math.random() * (maxIdx - 3)) + 2;
                    let x2 = Math.floor(Math.random() * (maxIdx - 3)) + 2;
                    p1 = { x: x1 * gridSize, y: topY * gridSize };
                    p2 = { x: x2 * gridSize, y: bottomY * gridSize };
                }
                
                let overlap = false;
                for (let part of snake) {
                    if ((part.x >= p1.x && part.x < p1.x + 2*gridSize && part.y >= p1.y && part.y < p1.y + 2*gridSize) ||
                        (part.x >= p2.x && part.x < p2.x + 2*gridSize && part.y >= p2.y && part.y < p2.y + 2*gridSize)) {
                        overlap = true; break;
                    }
                }
                if (!overlap) break;
            }
            return [p1, p2];
        }

        function drawScreenWithText(text) {
            clearCanvas(); drawWarpGate(); drawNormalFoods(); drawSnake();
            ctx.fillStyle = "rgba(0, 0, 0, 0.5)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "white"; ctx.font = "bold 50px 'Malgun Gothic'";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(text, canvas.width / 2, canvas.height / 2);
        }

        function drawGrid() {
            ctx.strokeStyle = "rgba(255, 255, 255, 0.15)"; // 눈에 거슬리지 않는 반투명 흰색 선
            ctx.lineWidth = 1;
            for(let x = 0; x <= canvas.width; x += gridSize) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for(let y = 0; y <= canvas.height; y += gridSize) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }
        }

        function main() {
            if (checkCollision()) { handleDeath(); return; }
            clearCanvas(); 
            
            // 🌐 250점 돌파 격자 효과
            if (isGridTime) drawGrid();
            
            // 🌟 보너스 타임 텍스트 배경 효과
            if (isBonusTime) {
                ctx.fillStyle = "rgba(241, 196, 15, 0.1)"; // 옅은 노란색 필터
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.font = "bold 100px 'Malgun Gothic'";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = "rgba(241, 196, 15, 0.4)";
                ctx.fillText("BONUS!", canvas.width / 2, canvas.height / 2);
            }
            
            drawWarpGate(); 
            drawNormalFoods(); 
            drawHiddenFruits(); 
            drawClover();
            drawBonusFoods(); // 보너스 타임 별 먹이 그리기
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
            
            // 보너스, 격자 타임 중 죽었을 때 초기화
            if(bonusTimeTimeout) clearTimeout(bonusTimeTimeout);
            isBonusTime = false;
            bonusFoods = [];
            
            if(gridTimeout) clearTimeout(gridTimeout);
            isGridTime = false;
            
            updateUI();
            
            const headDiffX = 300 - snake[0].x;
            const headDiffY = 300 - snake[0].y;
            snake.forEach(part => { part.x += headDiffX; part.y += headDiffY; });
            dx = 0; dy = -gridSize;
            hitWarpCooldown = 0;
            
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
            if(warpTimeout) clearTimeout(warpTimeout);
            if(warpScheduleTimeout) clearTimeout(warpScheduleTimeout);
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

        function drawClover() {
            if (clover) {
                ctx.font = "20px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
                ctx.fillText("🍀", clover.x + (gridSize / 2), clover.y + (gridSize / 2) + 2);
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
        
        function drawWarpGate() {
            if (!warpGate.active) return;
            ctx.font = "40px Arial";
            ctx.textAlign = "center"; 
            ctx.textBaseline = "middle";
            ctx.fillText("🕳️", warpGate.p1.x + gridSize, warpGate.p1.y + gridSize + 2);
            ctx.fillText("🕳️", warpGate.p2.x + gridSize, warpGate.p2.y + gridSize + 2);
        }
        
        function advanceSnake() { 
            let head = { x: snake[0].x + dx, y: snake[0].y + dy }; 
            
            if (warpGate.active && hitWarpCooldown <= 0) {
                if (head.x >= warpGate.p1.x && head.x < warpGate.p1.x + 2*gridSize &&
                    head.y >= warpGate.p1.y && head.y < warpGate.p1.y + 2*gridSize) {
                    head.x = warpGate.p2.x + (head.x - warpGate.p1.x);
                    head.y = warpGate.p2.y + (head.y - warpGate.p1.y);
                    hitWarpCooldown = 4; 
                } else if (head.x >= warpGate.p2.x && head.x < warpGate.p2.x + 2*gridSize &&
                           head.y >= warpGate.p2.y && head.y < warpGate.p2.y + 2*gridSize) {
                    head.x = warpGate.p1.x + (head.x - warpGate.p2.x);
                    head.y = warpGate.p1.y + (head.y - warpGate.p2.y);
                    hitWarpCooldown = 4;
                }
            }
            if (hitWarpCooldown > 0) hitWarpCooldown--;
            
            snake.unshift(head); 
            
            let hitRange = (snakeSizeMod > 1.2) ? gridSize : 0;
            let ateSomething = false;

            // 🌐 250점 돌파 격자 이벤트! (10초 유지)
            if (score >= 250 && !gridTriggered) {
                gridTriggered = true;
                isGridTime = true;
                
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🌐 250점 달성! 10초간 맵에 격자가 표시됩니다!";
                effectDisplay.style.color = "#3498db";
                
                gridTimeout = setTimeout(() => {
                    isGridTime = false;
                    if (!isGameOver && !isPaused && !isBonusTime) effectDisplay.innerText = "";
                }, 10000); // 10초
            }

            // 🍀 클로버 등장 로직
            if (snake.length >= 35 && !cloverSpawned) {
                cloverSpawned = true;
                let pos = generateValidPosition();
                clover = { x: pos.x, y: pos.y };
                
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = "🍀 행운의 클로버 등장! (2초 후 사라집니다!)"; 
                effectDisplay.style.color = "#2ecc71";

                cloverTimeout = setTimeout(() => {
                    clover = null;
                }, 2000);
            }

            // 🍀 클로버 획득 처리
            if (clover && Math.abs(clover.x - head.x) <= hitRange && Math.abs(clover.y - head.y) <= hitRange) {
                let bonus = Math.floor(Math.random() * 11) * 10 + 50; 
                score += bonus;
                clover = null;
                if (cloverTimeout) clearTimeout(cloverTimeout);
                
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = `🍀 클로버 획득! 잭팟 보너스 +${bonus}점!`; 
                effectDisplay.style.color = "#2ecc71";
                updateGameDifficulty();
                resetHungerTimer();
                ateSomething = true;
            }

            // 🌟 보너스 별 획득 처리
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
            
            // 🌟 500점 단위 돌파 보너스 타임 (스케일링 적용, 10초 유지)
            if (score >= nextBonusScore && !isBonusTime) {
                // 점수 구간에 따라 스폰 개수 증가
                let spawnCount = 40; // 500점 기본
                if (nextBonusScore === 1000) spawnCount = 50;
                else if (nextBonusScore === 1500) spawnCount = 60;
                else if (nextBonusScore >= 2000) spawnCount = 80;
                
                nextBonusScore = Math.floor(score / 500) * 500 + 500; // 다음 목표 점수 갱신
                isBonusTime = true;
                bonusFoods = [];
                
                // 지정된 개수만큼 보너스 먹이 스폰
                for (let i = 0; i < spawnCount; i++) {
                    bonusFoods.push(generateValidPosition());
                }
                
                const effectDisplay = document.getElementById("itemEffect");
                effectDisplay.innerText = `🎉 보너스 타임! 10초간 별이 ${spawnCount}개 쏟아집니다!`; 
                effectDisplay.style.color = "#f1c40f";
                
                bonusTimeTimeout = setTimeout(() => {
                    isBonusTime = false;
                    bonusFoods = [];
                    if (!isGameOver && !isPaused && !isGridTime) {
                        effectDisplay.innerText = "";
                    }
                }, 10000); // 10초
            }
        }

        function applyHiddenFruitEffect(type) {
            const effectDisplay = document.getElementById("itemEffect");
            if (type === 'blind') {
                effectDisplay.innerText = "☁️ 구름! 3초간 눈앞이 캄캄해집니다!"; effectDisplay.style.color = "#7f8c8d";
                document.getElementById("blindOverlay").style.display = "flex";
                if(blindTimeout) clearTimeout(blindTimeout);
                blindTimeout = setTimeout(() => { document.getElementById("blindOverlay").style.display = "none"; if(!isBonusTime && !isGridTime) effectDisplay.innerText = ""; }, 3000);
            
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
                effectDisplay.innerText = "🍄 독버섯! 3초간 방향키가 반대로 조작됩니다!"; effectDisplay.style.color = "#e67e22";
                isReversedControls = true;
                if(controlTimeout) clearTimeout(controlTimeout);
                controlTimeout = setTimeout(() => { isReversedControls = false; if(!isBonusTime && !isGridTime) effectDisplay.innerText = ""; }, 3000);
                
            } else if (type === 'caterpillar') {
                if (Math.random() < 0.5) {
                    effectDisplay.innerText = "🐛 왕꿈틀이! 주변 먹이를 싹쓸이합니다! (5초)"; effectDisplay.style.color = "#2ecc71";
                    snakeSizeMod = 1.6; 
                } else {
                    effectDisplay.innerText = "🐛 꼬마 애벌레! 5초간 몸집이 콩알만해집니다!"; effectDisplay.style.color = "#f1c40f";
                    snakeSizeMod = 0.5; 
                }
                if(sizeTimeout) clearTimeout(sizeTimeout);
                sizeTimeout = setTimeout(() => { snakeSizeMod = 1; if(!isBonusTime && !isGridTime) effectDisplay.innerText = ""; }, 5000);

            } else if (type === 'bonus') {
                score += 50; effectDisplay.innerText = "🍎 보너스 +50점!"; effectDisplay.style.color = "#f1c40f";
            } else if (type === 'slow') {
                effectDisplay.innerText = "🐢 바나나! 느릿느릿~ (5초)"; effectDisplay.style.color = "#3498db";
                speedMod = 1.6; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'fast') {
                effectDisplay.innerText = "⚡ 포도! 아주 빠르게! (5초)"; effectDisplay.style.color = "#9b59b6";
                speedMod = 0.5; updateSpeed();
                setTimeout(() => { if(!isGameOver && !isPaused) { speedMod = 1; updateSpeed(); } if(!isBonusTime && !isGridTime) effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'penalty') {
                score = Math.max(0, score - 30); effectDisplay.innerText = "💀 오렌지! 감점 -30점!"; effectDisplay.style.color = "#e74c3c";
            } else if (type === 'super') {
                score += 100; effectDisplay.innerText = "🍓 딸기! 슈퍼 보너스 +100점!"; effectDisplay.style.color = "#ff7675";
            }
            
            updateGameDifficulty(); 
            setTimeout(() => { if(!['slow','fast','blind','reverse','caterpillar'].includes(type) && !isBonusTime && !isGridTime) effectDisplay.innerText = ""; }, 2500);
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
            for (let i = 0; i < snake.length; i++) { if (snake[i].x === head.x && snake[i].y === head.y) return true; } 
            return head.x < 0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height; 
        }

        window.addEventListener("keydown", function(e) {
            if (e.keyCode === 32 && !isStarted && !isCountingDown) { e.preventDefault(); triggerStart(); return; }
            
            // ⏸️ 일시정지 로직 (P 키)
            if (e.keyCode === 80) {
                if (isCountingDown || isGameOver || !isStarted) return;
                
                if (!isPaused && !pauseUsed) {
                    isPaused = true;
                    pauseUsed = true; // 게임당 1회 제한
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
                    ctx.fillText("[P] 키를 다시 누르면 재개됩니다.", canvas.width / 2, canvas.height / 2 + 30);
                    ctx.fillText("(일시정지는 한 게임당 딱 한 번만 가능!)", canvas.width / 2, canvas.height / 2 + 60);
                } else if (isPaused) {
                    isPaused = false;
                    updateSpeed();
                    resumeHungerTimer();
                }
                return;
            }

            if (isCountingDown || isGameOver || isPaused) return;
            if([37, 38, 39, 40, 32, 80].indexOf(e.keyCode) > -1) e.preventDefault(); 
            
            let LEFT = 37, UP = 38, RIGHT = 39, DOWN = 40;
            
            if (isReversedControls) {
                LEFT = 39; RIGHT = 37; UP = 40; DOWN = 38;
            }
            
            if (e.keyCode === LEFT && dx === 0) { dx = -gridSize; dy = 0; }
            if (e.keyCode === UP && dy === 0) { dx = 0; dy = -gridSize; }
            if (e.keyCode === RIGHT && dx === 0) { dx = gridSize; dy = 0; }
            if (e.keyCode === DOWN && dy === 0) { dx = 0; dy = gridSize; }
        }, false);
    </script>
</body>
</html>
"""

# -------------------------------------------------------------
# 파일 폴더 생성 및 컴포넌트 선언 (캐시 방지 v24)
# -------------------------------------------------------------
component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_v24")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(GAME_HTML)

snake_game = components.declare_component("snake_v24", path=component_dir)

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
st.title("  🐍 TJ Random Speed Rush 🎮  ")
st.info("  🏆 최고의 점수에 도전해봅시다! 일시정지 [P]키 1번 가능! 게임가이드 보고 시작해보기‼  ")

col_empty, col1, col2 = st.columns([0.1, 2.1, 1.8])

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
            * **조작 방법**: 키보드 방향키 (⬅️ ⬆️ ➡️ ⬇️)
            * **게임 시작/부활**: 닉네임 입력 후 `[Space Bar]` 입력
            * **일시정지**: 게임 중 위급할 때 **`[P]` 키**를 누르면 일시정지됩니다. (단, 1게임당 **딱 1번만** 사용 가능!)
            * **난이도 상승 (Speed Rush!)**: 
              * 점수가 **50점** 오를 때마다 **속도가 점점 빨라집니다.**
              * 점수가 **100점** 오를 때마다 기본 먹이 개수가 증가합니다. (최대 5개)
            * **목숨(하트) 시스템**: 총 **3개(❤️❤️❤️)**의 목숨이 주어집니다.
              * 충돌 시 점수 감점 없이 **몸통만 3칸 줄어든 채** 중앙에서 부활합니다.
            * 🕳️ **대형 블랙홀(워프 게이트)**: 10~20초 주기로 맵 **상하/좌우 양끝단**에 대형 2x2 사이즈 블랙홀 2개가 열립니다. 쏙 들어가면 맵 반대편으로 순간이동하는 지름길입니다!
            * 🌐 **250점 격자 버프!**: 250점을 돌파하면 **10초간** 맵에 길을 찾기 쉽게 도와주는 반투명 격자가 나타납니다.
            * 🎉 **500점 돌파 피버 타임!**: 점수가 500단위에 도달하면 **10초간** 맵에 ⭐️(보너스 별)이 가득 차오르는 피버 타임이 발동합니다! (고득점일수록 별 개수 증가!)
            """)
            
        with tab2:
            st.markdown("""
            **물음표(❓) 상자** 안에는 아래 아이템 중 하나가 숨겨져 있습니다. (클로버 제외)
            
            | 아이템 | 효과 설명 |
            | :--- | :--- |
            | 🍀 **클로버** | ❓상자가 아닌, 몸통이 **35칸**이 될 때만 딱 한 번 나타납니다! (50~150점 랜덤 획득, **2초 후 소멸**) |
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

    st.subheader("🏆 실시간 TOP 10")
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


# -------------------------------------------------------------
# 🛠️ 관리자 도구 (비밀번호: 880610)
# -------------------------------------------------------------
st.sidebar.title("🛠️ 관리자 도구")
admin_password = st.sidebar.text_input("관리자 비밀번호를 입력하세요", type="password")

if admin_password == "880610":
    st.sidebar.success("✅ 관리자 인증 완료!")
    if st.sidebar.button("🚨 랭킹 데이터 전체 초기화"):
        if os.path.exists(SCORE_FILE):
            os.remove(SCORE_FILE)
            st.sidebar.success("데이터가 성공적으로 삭제되었습니다.")
            time.sleep(1)
            st.rerun()
        else:
            st.sidebar.info("삭제할 랭킹 데이터가 없습니다.")
elif admin_password != "":
    st.sidebar.error("❌ 비밀번호가 틀렸습니다.")
