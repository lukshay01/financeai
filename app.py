import streamlit as st
import re
import os
import plotly.graph_objects as go
from groq import Groq
from pdf_export import generate_pdf
from stocks_news import render_stocks_page

st.set_page_config(page_title=“FinanceAI”, page_icon=“💰”, layout=“wide”)

st.markdown(”””
<style>
@import url(‘https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap’);
html, body, [class*=“css”] { font-family: ‘Inter’, sans-serif; }
.main { background-color: #0f1117; color: #ffffff; }
.stApp { background-color: #0f1117; }
.metric-card {
background: linear-gradient(135deg, #1e2130, #252840);
border: 1px solid #2d3150;
border-radius: 16px;
padding: 20px;
text-align: center;
margin: 5px 0;
}
.metric-value { font-size: 2em; font-weight: 700; color: #4ade80; }
.metric-label { font-size: 0.85em; color: #94a3b8; margin-top: 4px; }
.profile-box {
background: linear-gradient(135deg, #1e2130, #252840);
border: 1px solid #2d3150;
padding: 10px 14px;
border-radius: 10px;
margin: 4px 0;
font-size: 0.9em;
}
.welcome-feature {
background: linear-gradient(135deg, #1e2130, #252840);
border: 1px solid #2d3150;
border-radius: 16px;
padding: 24px;
height: 100%;
}
.comparison-left {
background: linear-gradient(135deg, #0d2b1e, #1a3a2a);
border: 1px solid #2d6a4f;
border-radius: 12px;
padding: 20px;
}
.comparison-right {
background: linear-gradient(135deg, #2b1a0d, #3a2a1a);
border: 1px solid #6a4f2d;
border-radius: 12px;
padding: 20px;
}
div[data-testid=“stChatMessage”] {
background: #1e2130;
border-radius: 12px;
padding: 4px;
margin: 4px 0;
}
.stButton button { border-radius: 10px; font-weight: 600; }
</style>
“””, unsafe_allow_html=True)

# ============================================================

# GROQ CLIENT

# ============================================================

@st.cache_resource
def get_groq_client():
api_key = st.secrets.get(“GROQ_API_KEY”) or os.environ.get(“GROQ_API_KEY”)
if not api_key:
st.error(“Groq API key not found. Please add GROQ_API_KEY to your Streamlit secrets.”)
st.stop()
return Groq(api_key=api_key)

SYSTEM_PROMPT = “”“You are FinanceAI, an expert personal financial advisor with 20 years of experience.

IMPORTANT - You must follow this exact conversation flow:

STAGE 1 - GREETING:
Warmly welcome the user and ask for their name and age only.

STAGE 2 - INCOME AND EXPENSES:
Once you have name and age, ask about their monthly income and monthly expenses only.

STAGE 3 - GOALS:
Once you have income and expenses, ask about their financial goals (saving, investing, buying home, retirement etc).

STAGE 4 - RISK TOLERANCE:
Ask if they prefer low risk (safe), medium risk (balanced) or high risk (aggressive growth).

STAGE 5 - GENERATE FINANCIAL PLAN:
Once you have all information, think step by step like this:

Step 1 - Calculate their monthly savings (income minus expenses)
Step 2 - Calculate their savings rate percentage
Step 3 - Assess their financial health based on age and savings rate
Step 4 - Consider their goals and risk tolerance
Step 5 - Generate specific recommendations with real numbers and timelines

Then present a complete financial plan with these sections:

## Your Financial Summary

## Your Financial Health Score (rate out of 10 with explanation)

## Key Recommendations (at least 3 specific ones with numbers)

## Your Action Plan (week by week for first month)

## Long Term Outlook (where they could be in 5 and 10 years)

Always use their actual numbers. Be specific, warm and encouraging.
Never give vague advice. Every recommendation must include specific numbers and timelines.
Always complete your full response. Never leave answers incomplete.
Double check all spelling before responding.”””

# ============================================================

# SESSION STATE

# ============================================================

if “messages” not in st.session_state:
st.session_state.messages = []
if “started” not in st.session_state:
st.session_state.started = False
if “user_profile” not in st.session_state:
st.session_state.user_profile = {
“Name”: None, “Age”: None, “Monthly Income”: None,
“Monthly Expenses”: None, “Financial Goals”: None, “Risk Tolerance”: None
}
if “mode” not in st.session_state:
st.session_state.mode = “chat”
if “show_charts” not in st.session_state:
st.session_state.show_charts = False

# ============================================================

# HELPER FUNCTIONS

# ============================================================

def extract_numbers(text):
numbers = re.findall(r’$?(\d+(?:,\d{3})*(?:.\d{2})?)’, text)
return [float(n.replace(”,”, “”)) for n in numbers]

def extract_profile_info(message, profile):
msg_lower = message.lower()
words = message.split()
for i, word in enumerate(words):
if word.lower() in [“is”, “am”] and i + 1 < len(words):
potential_name = words[i + 1].strip(”.,!?”)
if potential_name and potential_name[0].isupper() and len(potential_name) > 1:
profile[“Name”] = potential_name
numbers = extract_numbers(message)
if numbers:
if any(word in msg_lower for word in [“earn”, “income”, “salary”, “make”, “paid”]):
profile[“Monthly Income”] = “$” + str(int(numbers[0]))
if any(word in msg_lower for word in [“spend”, “expenses”, “expense”, “costs”]):
profile[“Monthly Expenses”] = “$” + str(int(numbers[0]))
if any(word in msg_lower for word in [“low risk”, “safe”, “conservative”]):
profile[“Risk Tolerance”] = “Low Risk”
elif any(word in msg_lower for word in [“medium risk”, “balanced”, “moderate”]):
profile[“Risk Tolerance”] = “Medium Risk”
elif any(word in msg_lower for word in [“high risk”, “aggressive”, “growth”]):
profile[“Risk Tolerance”] = “High Risk”
goals = []
if “invest” in msg_lower:
goals.append(“Investing”)
if “house” in msg_lower or “home” in msg_lower:
goals.append(“Buy Home”)
if “retire” in msg_lower:
goals.append(“Retirement”)
if “save” in msg_lower:
goals.append(“Savings”)
if “debt” in msg_lower:
goals.append(“Debt Freedom”)
if goals:
profile[“Financial Goals”] = “, “.join(goals)
return profile

def get_groq_response(question, model=“llama-3.3-70b-versatile”):
client = get_groq_client()
simple_prompt = f”You are a financial advisor. Answer this question with specific advice and numbers: {question}”
response = client.chat.completions.create(
model=model,
messages=[{“role”: “user”, “content”: simple_prompt}],
max_tokens=1024,
temperature=0.5,
)
return response.choices[0].message.content

def parse_amount(amount_str):
if amount_str:
numbers = extract_numbers(amount_str)
if numbers:
return numbers[0]
return None

def create_budget_chart(income, expenses):
savings = max(income - expenses, 0)
expenses_display = min(expenses, income)
fig = go.Figure(data=[go.Pie(
labels=[“Expenses”, “Savings”],
values=[expenses_display, savings],
hole=0.6,
marker=dict(colors=[”#f87171”, “#4ade80”], line=dict(color=”#0f1117”, width=3)),
textinfo=“label+percent”,
textfont=dict(size=14, color=“white”),
)])
fig.update_layout(
paper_bgcolor=“rgba(0,0,0,0)”,
plot_bgcolor=“rgba(0,0,0,0)”,
font=dict(color=“white”, family=“Inter”),
showlegend=False,
margin=dict(t=20, b=20, l=20, r=20),
annotations=[dict(
text=f”${int(savings):,}<br>saved”,
x=0.5, y=0.5,
font=dict(size=16, color=”#4ade80”, family=“Inter”),
showarrow=False
)]
)
return fig

def create_projection_chart(monthly_savings, years=10):
months = list(range(0, years * 12 + 1))
rates = {
“No Investment (0%)”: 0.0,
“High Interest Savings (5%)”: 0.05,
“Index Funds (8%)”: 0.08,
}
colors = [”#94a3b8”, “#60a5fa”, “#4ade80”]
fig = go.Figure()
for (label, annual_rate), color in zip(rates.items(), colors):
monthly_rate = annual_rate / 12
values = []
total = 0
for m in months:
if m == 0:
values.append(0)
else:
total = total * (1 + monthly_rate) + monthly_savings
values.append(total)
fig.add_trace(go.Scatter(
x=[m / 12 for m in months],
y=values,
name=label,
line=dict(color=color, width=2.5),
))
fig.update_layout(
paper_bgcolor=“rgba(0,0,0,0)”,
plot_bgcolor=“rgba(0,0,0,0)”,
font=dict(color=“white”, family=“Inter”),
xaxis=dict(title=“Years”, gridcolor=”#2d3150”, color=“white”),
yaxis=dict(title=“Total Savings ($)”, gridcolor=”#2d3150”, tickformat=”$,.0f”, color=“white”),
legend=dict(bgcolor=“rgba(0,0,0,0)”, font=dict(color=“white”), orientation=“h”, yanchor=“bottom”, y=1.02),
margin=dict(t=60, b=40, l=60, r=20),
hovermode=“x unified”
)
return fig

# ============================================================

# SIDEBAR

# ============================================================

with st.sidebar:
st.markdown(”## 💰 FinanceAI”)
st.caption(“Your personal AI financial advisor”)
st.divider()

```
st.markdown("### Mode")
mode = st.radio("", ["💬 Chat", "📊 Dashboard", "📈 Markets & News", "⚖️ Compare Models"], index=0, label_visibility="collapsed")
if mode == "💬 Chat":
    st.session_state.mode = "chat"
elif mode == "📊 Dashboard":
    st.session_state.mode = "dashboard"
elif mode == "📈 Markets & News":
    st.session_state.mode = "markets"
else:
    st.session_state.mode = "compare"

st.divider()
st.markdown("### 👤 Your Profile")
any_info = False
for key, value in st.session_state.user_profile.items():
    if value:
        any_info = True
        st.markdown(f"<div class='profile-box'><strong>{key}</strong><br>{value}</div>", unsafe_allow_html=True)
if not any_info:
    st.caption("Your profile fills in as we chat!")

st.divider()
st.caption("🔒 Your data never leaves this session")

if st.session_state.messages:
    st.divider()
    st.markdown("### 📄 Export")
    pdf_buffer = generate_pdf(st.session_state.user_profile, st.session_state.messages)
    st.download_button(
        label="⬇️ Download Financial Plan (PDF)",
        data=pdf_buffer,
        file_name="FinanceAI_Plan.pdf",
        mime="application/pdf",
        use_container_width=True
    )

if st.button("🔄 Start Over", use_container_width=True):
    st.session_state.messages = []
    st.session_state.started = False
    st.session_state.show_charts = False
    st.session_state.user_profile = {
        "Name": None, "Age": None, "Monthly Income": None,
        "Monthly Expenses": None, "Financial Goals": None, "Risk Tolerance": None
    }
    st.rerun()
```

# ============================================================

# DASHBOARD MODE

# ============================================================

if st.session_state.mode == “dashboard”:
st.title(“📊 Financial Dashboard”)
st.caption(“Visual overview of your financial situation”)
st.divider()

```
income = parse_amount(st.session_state.user_profile.get("Monthly Income"))
expenses = parse_amount(st.session_state.user_profile.get("Monthly Expenses"))

if not income or not expenses:
    st.info("👋 Complete the chat first to populate your dashboard with real numbers!")
    st.markdown("Go to **💬 Chat** mode and tell FinanceAI your income and expenses to unlock your dashboard.")
else:
    savings = income - expenses
    savings_rate = (savings / income) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>${int(income):,}</div>
            <div class='metric-label'>Monthly Income</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value' style='color:#f87171'>${int(expenses):,}</div>
            <div class='metric-label'>Monthly Expenses</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        color = "#4ade80" if savings > 0 else "#f87171"
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value' style='color:{color}'>${int(savings):,}</div>
            <div class='metric-label'>Monthly Savings</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        color = "#4ade80" if savings_rate >= 20 else "#fbbf24" if savings_rate >= 10 else "#f87171"
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value' style='color:{color}'>{savings_rate:.1f}%</div>
            <div class='metric-label'>Savings Rate</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🥧 Budget Breakdown")
        st.plotly_chart(create_budget_chart(income, expenses), use_container_width=True)
    with col2:
        st.markdown("### 📈 10-Year Savings Projection")
        if savings > 0:
            st.plotly_chart(create_projection_chart(savings), use_container_width=True)
        else:
            st.warning("Your expenses exceed your income. Focus on reducing expenses first.")

    if savings > 0:
        st.divider()
        st.markdown("### 🔮 Projection at 10 Years")
        col1, col2, col3 = st.columns(3)
        months = 120
        with col1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>${int(savings * months):,}</div>
                <div class='metric-label'>No Investment (0%)</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            total = 0
            for _ in range(months):
                total = total * (1 + 0.05/12) + savings
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>${int(total):,}</div>
                <div class='metric-label'>High Interest Savings (5%)</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            total = 0
            for _ in range(months):
                total = total * (1 + 0.08/12) + savings
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>${int(total):,}</div>
                <div class='metric-label'>Index Funds (8%)</div>
            </div>""", unsafe_allow_html=True)
```

# ============================================================

# MARKETS MODE

# ============================================================

elif st.session_state.mode == “markets”:
render_stocks_page()

# ============================================================

# COMPARE MODE

# ============================================================

elif st.session_state.mode == “compare”:
st.title(“⚖️ Model Comparison”)
st.caption(“See how different AI models answer the same financial question”)
st.divider()
st.markdown(“Type any financial question below and two different models answer simultaneously.”)
st.divider()

```
compare_question = st.text_area(
    "Enter a financial question:",
    placeholder="e.g. I earn $5000 a month and spend $4000. I am 30 years old. What should I do with my savings?",
    height=100
)

if st.button("⚡ Compare Both Models", type="primary", use_container_width=True):
    if compare_question:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🟢 LLaMA 3.3 70B")
            st.caption("LLaMA 3.3 70B — Meta's most powerful open source model")
            with st.spinner("LLaMA 3.3 70B thinking..."):
                r1 = get_groq_response(compare_question, model="llama-3.3-70b-versatile")
            st.markdown(f"<div class='comparison-left'>{r1}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("### 🟠 LLaMA 3.1 8B")
            st.caption("LLaMA 3.1 8B — lighter, faster model for comparison")
            with st.spinner("LLaMA 3.1 8B thinking..."):
                r2 = get_groq_response(compare_question, model="llama-3.1-8b-instant")
            st.markdown(f"<div class='comparison-right'>{r2}</div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("### 📊 What to Notice")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**🎯 Specificity**\nMore specific numbers?")
        with col2:
            st.markdown("**📋 Structure**\nBetter organised?")
        with col3:
            st.markdown("**💬 Tone**\nWarmer and friendlier?")
        with col4:
            st.markdown("**✅ Actions**\nClearer next steps?")
    else:
        st.warning("Please enter a question first!")
```

# ============================================================

# CHAT MODE

# ============================================================

else:
st.title(“💰 FinanceAI”)
st.caption(“Your personal AI financial advisor — powered by Mixtral AI”)
st.divider()

```
if not st.session_state.started:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='welcome-feature'>
            <h3>📊 Budgeting</h3>
            <p style='color:#94a3b8'>Understand exactly where your money goes and how to optimise every dollar</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='welcome-feature'>
            <h3>💹 Investing</h3>
            <p style='color:#94a3b8'>Get a personalised investment strategy based on your goals and risk tolerance</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='welcome-feature'>
            <h3>🎯 Planning</h3>
            <p style='color:#94a3b8'>Build a step by step financial plan with real numbers and timelines</p>
        </div>""", unsafe_allow_html=True)

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🔒 **100% Private** — session only")
    with col2:
        st.markdown("⚡ **Blazing fast** — powered by Groq")
    with col3:
        st.markdown("🇦🇺 **Australian focused** — super, tax, grants")
    st.divider()

    if st.button("🚀 Start My Financial Plan", type="primary", use_container_width=True):
        st.session_state.started = True
        opening = "Welcome to FinanceAI! 👋 I am your personal financial advisor and I am here to build you a customised financial plan.\n\nTo get started, could you tell me your **first name** and **age**?"
        st.session_state.messages.append({"role": "assistant", "content": opening})
        st.rerun()

if st.session_state.started:
    income = parse_amount(st.session_state.user_profile.get("Monthly Income"))
    expenses = parse_amount(st.session_state.user_profile.get("Monthly Expenses"))
    if income and expenses:
        savings = income - expenses
        savings_rate = (savings / income) * 100
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>${int(income):,}</div>
                <div class='metric-label'>Monthly Income</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            color = "#4ade80" if savings > 0 else "#f87171"
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value' style='color:{color}'>${int(savings):,}</div>
                <div class='metric-label'>Monthly Savings</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            color = "#4ade80" if savings_rate >= 20 else "#fbbf24" if savings_rate >= 10 else "#f87171"
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value' style='color:{color}'>{savings_rate:.1f}%</div>
                <div class='metric-label'>Savings Rate</div>
            </div>""", unsafe_allow_html=True)
        st.caption("👆 Switch to **📊 Dashboard** in the sidebar for full charts")
        st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your message here..."):
        st.session_state.user_profile = extract_profile_info(prompt, st.session_state.user_profile)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        client = get_groq_client()
        with st.chat_message("assistant"):
            reply_placeholder = st.empty()
            full_reply = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=groq_messages,
                max_tokens=1024,
                temperature=0.5,
                stream=True,
            )
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                full_reply += token
                reply_placeholder.markdown(full_reply + "▌")
            reply_placeholder.markdown(full_reply)

        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        st.rerun()
```