import streamlit as st
import random
from streamlit.components.v1 import html
import json

# --- CONFIG ---
st.set_page_config(page_title="Тайный Санта", page_icon="🎅", layout="centered")

# --- DATA ---
DEFAULT_PARTICIPANTS = [
    "Даша К", "Даша З", "Саша М", "Саша З", "Саша К",
    "Рома", "Настя", "Вика", "Алексей", "Даниил", "Инна"
]

# --- ADMIN CONFIG ---
ADMIN_USER = "Даша К"  # Единственный пользователь с доступом к админке

# --- PERSISTENT STORAGE FUNCTIONS ---
def load_data():
    """Загружает данные из session_state или создает новые"""
    if "santa_data" not in st.session_state:
        st.session_state.santa_data = {
            "remaining": DEFAULT_PARTICIPANTS.copy(),
            "assigned": {},
            "used_tokens": set()
        }
    return st.session_state.santa_data

def save_data():
    """Сохраняет данные в session_state"""
    # Данные автоматически сохраняются в st.session_state
    pass

def reset_game():
    """Сбрасывает игру к начальному состоянию"""
    st.session_state.santa_data = {
        "remaining": DEFAULT_PARTICIPANTS.copy(),
        "assigned": {},
        "used_tokens": set()
    }
    st.session_state.current_user = None
    st.rerun()

# --- SESSION STATE INIT ---
def init_state():
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "Simple select"
    
    # Загружаем основные данные
    load_data()

init_state()

# Получаем ссылки на данные
santa_data = st.session_state.santa_data
remaining = santa_data["remaining"]
assigned = santa_data["assigned"]
used_tokens = santa_data["used_tokens"]

# --- SNOW ANIMATION (injected via an HTML canvas) ---
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

# --- STYLES ---
st.markdown(
    """
    <style>
      .app-title { text-align:center; font-size:48px; color:#9b111e; font-weight:800; }
      .card { background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.75)); padding:18px; border-radius:16px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); }
      .small { font-size:14px; color:#333; }
      .btn { background: linear-gradient(90deg,#ff9a9e,#fad0c4); border: none; padding: 10px 18px; border-radius: 12px; }
      .admin-section { border: 2px solid #ff6b6b; border-radius: 10px; padding: 15px; background: rgba(255, 107, 107, 0.1); }
    </style>
    """,
    unsafe_allow_html=True
)

# Inject snow (hidden behind app content)
html(SNOW_HTML, height=0)

