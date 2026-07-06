import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time

# 페이지 설정
st.set_page_config(page_title="TJ 꿈틀꿈틀", page_icon="🐍", layout="wide")

# -------------------------------------------------------------
# 🎮 [HTML/JS 게임 엔진 생성]
# -------------------------------------------------------------
GAME_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        body { display: flex; flex-direction: column; align-items: center; background-color: #2c3e50; color: white; font-family: 'Malgun Gothic', sans-serif; margin: 0; padding: 10px; height: 850px; overflow: hidden; }
        .canvas-container { position: relative; width: 550px; height: 550px; }
        canvas { background-color: #34495e; border: 3px solid #ecf0f1; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
        /* ☁️ 구름 아이템 암흑 효과 오버레이 */
        #blindOverlay { position: absolute; top: 3px; left: 3px; width: 550px; height: 550px; background-color: rgba(10, 15, 25, 0.98); display: none; pointer-events: none; justify-content: center; align-items: center; font-size: 30px; font-weight: bold; color: #7f8c8d; }
        .ui-container { display: flex; gap: 20px; margin-bottom: 10px; align-items: center; }
        .setup-container, .restart-container { margin-bottom: 20px; display: flex; gap: 10px; justify-content: center;}
        input { padding: 10px; font-size: 16px; border-radius: 5px; text-align: center; border: 1px solid #bdc3c7;}
        button { padding: 10px 20px; font-size: 16px; font-weight: bold; background-color: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #c0392b; }
        #scoreBoard, #livesBoard { font-size: 22px; font-weight: bold; }
        #livesBoard { color: #ff7675; }
        #itemEffect { font-size: 18px; color: #f1c40f; height: 24px; margin-bottom: 10px; font-weight: bold; }
        .info-text { font-size: 12px; color: #bdc3c7; margin-top: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="setup-container" id="setupContainer">
        <input type="text" id="nicknameInput" placeholder="닉네임 (최대10자)" maxlength="10">
        <button id="startBtn">게임 시작 (Space)</button>
    </div>

    <div class="restart-container" id="restartContainer" style="display: none;">
        <button id="restartBtn" style="background-color: #3498db;">🔄 다시 도전 (Space)</button>
    </div>

    <div class="ui-container">
        <div id="scoreBoard">점수: <span id="currentScore">0</span></div>
        <div id="livesBoard">목숨: <span id="heartDisplay">❤️❤️❤️</span></div>
    </div>
    <div id="itemEffect"></div>
    
    <div class="canvas-container">
        <canvas id="gameCanvas" width="550" height="550"></canvas>
        <div id="blindOverlay">👁️ 암흑 상태 (앞이 보이지 않습니다!)</div>
    </div>
    <div class="info-text">[Space Bar]를 눌러 게임을 시작하거나 다시 도전할 수 있습니다.</div>

    <script>
        function sendToStreamlit(type, data) {
            const msg = { isStreamlitMessage: true, type: type };
            if (data) Object.assign(msg, data);
            window.parent.postMessage(msg, "*");
        }

        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const gridSize = 20;
        
        let snake, normalFood, hiddenFruit;
        let dx, dy, score, nickname, gameInterval, lives, initialLength;
        let isCountingDown = false, isGameOver = false, isStarted = false, currentSpeed = 100;
        let blindTimeout = null;

        function initGame() {
            // 550 크기에 맞게 중앙 위치 조정 (20의 배수인 260)
            snake = [{ x: 260, y: 260 }]; dx = 0; dy = -gridSize;
            score = 0; lives = 3; currentSpeed = 100; isGameOver = false;
            document.getElementById("blindOverlay").style.display = "none";
            updateUI();
            normalFood = generateValidPosition();
            hiddenFruit = { active: false, x: 0, y: 0, type: '' };
        }

        function updateUI() {
            document.getElementById("currentScore").innerText = score;
            document.getElementById("heartDisplay").innerText = "❤️".repeat(lives);
            document.getElementById("itemEffect").innerText = "";
        }

        document.getElementById("startBtn").addEventListener("click", triggerStart);
        document.getElementById("restartBtn").addEventListener("click", triggerStart);

        function triggerStart() {
            nickname = document.getElementById("nicknameInput").value.trim() || "지렁이";
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
                    setGameSpeed(currentSpeed);
                }
            }, 800);
        }

        function setGameSpeed(speed) {
            if(gameInterval) clearInterval(gameInterval);
            gameInterval = setInterval(main, speed);
        }

        function drawScreenWithText(text) {
            clearCanvas(); drawNormalFood(); drawSnake();
            ctx.fillStyle = "rgba(0, 0, 0, 0.5)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "white"; ctx.font = "bold 50px 'Malgun Gothic'";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(text, canvas.width / 2, canvas.height / 2);
        }

        function main() {
            if (checkCollision()) {
                handleDeath();
                return;
            }
            clearCanvas(); drawNormalFood(); drawHiddenFruit(); advanceSnake(); drawSnake();
        }

        // 💀 죽었을 때 목숨별 점수 차감 및 몸통 단축 처리
        function handleDeath() {
            lives--;
            if (lives === 2) {
                // 첫 번째 죽음: -30점 감점, 몸통 5개 감소
                score = Math.max(0, score - 30);
                reduceSnakeBody(5);
                alert(`앗! 첫 번째 충돌! (-30점 감점 및 몸통 5칸 축소)`);
                resetSnakePosition();
            } else if (lives === 1) {
                // 두 번째 죽음: -50점 감점, 몸통 5개 감소
                score = Math.max(0, score - 50);
                reduceSnakeBody(5);
                alert(`위험합니다! 두 번째 충돌! (-50점 감점 및 몸통 5칸 축소)`);
                resetSnakePosition();
            } else if (lives <= 0) {
                // 마지막 죽음: -20점 감점 후 게임 종료
                score = Math.max(0, score - 20);
                updateUI();
                endGame();
            }
        }

        function reduceSnakeBody(count) {
            // 몸통이 다 사라져 죽는 현상 방지를 위해 최소 머리(1칸)는 남겨둠
            if (snake.length > count) {
                snake = snake.slice(0, snake.length - count);
            } else {
                snake = [snake[0]];
            }
        }

        function resetSnakePosition() {
            clearInterval(gameInterval);
            document.getElementById("blindOverlay").style.display = "none";
            updateUI();
            // 부딪힌 자리에서 머리 좌표만 중앙으로 이동하고, 현재 줄어든 몸통 형태 유지
            const headDiffX = 260 - snake[0].x;
            const headDiffY = 260 - snake[0].y;
            snake.forEach(part => {
                part.x += headDiffX;
                part.y += headDiffY;
            });
            dx = 0; dy = -gridSize;
            setTimeout(() => { if(!isGameOver) setGameSpeed(currentSpeed); }, 1000);
        }

        function endGame() {
            clearInterval(gameInterval); isGameOver = true; isStarted = false;
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
                ctx.fillStyle = (index === 0) ? "#27ae60" : "#2ecc71"; 
                ctx.fillRect(part.x, part.y, gridSize-1, gridSize-1); 
            }); 
        }
        function drawNormalFood() { ctx.fillStyle = "#e74c3c"; ctx.fillRect(normalFood.x, normalFood.y, gridSize, gridSize); }
        
        function drawHiddenFruit() {
            if (!hiddenFruit.active) return;
            ctx.font = "18px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(hiddenFruit.emoji, hiddenFruit.x + (gridSize / 2), hiddenFruit.y + (gridSize / 2));
        }
        
        function advanceSnake() { 
            const head = { x: snake[0].x + dx, y: snake[0].y + dy }; 
            snake.unshift(head); 
            
            let ateNormal = (head.x === normalFood.x && head.y === normalFood.y);
            let ateHidden = (hiddenFruit.active && head.x === hiddenFruit.x && head.y === hiddenFruit.y);

            if (ateNormal) { 
                score += 10; document.getElementById("currentScore").innerText = score; 
                normalFood = generateValidPosition(); 
                if (!hiddenFruit.active && Math.random() < 0.4) spawnHiddenFruit();
            } else if (ateHidden) {
                hiddenFruit.active = false; applyHiddenFruitEffect(hiddenFruit.type);
            } else { snake.pop(); } 
        }

        function applyHiddenFruitEffect(type) {
            const effectDisplay = document.getElementById("itemEffect");
            if (type === 'blind') {
                effectDisplay.innerText = "☁️ 구름! 2초간 눈앞이 캄캄해집니다!"; effectDisplay.style.color = "#7f8c8d";
                document.getElementById("blindOverlay").style.display = "flex";
                if(blindTimeout) clearTimeout(blindTimeout);
                blindTimeout = setTimeout(() => { document.getElementById("blindOverlay").style.display = "none"; effectDisplay.innerText = ""; }, 2000);
            } else if (type === 'bonus') {
                score += 50; effectDisplay.innerText = "🍎 보너스 +50점!"; effectDisplay.style.color = "#f1c40f";
            } else if (type === 'slow') {
                effectDisplay.innerText = "🐢 바나나! 느릿느릿~ (5초)"; effectDisplay.style.color = "#3498db";
                setGameSpeed(160);
                setTimeout(() => { if(!isGameOver) setGameSpeed(currentSpeed); effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'fast') {
                effectDisplay.innerText = "⚡ 포도! 아주 빠르게! (5초)"; effectDisplay.style.color = "#9b59b6";
                setGameSpeed(50);
                setTimeout(() => { if(!isGameOver) setGameSpeed(currentSpeed); effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'penalty') {
                score = Math.max(0, score - 30); effectDisplay.innerText = "💀 오렌지! 감점 -30점!"; effectDisplay.style.color = "#e67e22";
            } else if (type === 'super') {
                score += 100; effectDisplay.innerText = "🍓 딸기! 슈퍼 보너스 +100점!"; effectDisplay.style.color = "#ff7675";
            }
            document.getElementById("currentScore").innerText = score;
            setTimeout(() => { if(!['slow','fast','blind'].includes(type)) effectDisplay.innerText = ""; }, 2000);
        }

        function spawnHiddenFruit() {
            hiddenFruit.active = true;
            let pos = generateValidPosition();
            hiddenFruit.x = pos.x; hiddenFruit.y = pos.y;
            const rand = Math.random();
            // 구름 아이템(blind) 확률 배정
            if (rand < 0.2) { hiddenFruit.emoji = '☁️'; hiddenFruit.type = 'blind'; }
            else if (rand < 0.4) { hiddenFruit.emoji = '🍎'; hiddenFruit.type = 'bonus'; }
            else if (rand < 0.55) { hiddenFruit.emoji = '🍌'; hiddenFruit.type = 'slow'; }
            else if (rand < 0.7) { hiddenFruit.emoji = '🍇'; hiddenFruit.type = 'fast'; }
            else if (rand < 0.85) { hiddenFruit.emoji = '🍊'; hiddenFruit.type = 'penalty'; }
            else { hiddenFruit.emoji = '🍓'; hiddenFruit.type = 'super'; }
            setTimeout(() => { hiddenFruit.active = false; }, 6000);
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
            if (e.keyCode === 32 && !isStarted && !isCountingDown) {
                e.preventDefault();
                triggerStart();
                return;
            }

            if (isCountingDown || isGameOver) return;
            if([37, 38, 39, 40, 32].indexOf(e.keyCode) > -1) e.preventDefault(); 
            
            const LEFT = 37, UP = 38, RIGHT = 39, DOWN = 40;
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
    existing_user = next((item for item in scores if item["nickname"] == nickname), None)
    
    if existing_user:
        if score > existing_user["score"]:
            existing_user["score"] = score
    else:
        scores.append({"nickname": nickname, "score": score})
    
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)

# 컴포넌트 폴더 준비
component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_v4")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(GAME_HTML)

snake_game = components.declare_component("snake_v4", path=component_dir)

# -------------------------------------------------------------
# 🏁 스트림릿 메인 화면 레이아웃
# -------------------------------------------------------------
st.title("🐍 TJ 꿈틀꿈틀 랭킹전 🎮")
st.info("방향키로 조종하세요! 벽이나 몸에 부딪히면 목숨별로 점수가 차감되며 몸통이 5칸 줄어듭니다. 구름(☁️) 아이템을 조심하세요!")

col1, col2 = st.columns([3, 1])

with col1:
    # 확장된 해상도에 맞춰 넉넉하게 콤포넌트 출력 높이를 850으로 조정
    result = snake_game(height=850)
    if result:
        nickname = result.get("nickname")
        score = result.get("score")
        ts = result.get("timestamp")
        
        if "last_ts" not in st.session_state or st.session_state["last_ts"] != ts:
            save_score(nickname, score)
            st.session_state["last_ts"] = ts
            st.success(f"🎉 {nickname}님! {score}점 기록 완료!")
            st.rerun()

with col2:
    st.subheader("🏆 실시간 TOP 10")
    scores = load_scores()
    if not scores:
        st.write("첫 기록을 남겨보세요!")
    else:
        for i, s in enumerate(scores):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}위"
            st.markdown(f"**{medal} | {s['nickname']}**")
            st.caption(f"Score: {s['score']} pts")
            st.divider()

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
