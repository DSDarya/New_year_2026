import streamlit as st
import random
from streamlit.components.v1 import html

# --- CONFIG ---
st.set_page_config(page_title="Тайный Санта", page_icon="🎅", layout="centered")

# --- DATA ---
DEFAULT_PARTICIPANTS = [
    "Даша К", "Даша З", "Саша М", "Саша З", "Саша К",
    "Рома", "Настя", "Вика", "Алексей", "Даниил", "Инна"
]

# --- SESSION STATE INIT ---
def init_state():
    if "remaining" not in st.session_state:
        st.session_state.remaining = DEFAULT_PARTICIPANTS.copy()
    if "assigned" not in st.session_state:
        st.session_state.assigned = {}
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "Simple select"

init_state()

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
    """)

st.markdown("---")

# --- AUTH MODE ---
st.markdown("### Вариант авторизации")
st.session_state.auth_mode = st.selectbox("Выберите способ авторизации:", ["Simple select", "Secret code (demo)", "One-time token (demo)"])

# --- AUTH FORM ---
st.markdown("### Авторизация")
if st.session_state.auth_mode == "Simple select":
    user = st.selectbox("Кто вы?", ["Выберите..."] + DEFAULT_PARTICIPANTS)
    if user != "Выберите...":
        st.session_state.current_user = user

elif st.session_state.auth_mode == "Secret code (demo)":
    st.info("Режим демонстрации: введите ваше имя и секретный код. Код не проверяется — это пример UX.")
    user_input = st.text_input("Ваше имя")
    code = st.text_input("Секретный код")
    if st.button("Войти" , key="login_code"):
        if user_input and code:
            st.session_state.current_user = user_input
            st.success("Вход выполнен (демо)")
        else:
            st.error("Введите имя и код")

else:
    st.info("Режим демонстрации: одноразовый токен имитируется генерацией случайного токена")
    display_token = st.text_input("Введите ваш одноразовый токен")
    if st.button("Войти", key="login_token"):
        if display_token:
            # In demo we accept any token
            st.session_state.current_user = "(токен) " + display_token
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
        st.markdown("Вы можете получить имя вашего получателя один раз. После выдачи это имя удаляется из общего пула.")
    with col_b:
        st.markdown(f"**Осталось участников:** {len(st.session_state.remaining)}")

    if st.button("Получить имя получателя 🎁"):
        if user in st.session_state.assigned:
            st.warning("Вы уже получили имя! 🎄")
        else:
            # Ensure the pool is up-to-date: initialize from defaults minus already assigned recipients
            # (use this to be robust if participants list was edited)
            pool = [p for p in st.session_state.remaining if p != user]
            if not pool:
                st.error("К сожалению, доступных имён не осталось.")
            else:
                chosen = random.choice(pool)
                st.session_state.assigned[user] = chosen
                # Remove from remaining so nobody else can get it
                st.session_state.remaining.remove(chosen)
                st.success("Имя успешно выдано! Перезагрузите страницу, чтобы скрыть ответ (при желании).")

    if user in st.session_state.assigned:
        st.markdown("---")
        st.success(f"Ваш получатель: **{st.session_state.assigned[user]}** 🎁✨")

    # Optional: show small hint

else:
    st.info("Пожалуйста, авторизуйтесь, чтобы получить имя получателя.")

st.markdown("---")