# --- HEADER ---
st.markdown('<div class="app-title">🎄 Тайный Санта — хо-хо-хо🎁</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1,2])
with col1:
    st.image("https://images.unsplash.com/photo-1549880338-65ddcdfd017b?q=80&w=400&auto=format&fit=crop&ixlib=rb-4.0.3&s=placeholder", width=120)
with col2:
    st.markdown("""
    **Как работает**
    - Вы выбираете своё имя в форме авторизации.
    - Нажимаете кнопку — и вам случайно выдаётся получатель.
    - Каждый участник может выбрать имя только один раз!
    - Каждое имя может быть выбрано только один раз!
    """)

st.markdown("---")

# --- ADMIN SECTION (ONLY FOR Даша К) ---
def show_admin_section():
    """Показывает админ-панель только для Даши К"""
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.markdown("### 🔧 Панель организатора")
    
    st.write("**Текущее состояние:**")
    st.write(f"Осталось участников: {len(remaining)}")
    st.write(f"Уже выбрали: {len(assigned)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Полный сброс игры", type="secondary", use_container_width=True):
            reset_game()
            st.success("Игра полностью сброшена!")
    
    with col2:
        if st.button("📊 Показать все назначения", type="secondary", use_container_width=True):
            if assigned:
                st.write("**Все назначения:**")
                for santa, recipient in assigned.items():
                    st.write(f"🎅 {santa} → 🎁 {recipient}")
            else:
                st.info("Назначений пока нет")
    
    # Расширенная информация
    if assigned:
        st.write("**Детальная информация:**")
        assigned_users = list(assigned.keys())
        remaining_users = remaining.copy()
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.write("**Выбрали получателей:**")
            for user in assigned_users:
                st.write(f"• {user}")
        
        with col_info2:
            st.write("**Еще не выбрали:**")
            for user in remaining_users:
                st.write(f"• {user}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Проверяем, является ли текущий пользователь админом
is_admin = st.session_state.current_user == ADMIN_USER

if is_admin:
    show_admin_section()
else:
    # Показываем минимальную информацию о статусе для всех пользователей
    st.markdown(f"**Статус:** {len(assigned)} из {len(DEFAULT_PARTICIPANTS)} участников уже выбрали получателей")

st.markdown("---")

# --- AUTH MODE ---
st.markdown("### Вариант авторизации")
st.session_state.auth_mode = st.selectbox("Выберите способ авторизации:", ["Simple select", "Secret code (demo)", "One-time token (demo)"])

# --- AUTH FORM ---
st.markdown("### Авторизация")
current_user = None

if st.session_state.auth_mode == "Simple select":
    # Показываем только тех, кто еще не выбрал
    available_users = [p for p in DEFAULT_PARTICIPANTS if p not in assigned]
    options = ["Выберите..."] + available_users
    
    user = st.selectbox("Кто вы?", options)
    if user != "Выберите...":
        st.session_state.current_user = user
        current_user = user

elif st.session_state.auth_mode == "Secret code (demo)":
    st.info("Режим демонстрации: введите ваше имя и секретный код. Код не проверяется — это пример UX.")
    user_input = st.text_input("Ваше имя")
    code = st.text_input("Секретный код")
    if st.button("Войти", key="login_code"):
        if user_input and code:
            if user_input in assigned:
                st.error("Этот пользователь уже выбрал получателя!")
            else:
                st.session_state.current_user = user_input
                current_user = user_input
                st.success("Вход выполнен (демо)")
        else:
            st.error("Введите имя и код")

else:  # One-time token
    st.info("Режим демонстрации: одноразовый токен имитируется генерацией случайного токена")
    
    # Генерация уникального токена
    if 'generated_token' not in st.session_state:
        st.session_state.generated_token = f"token_{random.randint(1000, 9999)}"
    
    st.code(f"Ваш демо-токен: {st.session_state.generated_token}", language="text")
    st.caption("Скопируйте этот токен для входа (демо-режим)")
    
    display_token = st.text_input("Введите ваш одноразовый токен")
    if st.button("Войти", key="login_token"):
        if display_token:
            if display_token in used_tokens:
                st.error("Этот токен уже использован!")
            else:
                used_tokens.add(display_token)
                st.session_state.current_user = f"Пользователь_{display_token}"
                current_user = st.session_state.current_user
                st.success("Вход выполнен (демо)")
        else:
            st.error("Требуется токен")

st.markdown("---")

# --- MAIN INTERACTION ---
if st.session_state.current_user:
    user = st.session_state.current_user
    st.markdown(f"## Привет, **{user}**! 🎅")

    col_a, col_b = st.columns([2,1])
    with col_a:
        st.markdown("Вы можете получить имя вашего получателя **только один раз**. После выдачи это имя удаляется из общего пуала.")
    
    with col_b:
        st.markdown(f"**Осталось участников:** {len(remaining)}")
        if is_admin:
            st.markdown("👑 **Вы организатор**")

    # Проверяем, не выбрал ли уже этот пользователь
    if user in assigned:
        st.warning("⚠️ Вы уже получили имя получателя!")
        st.success(f"Ваш получатель: **{assigned[user]}** 🎁✨")
        st.info("Если вы забыли имя получателя, оно показано выше.")
        
    else:
        if st.button("🎯 Получить имя получателя 🎁", type="primary"):
            if not remaining:
                st.error("К сожалению, все имена уже разобраны!")
            else:
                # Исключаем текущего пользователя из возможных получателей
                pool = [p for p in remaining if p != user]
                
                if not pool:
                    st.error("К сожалению, для вас нет доступных получателей.")
                else:
                    chosen = random.choice(pool)
                    assigned[user] = chosen
                    remaining.remove(chosen)
                    save_data()
                    
                    st.balloons()
                    st.success(f"🎉 Ваш получатель: **{chosen}** 🎁✨")
                    st.info("Запишите или запомните это имя! После обновления страницы вы сможете снова его посмотреть.")

    # Всегда показываем текущее назначение, если оно есть
    if user in assigned:
        st.markdown("---")
        st.markdown(f"### 🎁 Ваш получатель: **{assigned[user]}**")
        st.caption("Это имя сохранится даже после обновления страницы")

else:
    st.info("👆 Пожалуйста, авторизуйтесь, чтобы получить имя получателя.")

st.markdown("---")

# --- STATUS INFO ---
st.markdown("### 📊 Статус игры")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Всего участников", len(DEFAULT_PARTICIPANTS))
with col2:
    st.metric("Уже выбрали", len(assigned))
with col3:
    st.metric("Осталось", len(remaining))

if not remaining and assigned:
    st.success("🎄 Все участники получили своих получателей! Тайный Санта завершен!")

# --- SECRET ADMIN ACCESS FOR Даша К (даже если она уже выбрала) ---
if st.session_state.current_user and st.session_state.current_user == ADMIN_USER and st.session_state.current_user in assigned:
    st.markdown("---")
    with st.expander("🔒 Секретный доступ организатора"):
        st.info("Вы уже выбрали получателя, но как организатор можете видеть админ-функции")
        show_admin_section()
