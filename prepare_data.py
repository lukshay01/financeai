import json
import pandas as pd
from datasets import load_dataset

print("=" * 60)
print("FinanceAI Data Pipeline")
print("=" * 60)

# ============================================================
# STEP 1: DOWNLOAD DATASET
# ============================================================
print("\n📥 Step 1: Downloading finance-alpaca dataset from HuggingFace...")
print("This has 68,912 real financial Q&A pairs - please wait...")

dataset = load_dataset("gbharti/finance-alpaca", split="train")
print(f"✅ Downloaded! Total examples: {len(dataset)}")

# ============================================================
# STEP 2: CONVERT TO DATAFRAME FOR CLEANING
# ============================================================
print("\n🔄 Step 2: Converting to DataFrame for cleaning...")
df = pd.DataFrame(dataset)
print(f"Columns available: {list(df.columns)}")
print(f"Sample row:\n{df.iloc[0]}")

# ============================================================
# STEP 3: CLEAN THE DATA
# ============================================================
print("\n🧹 Step 3: Cleaning the data...")
initial_count = len(df)

# Combine instruction + input as the prompt
def build_prompt(row):
    if row.get("input") and str(row["input"]).strip():
        return f"{row['instruction']}\n\nContext: {row['input']}"
    return row["instruction"]

df["prompt"] = df.apply(build_prompt, axis=1)
df["response"] = df["output"]

# Remove rows with missing values
df = df.dropna(subset=["prompt", "response"])
print(f"  After removing nulls: {len(df)} rows")

# Remove duplicates
df = df.drop_duplicates(subset=["prompt"])
print(f"  After removing duplicates: {len(df)} rows")

# Remove rows where prompt is too short (less than 20 characters)
df = df[df["prompt"].str.len() >= 20]
print(f"  After removing short prompts: {len(df)} rows")

# Remove rows where response is too short (less than 50 characters)
df = df[df["response"].str.len() >= 50]
print(f"  After removing short responses: {len(df)} rows")

# Remove rows where response is too long (more than 2000 characters - too heavy for training)
df = df[df["response"].str.len() <= 2000]
print(f"  After removing very long responses: {len(df)} rows")

# Remove rows with placeholder or junk text
junk_phrases = ["lorem ipsum", "placeholder", "todo", "tbd", "n/a", "null"]
for phrase in junk_phrases:
    df = df[~df["response"].str.lower().str.contains(phrase, na=False)]
print(f"  After removing junk text: {len(df)} rows")

print(f"\n✅ Cleaning complete! Removed {initial_count - len(df)} bad rows")
print(f"   Clean dataset size: {len(df)} examples")

# ============================================================
# STEP 4: FILTER FOR QUALITY
# ============================================================
print("\n🔍 Step 4: Filtering for quality...")

# Keep only responses with good length (sweet spot for quality)
df["response_length"] = df["response"].str.len()
df["prompt_length"] = df["prompt"].str.len()

# Score each example by response length (longer = more detailed = better)
df["quality_score"] = df["response_length"]

# Boost score for examples with numbers (financial advice should have numbers)
df["has_numbers"] = df["response"].str.contains(r'\$|\d+%|\d+,\d+', regex=True)
df["quality_score"] = df["quality_score"] + (df["has_numbers"] * 200)

# Boost score for examples with financial keywords
financial_keywords = ["invest", "budget", "saving", "return", "portfolio", 
                      "risk", "income", "expense", "retire", "debt", "interest"]
for keyword in financial_keywords:
    df["quality_score"] = df["quality_score"] + (
        df["response"].str.lower().str.contains(keyword) * 50
    )

print(f"  Average quality score: {df['quality_score'].mean():.0f}")
print(f"  Top quality score: {df['quality_score'].max():.0f}")

# ============================================================
# STEP 5: SAMPLE BEST EXAMPLES
# ============================================================
print("\n🎯 Step 5: Selecting best 1000 examples...")

# Sort by quality score and take top 1000
df_top = df.nlargest(1000, "quality_score")
print(f"  Selected {len(df_top)} high quality examples")
print(f"  Average response length: {df_top['response_length'].mean():.0f} characters")
print(f"  Examples with numbers: {df_top['has_numbers'].sum()} ({df_top['has_numbers'].mean()*100:.0f}%)")

# ============================================================
# STEP 6: ADD OUR CUSTOM EXAMPLES ON TOP
# ============================================================
print("\n➕ Step 6: Adding custom Australian financial examples...")

