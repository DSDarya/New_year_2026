import streamlit as st
import random
from streamlit.components.v1 import html
from datetime import datetime
from supabase import create_client

# --- Настройки базы данных ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- Инициализация игры ---
def initialize_game_state():
    response = supabase.table("santa_game").select("*").eq("id", 1).execute()
    
    if not response.data:
        initial_state = {
            "id": 1,
            "game_state": {
                "remaining": DEFAULT_PARTICIPANTS.copy(),
                "assigned": {},
                "game_started": False
            },
            "last_updated": datetime.now().isoformat()
        }
        supabase.table("santa_game").insert(initial_state).execute()
        return initial_state["game_state"]
    else:
        return response.data[0]["game_state"]

def get_santa_data():
    try:
        response = supabase.table("santa_game").select("*").eq("id", 1).execute()
        if response.data:
            return response.data[0]["game_state"]
    except Exception:
        return initialize_game_state()

def save_santa_data(game_state):
    try:
        data_to_save = {
            "game_state": game_state,
            "last_updated": datetime.now().isoformat()
        }
        supabase.table("santa_game").update(data_to_save).eq("id", 1).execute()
        return True
    except Exception:
        return False

def reset_game_in_db():
    reset_state = {
        "game_state": {
            "remaining": DEFAULT_PARTICIPANTS.copy(),
            "assigned": {},
            "game_started": True
        },
        "last_updated": datetime.now().isoformat()
    }
    supabase.table("santa_game").update(reset_state).eq("id", 1).execute()
    return reset_state["game_state"]

# --- Конфигурация приложения ---
st.set_page_config(page_title="Тайный Санта", page_icon="🎅", layout="centered")

DEFAULT_PARTICIPANTS = ["Даша Клоконос", "Даша Зинченко", "Саша Морозов", "Саша Зинченко", "Саша Клоконос", "Рома", "Настя", "Вика", "Алексей", "Даниил", "Инна"]

ADMIN_USER = "Даша Клоконос"

# Загружаем данные игры
santa_data = get_santa_data()
remaining = santa_data["remaining"]
assigned = santa_data["assigned"]
game_started = santa_data["game_started"]

# Инициализируем состояние сессии
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "initialized" not in st.session_state:
    st.session_state.initialized = True

# --- Снежная анимация ---
SNOW_HTML = r"""
<div id="snow-wrap" style="position:fixed;inset:0;pointer-events:none;z-index:9999;"></div>
<script>
(function() {
  var canvas = document.createElement('canvas');
  canvas.id = 'snow-canvas';
  canvas.style.position = 'fixed';
  canvas.style.left = 0;
  canvas.style.top = 0;
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = 9999;
  document.getElementById('snow-wrap').appendChild(canvas);
  var ctx = canvas.getContext('2d');
  var w, h;
  function resize(){
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  var num = Math.floor((w*h)/5000);
  var flakes = [];
  for(var i=0;i<num;i++){
    flakes.push({
      x: Math.random()*w,
      y: Math.random()*h,
      r: Math.random()*4+1,
      d: Math.random()*1
    });
  }

  function draw(){
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.beginPath();
    for(var i=0;i<flakes.length;i++){
      var f = flakes[i];
      ctx.moveTo(f.x, f.y);
      ctx.arc(f.x, f.y, f.r, 0, Math.PI*2, true);
    }
    ctx.fill();
    update();
  }

  var angle = 0;
  function update(){
    angle += 0.01;
    for(var i=0;i<flakes.length;i++){
      var f = flakes[i];
      f.y += Math.pow(f.d+1, 0.7) + 0.5;
      f.x += Math.sin(angle) * 0.5;
      if(f.y > h){
        f.y = -10;
        f.x = Math.random()*w;
      }
    }
  }

  function loop(){
    draw();
    requestAnimationFrame(loop);
  }
  loop();
})();
</script>
"""

