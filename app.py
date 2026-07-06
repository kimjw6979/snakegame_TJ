import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
import datetime

# 페이지 설정
st.set_page_config(page_title="꿈틀꿈틀", page_icon="🐍", layout="wide")

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
    </div>
    <div id="itemEffect"></div>
    
    <div class="canvas-container">
        <canvas id="gameCanvas" width="600" height="600"></canvas>
        <div id="blindOverlay">👁️ 암흑 상태 (앞이 보이지 않습니다!)</div>
    </div>
    <div class="info-text">[Space Bar]를 눌러 게임을 시작하거나 다시 도전할 수 있습니다.</div>

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
        
        // 🌟 스피드 및 방향키 제어 변수
        let baseSpeed = 100;
        let speedMod = 1;
        let isReversedControls = false;
        
        let blindTimeout = null;
        let controlTimeout = null;

        function initGame() {
            snake = [{ x: 300, y: 300 }]; dx = 0; dy = -gridSize;
            score = 0; lives = 3; isGameOver = false;
            baseSpeed = 100; speedMod = 1; isReversedControls = false;
            document.getElementById("blindOverlay").style.display = "none";
            updateUI();
            
            // 일반 먹이는 배열로 관리 (시작은 1개)
            normalFoods = [generateValidPosition()];
            // 히든 아이템은 최대 3개까지 배열로 유지
            hiddenFruits = [];
        }

        function updateUI() {
            document.getElementById("currentScore").innerText = score;
            document.getElementById("heartDisplay").innerText = "❤️".repeat(lives);
            document.getElementById("itemEffect").innerText = "";
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
                }
            }, 800);
        }

        // 🌟 스피드 통합 제어 함수 (점수에 따른 기본 속도 + 아이템 배속)
        function updateSpeed() {
            if(gameInterval) clearInterval(gameInterval);
            gameInterval = setInterval(main, baseSpeed * speedMod);
        }

        // 🌟 점수에 비례하여 난이도(속도/먹이 수)를 올리는 로직
        function updateGameDifficulty() {
            document.getElementById("currentScore").innerText = score;
            
            // 속도 증가: 50점마다 간격을 5ms씩 줄임 (최대 40ms까지)
            baseSpeed = Math.max(40, 100 - Math.floor(score / 50) * 5);
            updateSpeed();
            
            // 일반 먹이 개수 증가: 100점마다 1개씩 추가 (최대 5개)
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

        function main() {
            if (checkCollision()) { handleDeath(); return; }
            clearCanvas(); drawNormalFoods(); drawHiddenFruits(); advanceSnake(); drawSnake();
        }

        function handleDeath() {
            lives--;
            if (lives === 2) {
                score = Math.max(0, score - 30); reduceSnakeBody(5);
                alert(`앗! 첫 번째 충돌! (-30점 감점 및 몸통 5칸 축소)`); resetSnakePosition();
            } else if (lives === 1) {
                score = Math.max(0, score - 50); reduceSnakeBody(5);
                alert(`위험합니다! 두 번째 충돌! (-50점 감점 및 몸통 5칸 축소)`); resetSnakePosition();
            } else if (lives <= 0) {
                score = Math.max(0, score - 20); updateUI(); endGame();
            }
        }

        function reduceSnakeBody(count) {
            if (snake.length > count) { snake = snake.slice(0, snake.length - count); } 
            else { snake = [snake[0]]; }
        }

        function resetSnakePosition() {
            clearInterval(gameInterval);
            document.getElementById("blindOverlay").style.display = "none";
            isReversedControls = false; // 죽으면 조작 반전 초기화
            updateUI();
            
            const headDiffX = 300 - snake[0].x;
            const headDiffY = 300 - snake[0].y;
            snake.forEach(part => { part.x += headDiffX; part.y += headDiffY; });
            dx = 0; dy = -gridSize;
            
            setTimeout(() => { if(!isGameOver) updateSpeed(); }, 1000);
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
                // 독버섯 상태일 땐 지렁이 머리 색상이 경고색으로 변함
                if (index === 0) ctx.fillStyle = isReversedControls ? "#e74c3c" : "#27ae60"; 
                else ctx.fillStyle = isReversedControls ? "#c0392b" : "#2ecc71";
                ctx.fillRect(part.x, part.y, gridSize-1, gridSize-1); 
            }); 
        }
        function drawNormalFoods() { 
            ctx.fillStyle = "#e74c3c"; 
            normalFoods.forEach(food => ctx.fillRect(food.x, food.y, gridSize, gridSize)); 
        }
        
        function drawHiddenFruits() {
            ctx.font = "18px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
            hiddenFruits.forEach(fruit => {
                ctx.fillText(fruit.emoji, fruit.x + (gridSize / 2), fruit.y + (gridSize / 2));
            });
        }
        
        function advanceSnake() { 
            const head = { x: snake[0].x + dx, y: snake[0].y + dy }; 
            snake.unshift(head); 
            
            // 일반 먹이 충돌 체크
            let ateNormalIndex = normalFoods.findIndex(f => f.x === head.x && f.y === head.y);
            // 아이템 충돌 체크
            let ateHiddenIndex = hiddenFruits.findIndex(f => f.x === head.x && f.y === head.y);

            if (ateNormalIndex !== -1) { 
                score += 10; 
                normalFoods.splice(ateNormalIndex, 1);
                updateGameDifficulty(); // 점수에 따른 속도/먹이 증가 업데이트
                
                // 아이템은 최대 3개까지 유지되며 스폰 확률 부여
                if (hiddenFruits.length < 3 && Math.random() < 0.4) spawnHiddenFruit();
            } else if (ateHiddenIndex !== -1) {
                let fruit = hiddenFruits.splice(ateHiddenIndex, 1)[0];
                applyHiddenFruitEffect(fruit.type);
            } else { 
                snake.pop(); 
            } 
        }

        function applyHiddenFruitEffect(type) {
            const effectDisplay = document.getElementById("itemEffect");
            if (type === 'blind') {
                effectDisplay.innerText = "☁️ 구름! 2초간 눈앞이 캄캄해집니다!"; effectDisplay.style.color = "#7f8c8d";
                document.getElementById("blindOverlay").style.display = "flex";
                if(blindTimeout) clearTimeout(blindTimeout);
                blindTimeout = setTimeout(() => { document.getElementById("blindOverlay").style.display = "none"; effectDisplay.innerText = ""; }, 2000);
            
            // 🌟 터널 (이동 방향 즉시 반전)
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
            
            // 🌟 독버섯 (방향키 반전)
            } else if (type === 'reverse') {
                effectDisplay.innerText = "🍄 독버섯! 5초간 방향키가 반대로 조작됩니다!"; effectDisplay.style.color = "#e67e22";
                isReversedControls = true;
                if(controlTimeout) clearTimeout(controlTimeout);
                controlTimeout = setTimeout(() => { isReversedControls = false; effectDisplay.innerText = ""; }, 5000);
                
            } else if (type === 'bonus') {
                score += 50; effectDisplay.innerText = "🍎 보너스 +50점!"; effectDisplay.style.color = "#f1c40f";
            } else if (type === 'slow') {
                effectDisplay.innerText = "🐢 바나나! 느릿느릿~ (5초)"; effectDisplay.style.color = "#3498db";
                speedMod = 1.6; updateSpeed();
                setTimeout(() => { if(!isGameOver) { speedMod = 1; updateSpeed(); } effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'fast') {
                effectDisplay.innerText = "⚡ 포도! 아주 빠르게! (5초)"; effectDisplay.style.color = "#9b59b6";
                speedMod = 0.5; updateSpeed();
                setTimeout(() => { if(!isGameOver) { speedMod = 1; updateSpeed(); } effectDisplay.innerText = ""; }, 5000);
            } else if (type === 'penalty') {
                score = Math.max(0, score - 30); effectDisplay.innerText = "💀 오렌지! 감점 -30점!"; effectDisplay.style.color = "#e74c3c";
            } else if (type === 'super') {
                score += 100; effectDisplay.innerText = "🍓 딸기! 슈퍼 보너스 +100점!"; effectDisplay.style.color = "#ff7675";
            }
            
            updateGameDifficulty(); // 점수 변동 시 난이도 즉각 반영
            setTimeout(() => { if(!['slow','fast','blind','reverse'].includes(type)) effectDisplay.innerText = ""; }, 2500);
        }

        // 🌟 수정: 스폰되는 모든 아이템의 이모지를 물음표(❓)로 통일
        function spawnHiddenFruit() {
            let pos = generateValidPosition();
            let fruit = { x: pos.x, y: pos.y, emoji: '❓', type: '', id: Date.now() };
            const rand = Math.random();
            
            if (rand < 0.15) { fruit.type = 'blind'; }
            else if (rand < 0.30) { fruit.type = 'tunnel'; }
            else if (rand < 0.45) { fruit.type = 'reverse'; }
            else if (rand < 0.60) { fruit.type = 'bonus'; }
            else if (rand < 0.70) { fruit.type = 'slow'; }
            else if (rand < 0.80) { fruit.type = 'fast'; }
            else if (rand < 0.90) { fruit.type = 'penalty'; }
            else { fruit.type = 'super'; }
            
            hiddenFruits.push(fruit);
            
            // 스폰된 아이템은 8초 후 자동 소멸
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
            if (isCountingDown || isGameOver) return;
            if([37, 38, 39, 40, 32].indexOf(e.keyCode) > -1) e.preventDefault(); 
            
            let LEFT = 37, UP = 38, RIGHT = 39, DOWN = 40;
            
            // 🌟 독버섯 조작 반전 활성화 시 매핑 변경
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
# 파일 폴더 생성 및 컴포넌트 선언 (캐시 방지 v8)
# -------------------------------------------------------------
component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_v8")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(GAME_HTML)

snake_game = components.declare_component("snake_v8", path=component_dir)

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
    
    # 🌟 한국 시간(KST)을 강제로 계산하여 저장 포맷으로 변환
    kst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    date_str = kst_now.strftime("%Y-%m-%d %H:%M")
    
    existing_user = next((item for item in scores if item["nickname"] == nickname), None)
    
    if existing_user:
        if score > existing_user["score"]:
            existing_user["score"] = score
            existing_user["date"] = date_str  # 신기록 갱신 시 날짜 업데이트
    else:
        scores.append({"nickname": nickname, "score": score, "date": date_str})
    
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)

# -------------------------------------------------------------
# 🏁 스트림릿 메인 화면 레이아웃
# -------------------------------------------------------------
st.title("🐍 TJ Random Speed Rush 🎮 ")
st.info(" ⬅⬆➡ 방향키 조작! 먹이를 먹을수록 **속도와 먹이 개수**가 증가합니다. ❓**물음표(랜덤 아이템)** 안에는 어떤 효과가 숨어있을까요?")

col1, col2 = st.columns([3, 1])

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
    st.subheader("🏆 실시간 TOP 10")
    scores = load_scores()
    
    if not scores:
        st.write("첫 기록을 남겨보세요!")
    else:
        # 🌟 들여쓰기 제거를 위해 줄바꿈 없이 단일 라인 문자열 덧붙임 형식으로 수정
        board_html = "<div style='display: flex; flex-direction: column; gap: 8px;'>"
        for i, s in enumerate(scores):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}위"
            
            # 1등 유저 옆 달성일 표시
            date_str = f" <span style='font-size: 12px; font-weight: normal; color: #888;'>👑 (달성: {s.get('date', '알수없음')})</span>" if i == 0 and "date" in s else ""
            
            # 스트림릿 마크다운 렌더링 오류 방지를 위해 코드 블록 안에서 탭(공백)을 완전히 제거
            board_html += "<div style='border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 8px;'>"
            board_html += f"<div style='font-weight: bold; font-size: 16px; margin-bottom: 2px;'>{medal} | {s['nickname']}{date_str}</div>"
            board_html += f"<div style='font-size: 13px; color: gray;'>Score: {s['score']} pts</div>"
            board_html += "</div>"
            
        board_html += "</div>"
        
        # HTML 렌더링
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
