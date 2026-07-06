import streamlit as st
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title="꿈틀꿈틀", page_icon="🐍", layout="wide")
st.title("🐍 TJ 꿈틀꿈틀 랭킹전!")
st.write("히든 아이템(과일)을 먹고 최고 점수를 노려보세요!")

# -------------------------------------------------------------
# 🌟 [오프라인 자체 생성 시스템]
# 외부 링크(CDN)를 완전히 제거하고, 자체 통신 기능이 내장된 HTML을 파이썬이 직접 만듭니다.
# -------------------------------------------------------------
GAME_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { display: flex; flex-direction: column; align-items: center; background-color: #2c3e50; color: white; font-family: 'Malgun Gothic', sans-serif; margin: 0; padding: 10px; height: 680px; overflow: hidden; }
        canvas { background-color: #34495e; border: 3px solid #ecf0f1; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
        .setup-container, .restart-container { margin-bottom: 20px; display: flex; gap: 10px; justify-content: center;}
        input { padding: 10px; font-size: 16px; border-radius: 5px; text-align: center; border: 1px solid #bdc3c7;}
        button { padding: 10px 20px; font-size: 16px; font-weight: bold; background-color: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #c0392b; }
        #scoreBoard { font-size: 20px; font-weight: bold; margin-bottom: 10px; }
        #itemEffect { font-size: 16px; color: #f1c40f; height: 20px; margin-bottom: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="setup-container" id="setupContainer">
        <input type="text" id="nicknameInput" placeholder="닉네임 (최대10자)" maxlength="10">
        <button id="startBtn">게임 시작</button>
    </div>

    <div class="restart-container" id="restartContainer" style="display: none;">
        <button id="restartBtn" style="background-color: #3498db;">🔄 다시 하기</button>
    </div>

    <div id="scoreBoard">현재 점수: <span id="currentScore">0</span></div>
    <div id="itemEffect"></div>
    <canvas id="gameCanvas" width="400" height="400"></canvas>

    <script>
        // 🌟 외부 파일(CDN) 차단 문제 완벽 해결: 스트림릿과 직접 통신하는 자체 함수
        function sendToStreamlit(type, data) {
            const msg = { isStreamlitMessage: true, type: type };
            if (data) Object.assign(msg, data);
            window.parent.postMessage(msg, "*");
        }
        function setHeight() { sendToStreamlit("streamlit:setFrameHeight", { height: 680 }); }

        window.addEventListener("load", function() {
            sendToStreamlit("streamlit:componentReady", { apiVersion: 1 });
            setHeight();
        });
        window.addEventListener("message", function(event) {
            if (event.data && event.data.type === "streamlit:render") setHeight();
        });

        // --- 여기서부터 게임 로직 ---
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const gridSize = 20;
        
        let snake, normalFood, hiddenFruit;
        let dx, dy, score, nickname, gameInterval;
        let isCountingDown = false, isGameOver = false, currentSpeed = 100;

        function initGame() {
            snake = [{ x: 200, y: 200 }]; dx = 0; dy = -gridSize;
            score = 0; currentSpeed = 100; isGameOver = false;
            document.getElementById("currentScore").innerText = score;
            document.getElementById("itemEffect").innerText = "";
            normalFood = generateValidPosition();
            hiddenFruit = { active: false, x: 0, y: 0, type: '' };
        }

        document.getElementById("startBtn").addEventListener("click", function() {
            nickname = document.getElementById("nicknameInput").value.trim() || "지렁이";
            document.getElementById("setupContainer").style.display = "none";
            startGameSequence();
        });

        document.getElementById("restartBtn").addEventListener("click", function() {
            document.getElementById("restartContainer").style.display = "none";
            startGameSequence();
        });

        function startGameSequence() { initGame(); startCountdown(); }

        function startCountdown() {
            isCountingDown = true;
            let count = 3; drawScreenWithText(count);
            let countInterval = setInterval(() => {
                count--;
                if (count > 0) drawScreenWithText(count);
                else if (count === 0) drawScreenWithText("시작!");
                else {
                    clearInterval(countInterval); isCountingDown = false;
                    setGameSpeed(currentSpeed);
                }
            }, 1000);
        }

        function setGameSpeed(speed) {
            if(gameInterval) clearInterval(gameInterval);
            gameInterval = setInterval(main, speed);
        }

        function drawScreenWithText(text) {
            clearCanvas(); drawNormalFood(); drawSnake();
            ctx.fillStyle = "rgba(0, 0, 0, 0.5)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "white"; ctx.font = "bold 60px 'Malgun Gothic'";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(text, canvas.width / 2, canvas.height / 2);
        }

        function main() {
            if (hasGameEnded()) {
                clearInterval(gameInterval); isGameOver = true;
                document.getElementById("restartContainer").style.display = "flex";
                alert(`게임 오버!\\n${nickname}님의 최종 점수: ${score}점\\n랭킹에 자동 등록됩니다!`);
                
                // 🌟 자체 통신망을 통해 파이썬으로 랭킹 점수 쏘기!
                sendToStreamlit("streamlit:setComponentValue", { 
                    value: { nickname: nickname, score: score, timestamp: Date.now() } 
                });
                return;
            }
            clearCanvas(); drawNormalFood(); drawHiddenFruit(); advanceSnake(); drawSnake();
        }

        function clearCanvas() { ctx.fillStyle = "#34495e"; ctx.fillRect(0, 0, canvas.width, canvas.height); }
        function drawSnake() { ctx.fillStyle = "#2ecc71"; ctx.strokeStyle = "#27ae60"; snake.forEach(part => { ctx.fillRect(part.x, part.y, gridSize, gridSize); ctx.strokeRect(part.x, part.y, gridSize, gridSize); }); }
        function drawNormalFood() { ctx.fillStyle = "#e74c3c"; ctx.fillRect(normalFood.x, normalFood.y, gridSize, gridSize); }
        
        function drawHiddenFruit() {
            if (!hiddenFruit.active) return;
            ctx.font = "18px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(hiddenFruit.emoji, hiddenFruit.x + (gridSize / 2), hiddenFruit.y + (gridSize / 2) + 2);
        }
        
        function advanceSnake() { 
            const head = { x: snake[0].x + dx, y: snake[0].y + dy }; 
            snake.unshift(head); 
            
            let ateNormal = (head.x === normalFood.x && head.y === normalFood.y);
            let ateHidden = (hiddenFruit.active && head.x === hiddenFruit.x && head.y === hiddenFruit.y);

            if (ateNormal) { 
                score += 10; document.getElementById("currentScore").innerText = score; 
                normalFood = generateValidPosition(); 
                if (!hiddenFruit.active && Math.random() < 0.3) spawnHiddenFruit();
            } else if (ateHidden) {
                hiddenFruit.active = false; applyHiddenFruitEffect(hiddenFruit.type);
            } else { snake.pop(); } 
        }

        function applyHiddenFruitEffect(type) {
            const effectDisplay = document.getElementById("itemEffect");
            if (type === 'bonus') {
                score += 50; document.getElementById("currentScore").innerText = score; 
                effectDisplay.innerText = "🍎 대박! 보너스 50점!"; effectDisplay.style.color = "#f1c40f";
            } else if (type === 'slow') {
                effectDisplay.innerText = "🐢 바나나! 속도가 5초간 느려집니다!"; effectDisplay.style.color = "#3498db";
                setGameSpeed(180);
                setTimeout(() => { if(!isGameOver) setGameSpeed(100); effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'fast') {
                effectDisplay.innerText = "⚡ 포도! 속도가 5초간 빨라집니다!"; effectDisplay.style.color = "#e74c3c";
                setGameSpeed(50);
                setTimeout(() => { if(!isGameOver) setGameSpeed(100); effectDisplay.innerText = ""; }, 5000);
            }
            setTimeout(() => { if(type === 'bonus') effectDisplay.innerText = ""; }, 2000);
        }

        function spawnHiddenFruit() {
            hiddenFruit.active = true;
            let pos = generateValidPosition();
            hiddenFruit.x = pos.x; hiddenFruit.y = pos.y;
            const rand = Math.floor(Math.random() * 3);
            if (rand === 0) { hiddenFruit.emoji = '🍎'; hiddenFruit.type = 'bonus'; }
            else if (rand === 1) { hiddenFruit.emoji = '🍌'; hiddenFruit.type = 'slow'; }
            else { hiddenFruit.emoji = '🍇'; hiddenFruit.type = 'fast'; }
            setTimeout(() => { hiddenFruit.active = false; }, 6000);
        }
        
        function generateValidPosition() {
            let newPos;
            while (true) {
                newPos = { x: Math.round((Math.random() * (canvas.width - gridSize)) / gridSize) * gridSize, y: Math.round((Math.random() * (canvas.height - gridSize)) / gridSize) * gridSize };
                if (!snake.some(part => part.x === newPos.x && part.y === newPos.y)) break;
            }
            return newPos;
        }
        
        function hasGameEnded() { 
            for (let i = 4; i < snake.length; i++) { if (snake[i].x === snake[0].x && snake[i].y === snake[0].y) return true; } 
            return snake[0].x < 0 || snake[0].x >= canvas.width || snake[0].y < 0 || snake[0].y >= canvas.height; 
        }

        window.addEventListener("keydown", function(e) {
            if (isCountingDown || isGameOver) return;
            if([37, 38, 39, 40].indexOf(e.keyCode) > -1) { e.preventDefault(); }
            const LEFT = 37, RIGHT = 39, UP = 38, DOWN = 40;
            if (e.keyCode === LEFT && dx === 0) { dx = -gridSize; dy = 0; }
            if (e.keyCode === UP && dy === 0) { dx = 0; dy = -gridSize; }
            if (e.keyCode === RIGHT && dx === 0) { dx = gridSize; dy = 0; }
            if (e.keyCode === DOWN && dy === 0) { dx = 0; dy = gridSize; }
        }, false);
    </script>
</body>
</html>
"""

# 폴더 생성 및 저장
current_dir = os.path.dirname(os.path.abspath(__file__))
component_dir = os.path.join(current_dir, "snake_offline_v1")
os.makedirs(component_dir, exist_ok=True)
html_path = os.path.join(component_dir, "index.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(GAME_HTML)

# 오프라인 모드 컴포넌트 선언
snake_game_component = components.declare_component("snake_offline_v1", path=component_dir)

# -------------------------------------------------------------
# 랭킹 시스템
# -------------------------------------------------------------
SCORE_FILE = "scores.json"

def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_score(nickname, score):
    scores = load_scores()
    scores.append({"nickname": nickname, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)

# -------------------------------------------------------------
# 레이아웃 
# -------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎮 게임 플레이")
    
    # 여기서 게임이 무조건 열립니다!
    game_result = snake_game_component()
    
    if game_result:
        nickname = game_result.get("nickname")
        score = game_result.get("score")
        timestamp = game_result.get("timestamp")
        
        if "last_timestamp" not in st.session_state or st.session_state["last_timestamp"] != timestamp:
            save_score(nickname, score)
            st.session_state["last_timestamp"] = timestamp
            st.toast(f"🎉 {nickname}님의 {score}점 랭킹 등록 완료!")
            st.rerun()

with col2:
    st.subheader("🏆 명예의 전당 (Top 10)")
    scores = load_scores()
    
    if not scores:
        st.info("아직 기록이 없습니다. 첫 1위의 주인공이 되어보세요!")
    else:
        for i, s in enumerate(scores):
            if i == 0: medal = "🥇"
            elif i == 1: medal = "🥈"
            elif i == 2: medal = "🥉"
            else: medal = f"🏅 {i+1}위"
            
            st.markdown(f"**{medal} | {s['nickname']}** : {s['score']}점")
            st.divider()