# --- Стили ---
st.markdown(
    """
    <style>
      .app-title { 
        text-align:center; 
        font-size:48px; 
        color:#9b111e; 
        font-weight:800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
      }
      .card { 
        background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8)); 
        padding:24px; 
        border-radius:20px; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        margin-bottom: 20px;
      }
      .btn-primary {
        background: linear-gradient(90deg,#ff6b6b,#ff8e53);
        border: none;
        padding: 14px 28px;
        border-radius: 50px;
        font-size: 18px;
        font-weight: bold;
        color: white;
        transition: all 0.3s ease;
      }
      .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255,107,107,0.3);
      }
      .admin-section { 
        border: 3px solid #ff6b6b; 
        border-radius: 16px; 
        padding: 25px; 
        background: linear-gradient(135deg, rgba(255,107,107,0.08), rgba(255,142,83,0.08));
        margin: 25px 0;
      }
      .status-badge {
        background: linear-gradient(90deg,#4CAF50,#8BC34A);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
      }
      .result-card {
        background: linear-gradient(135deg,#e3f2fd,#f3e5f5);
        border-left: 6px solid #2196F3;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# Добавляем снег
html(SNOW_HTML, height=0)

# --- Заголовок ---
st.markdown('<div class="app-title">🎄 Тайный Санта 🎁</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1,2])
with col1:
    st.image("https://images.unsplash.com/photo-1549880338-65ddcdfd017b?q=80&w=400&auto=format&fit=crop", width=140)
with col2:
    st.markdown("""
    **Как это работает:**
    
    1. **Выберите своё имя** из списка ниже
    2. **Нажмите кнопку**, чтобы узнать, кому вы дарите подарок
    3. **Сохраните результат** — он останется в тайне от других
    4. **Организатор** может видеть все пары и управлять игрой
    """)

st.markdown("<div class='card'>", unsafe_allow_html=True)

# --- Авторизация (единственный способ) ---
st.markdown("### 👤 Выберите, кто вы")

# Показываем только тех, кто еще не выбрал получателя
available_users = [p for p in DEFAULT_PARTICIPANTS if p not in assigned]
options = ["Выберите своё имя..."] + available_users

user = st.selectbox("", options, label_visibility="collapsed")

if user != "Выберите своё имя...":
    st.session_state.current_user = user
    st.success(f"Привет, **{user}**! 👋")

st.markdown("</div>", unsafe_allow_html=True)

# --- Основной интерфейс ---
if st.session_state.current_user:
    user = st.session_state.current_user
    is_admin = user == ADMIN_USER
    
    st.markdown(f"## 🎅 Добро пожаловать, {user}!")
    
    col_a, col_b = st.columns([2,1])
    with col_a:
        st.markdown("**✨ Вы можете узнать получателя только один раз**")
    with col_b:
        st.markdown(f"<div class='status-badge'>Осталось участников: {len(remaining)}</div>", unsafe_allow_html=True)
    
    # Проверяем, не выбрал ли уже этот пользователь
    if user in assigned:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("### 🎉 Ваш получатель найден!")
        st.markdown(f"# 🎁 **{assigned[user]}**")
        st.markdown("Этот результат сохранён и больше не изменится")
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        if st.button("🎯 Узнать, кому я дарю подарок", type="primary", use_container_width=True):
            if not remaining:
                st.error("Все подарки уже распределены! 🎄")
            else:
                # Исключаем текущего пользователя из возможных получателей
                pool = [p for p in remaining if p != user]
                
                if not pool:
                    st.error("Для вас нет доступных получателей 😔")
                else:
                    chosen = random.choice(pool)
                    assigned[user] = chosen
                    remaining.remove(chosen)
                    santa_data["game_started"] = True
                    santa_data["assigned"] = assigned
                    santa_data["remaining"] = remaining
                    
                    if save_santa_data(santa_data):
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Что-то пошло не так. Попробуйте ещё раз")

# --- Панель организатора ---
if st.session_state.current_user == ADMIN_USER:
    st.markdown("<div class='admin-section'>", unsafe_allow_html=True)
    st.markdown("### 👑 Панель организатора")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Текущий статус:**")
        st.write(f"Всего участников: **{len(DEFAULT_PARTICIPANTS)}**")
        st.write(f"Уже выбрали: **{len(assigned)}**")
        st.write(f"Осталось: **{len(remaining)}**")
    
    with col2:
        if st.button("🔄 Начать игру заново", type="secondary", use_container_width=True):
            reset_game_in_db()
            st.success("Игра сброшена!")
            st.rerun()
    
    # Показать все назначения
    if assigned:
        st.markdown("### 📋 Все пары Санта → Получатель")
        cols = st.columns(3)
        for idx, (santa, recipient) in enumerate(assigned.items()):
            with cols[idx % 3]:
                st.markdown(f"**🎅 {santa}**<br>→ 🎁 **{recipient}**", unsafe_allow_html=True)
        
        # Кнопка для скачивания
        st.download_button(
            label="📥 Скачать полный список",
            data="\n".join([f"{santa} → {recipient}" for santa, recipient in assigned.items()]),
            file_name="тайный_санта_результаты.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- Статус игры ---
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 📊 Статус игры")

progress = len(assigned) / len(DEFAULT_PARTICIPANTS)
st.progress(progress)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Всего участников", len(DEFAULT_PARTICIPANTS), border=True)
with col2:
    st.metric("Уже выбрали", len(assigned), border=True)
with col3:
    st.metric("Осталось", len(remaining), border=True)

if not remaining and assigned:
    st.success("🎉 **Все участники получили своих получателей! Игра завершена!**")
    
    # Показываем все пары при завершении игры
    st.markdown("### 🎄 Финальные пары")
    for santa, recipient in assigned.items():
        st.markdown(f"**{santa}** → **{recipient}**")

st.markdown("</div>", unsafe_allow_html=True)

# --- Информация о сохранении ---
if not game_started and len(assigned) == 0:
    st.info("ℹ️ **Игра готова к началу!** Первый участник может выбрать получателя.")
else:
    st.success("✅ **Все результаты надёжно сохранены** и доступны всем участникам")