custom_examples = [
    {
        "prompt": "I earn $5000 a month and spend $4500. What should I do?",
        "response": "Based on your situation, you are saving $500 per month which is 10% of your income. Here is my step by step analysis:\n\n**Current Situation:**\n- Monthly income: $5,000\n- Monthly expenses: $4,500\n- Current savings: $500 (10%)\n\n**Recommendations:**\n1. Build an emergency fund of 3-6 months expenses ($13,500-$27,000)\n2. Track your $4,500 expenses to find areas to cut\n3. Aim to increase savings rate to 20% ($1,000/month)\n4. Once emergency fund is built, start investing in index funds\n\n**Action Plan:**\n- Week 1: List all your expenses in categories\n- Week 2: Identify 3 areas to reduce spending\n- Month 2: Open a high-interest savings account\n- Month 3: Start automated savings of $500 extra"
    },
    {
        "prompt": "I am 25 years old and want to start investing in Australia. Where do I begin?",
        "response": "Starting to invest at 25 in Australia is excellent. Here is your step by step plan:\n\n**Before You Invest:**\n1. Build 3 months emergency fund first\n2. Pay off any high-interest debt (credit cards)\n3. Maximise your superannuation contributions\n\n**Australian Investment Strategy:**\n- Superannuation: Increase contributions to 15% (tax effective)\n- ETFs: Start with ASX 200 index fund (e.g. VAS) or S&P 500 ETF (VGS)\n- Minimum $200/month to start\n\n**Why This Works:**\n- $200/month at 25 with 7% annual return = $525,000 by age 65\n- ETFs are low cost and diversified\n- Super contributions are taxed at only 15%\n\n**First Steps:**\n1. Open a brokerage account (CommSec, SelfWealth, or Stake)\n2. Set up automatic monthly investment\n3. Never try to time the market"
    },
    {
        "prompt": "How does superannuation work in Australia and how can I maximise it?",
        "response": "Superannuation is Australia's compulsory retirement savings system. Here is everything you need to know:\n\n**How It Works:**\n- Your employer pays 11% of your salary into your super fund (2024 rate)\n- Money grows tax-free inside super\n- You can access it at preservation age (60 for most people)\n\n**How to Maximise It:**\n1. Concessional contributions (pre-tax): Up to $27,500/year taxed at 15%\n2. Non-concessional (after-tax): Up to $110,000/year tax free growth\n3. Salary sacrifice: Ask employer to contribute extra pre-tax dollars\n\n**Choosing the Right Fund:**\n- Compare fees (look for under 0.5% annual fee)\n- Check investment options and performance\n- Top performing funds: Australian Super, Hostplus, REST\n\n**Action Steps:**\n1. Log into ATO MyGov to find all your super accounts\n2. Consolidate multiple accounts to avoid duplicate fees\n3. Choose growth investment option if under 50"
    },
    {
        "prompt": "I want to buy a house in Sydney. How do I save for a deposit?",
        "response": "Buying in Sydney is challenging but achievable with the right plan. Here is how:\n\n**What You Need:**\n- Typical deposit: 20% to avoid LMI (Lenders Mortgage Insurance)\n- Sydney median house price ~$1.2M = $240,000 deposit\n- Plus stamp duty ~$50,000 and legal fees ~$3,000\n- Total needed: approximately $293,000\n\n**Australian Government Help:**\n- First Home Owner Grant: $10,000 for new homes under $600,000\n- First Home Super Saver Scheme: Save up to $50,000 in super for deposit\n- First Home Guarantee: Buy with only 5% deposit (no LMI) if eligible\n\n**Savings Strategy:**\n- Open a dedicated HISA (High Interest Savings Account)\n- ING, Macquarie and UBank currently offer best rates (5%+)\n- Save $3,000/month = deposit in 8 years\n- Save $5,000/month = deposit in 5 years\n\n**Action Plan:**\n1. Check First Home Guarantee eligibility today\n2. Open First Home Super Saver account\n3. Set up automatic savings transfer on pay day"
    },
    {
        "prompt": "I have $10,000 in credit card debt at 20% interest. What should I do?",
        "response": "Credit card debt at 20% is urgent. This is costing you $2,000 per year in interest alone. Here is your elimination plan:\n\n**The Math:**\n- $10,000 at 20% = $2,000/year in interest\n- Paying minimum only = 10+ years to pay off\n- Paying $500/month = debt free in 24 months saving $3,000 in interest\n\n**Immediate Steps:**\n1. Stop using the credit card today\n2. Call your bank and ask for a hardship rate reduction\n3. Consider balance transfer to 0% card (many Australian banks offer this)\n\n**Payoff Strategy (Avalanche Method):**\n- Pay minimum on everything else\n- Throw every extra dollar at the 20% debt\n- Once cleared, redirect that payment to savings\n\n**After Debt is Cleared:**\n1. Build $5,000 emergency fund\n2. Start investing what you were paying toward debt\n3. Keep one credit card for emergencies, pay in full monthly"
    }
]

custom_df = pd.DataFrame(custom_examples)
custom_df["quality_score"] = 99999  # Always keep these

# Combine custom + top dataset examples
df_final = pd.concat([custom_df[["prompt", "response"]], 
                       df_top[["prompt", "response"]]], ignore_index=True)
df_final = df_final.drop_duplicates(subset=["prompt"])
print(f"  Final dataset size: {len(df_final)} examples")

# ============================================================
# STEP 7: SAVE TO JSONL
# ============================================================
print("\n💾 Step 7: Saving to training_data.jsonl...")

with open("training_data.jsonl", "w", encoding="utf-8") as f:
    for _, row in df_final.iterrows():
        example = {
            "prompt": str(row["prompt"]).strip(),
            "response": str(row["response"]).strip()
        }
        f.write(json.dumps(example) + "\n")

print(f"✅ Saved {len(df_final)} examples to training_data.jsonl")

# ============================================================
# STEP 8: SHOW SUMMARY STATS
# ============================================================
print("\n" + "=" * 60)
print("📊 DATASET SUMMARY")
print("=" * 60)
print(f"Total training examples:     {len(df_final)}")
print(f"Custom Australian examples:  {len(custom_examples)}")
print(f"HuggingFace examples:        {len(df_final) - len(custom_examples)}")
print(f"Average prompt length:       {df_final['prompt'].str.len().mean():.0f} chars")
print(f"Average response length:     {df_final['response'].str.len().mean():.0f} chars")
print("\n✅ Data pipeline complete!")
print("\n🚀 Next step: Run this command to retrain your model:")
print("   ollama create financeai -f Modelfile")
print("=" * 60)