import streamlit as st
import re

st.set_page_config(page_title="ECObot - Waste Segregation Assistant", page_icon="♻️")

# ---------------------------
# 1. Waste category dictionary
# ---------------------------
WASTE_DB = {
    "Wet Waste (Organic/Biodegradable)": {
        "keywords": ["banana peel", "fruit peel", "vegetable peel", "food waste",
                     "tea leaves", "coffee grounds", "eggshell", "leftover food",
                     "flower", "leaf", "leaves", "meat", "fish bones", "bread",
                     "chai patti", "chai leaves", "sabzi chilka", "sabji peel",
                     "aloo chilka", "potato peel", "onion peel", "pyaz chilka",
                     "roti", "chapati", "rice", "chawal", "dal", "curd", "dahi",
                     "coconut shell", "nariyal", "puja flowers", "phool", "mala",
                     "banana leaf", "kela ka patta", "areca leaf plate", "pattal",
                     "tea bag", "used tea bag", "fruit waste", "kitchen waste"],
        "bin": "🟢 Green Bin",
        "bin_hi": "🟢 Hara (Green) Bin",
        "steps": [
            "Drain any excess liquid before throwing it in.",
            "Do not mix with plastic wrappers or packaging.",
            "Put it in the GREEN bin — it will be composted.",
            "If you compost at home, this can go straight into your compost pit."
        ],
        "steps_hi": [
            "Pehle extra paani/liquid nikaal do phenkne se pehle.",
            "Isse plastic wrapper ya packaging ke saath mat milao.",
            "Ise HARE bin mein daalo — yeh compost ban jayega.",
            "Agar ghar par compost karte ho, toh seedha compost pit mein daal sakte ho."
        ]
    },
    "Dry Waste (Recyclable)": {
        "keywords": ["plastic bottle", "paper", "newspaper", "cardboard", "carton",
                     "plastic bag", "wrapper", "glass bottle", "tin can", "metal can",
                     "aluminium foil", "magazine", "book", "plastic container",
                     "polythene", "polythene bag", "thaili", "carry bag", "kirana bag",
                     "doodh packet", "milk packet", "milk pouch", "dahi packet",
                     "curd packet", "oil packet", "ghee packet", "chip packet",
                     "kurkure packet", "namkeen packet", "biscuit wrapper",
                     "chocolate wrapper", "steel", "aluminium tiffin", "tiffin box",
                     "thermocol", "thermocol plate", "cutlery", "plastic cup",
                     "plastic plate", "kulhad", "matka", "clay pot"],
        "bin": "🔵 Blue Bin",
        "bin_hi": "🔵 Neela (Blue) Bin",
        "steps": [
            "Rinse it if it had food or liquid in it (helps recycling quality).",
            "Flatten boxes/bottles if possible to save space.",
            "Remove caps/lids if they're a different material and bin separately.",
            "Put it in the BLUE bin for recycling."
        ],
        "steps_hi": [
            "Agar isme khana ya liquid tha toh pehle dho lo.",
            "Ho sake toh box/bottle ko chapta (flatten) kar do, jagah bachegi.",
            "Agar cap/lid alag material ka hai toh usse alag rakho.",
            "Ise NEELE bin mein daalo, recycle ho jayega."
        ]
    },
    "E-Waste": {
        "keywords": ["battery", "phone", "charger", "cable", "laptop", "computer",
                     "tubelight", "bulb", "remote", "circuit", "wire", "headphone",
                     "earphone", "adapter", "cd", "pendrive", "mobile", "mobile phone",
                     "sim card", "cfl bulb", "led bulb", "inverter battery",
                     "car battery", "bike battery", "mixer grinder", "iron",
                     "electric iron", "fan", "table fan", "torch", "power bank",
                     "smart watch", "tablet", "keyboard", "mouse"],
        "bin": "🟡 E-Waste Collection Point",
        "bin_hi": "🟡 E-Waste Collection Point",
        "steps": [
            "Do NOT put this in your regular household bin.",
            "If it has a battery, remove it separately if possible.",
            "Wipe/erase personal data if it's a phone or storage device.",
            "Drop it off at an authorized e-waste collection center or a store take-back scheme."
        ],
        "steps_hi": [
            "Ise normal ghar ke bin mein bilkul mat daalo.",
            "Agar battery hai toh usse alag nikaal lo agar ho sake.",
            "Agar phone ya storage device hai toh personal data delete/wipe kar do.",
            "Kisi authorized e-waste collection center ya store take-back scheme mein jama karo."
        ]
    },
    "Hazardous Waste": {
        "keywords": ["paint", "chemical", "pesticide", "medicine", "expired medicine",
                     "syringe", "thermometer", "mercury", "acid", "sanitizer bottle",
                     "insecticide", "nail polish", "dawai", "expired dawai", "tablet strip",
                     "medicine strip", "insulin", "mosquito coil", "hit spray",
                     "phenyl bottle", "detergent bottle", "gutkha", "gutka pouch",
                     "paan masala pouch", "bidi", "cigarette", "firecracker waste",
                     "cracker waste", "hand sanitizer bottle"],
        "bin": "🔴 Hazardous Waste Point",
        "bin_hi": "🔴 Hazardous Waste Point",
        "steps": [
            "Do NOT pour liquids down the drain or mix with other trash.",
            "Keep it in its original container/labeled if possible.",
            "Keep away from children and pets until disposal.",
            "Hand over to a pharmacy (for medicines) or hazardous waste collection center."
        ],
        "steps_hi": [
            "Liquid ko drain mein mat baho, na hi doosre kachre ke saath milao.",
            "Ho sake toh apne original container mein hi rakho, label ke saath.",
            "Bachon aur pets se door rakho jab tak dispose na ho jaye.",
            "Dawai ho toh pharmacy mein do, warna hazardous waste collection center mein."
        ]
    },
    "Sanitary/Reject Waste": {
        "keywords": ["diaper", "sanitary pad", "napkin", "tissue", "cotton", "mask",
                     "bandage", "cigarette butt", "sanitary napkin", "nappy",
                     "face mask", "surgical mask", "ppe kit", "cotton swab",
                     "earbud", "band aid"],
        "bin": "⚫ Black/Reject Bin",
        "bin_hi": "⚫ Kala (Black) Bin",
        "steps": [
            "Wrap it fully in paper or a small bag — never leave it exposed.",
            "Do not flush it, even if the packaging says 'flushable'.",
            "Put it in the BLACK/reject bin, separate from wet and dry waste."
        ],
        "steps_hi": [
            "Isse pura paper ya chhoti bag mein wrap karo — khula mat chhodo.",
            "Flush mat karo, chahe packaging pe 'flushable' likha ho.",
            "Ise KAALE bin mein daalo, wet/dry waste se alag."
        ]
    },
}

ECO_FACTS = [
    "A single plastic bottle can take up to 450 years to decompose.",
    "Composting wet waste can reduce landfill volume by up to 30%.",
    "Recycling one aluminium can saves enough energy to run a TV for 3 hours.",
    "India generates over 62 million tonnes of waste every year.",
    "E-waste is the fastest-growing waste stream in the world.",
]

# ---------------------------
# 2. Matching logic
# ---------------------------
def match_waste(user_input):
    text = user_input.lower()
    for category, data in WASTE_DB.items():
        for keyword in data["keywords"]:
            if keyword in text:
                return category, data
    return None, None

def format_guide(category, data, lang="both"):
    lines = []
    if lang in ("en", "both"):
        lines.append(f"**{category}** → {data['bin']}")
        lines.append("**What to do:**")
        for i, step in enumerate(data["steps"], 1):
            lines.append(f"{i}. {step}")
    if lang == "both":
        lines.append("")
        lines.append("---")
        lines.append("")
    if lang in ("hi", "both"):
        lines.append(f"**{category}** → {data['bin_hi']}")
        lines.append("**Kya karna hai:**")
        for i, step in enumerate(data["steps_hi"], 1):
            lines.append(f"{i}. {step}")
    return "\n".join(lines)

# ---------------------------
# 3. AI fallback (optional - only runs if no keyword match)
#    Requires: pip install anthropic
#    Requires: an ANTHROPIC_API_KEY set as an environment variable
# ---------------------------
def ai_fallback(user_input, lang="both"):
    try:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
        lang_instruction = {
            "en": "Respond in English only.",
            "hi": "Respond in Hinglish only (Hindi words written in Roman/English script).",
            "both": "Respond in English first, then a '---' separator, then the same content in Hinglish (Hindi written in Roman script)."
        }[lang]
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=300,
            system=(
                "You are ECObot, a waste segregation guide for Indian users. Given an item, respond with: "
                "first line = category name and bin color (Wet/Green, Dry-Recyclable/Blue, E-Waste/Yellow, "
                "Hazardous/Red, or Sanitary-Reject/Black), then a numbered list of 2-4 short, practical "
                f"disposal steps. {lang_instruction} Keep it concise and actionable."
            ),
            messages=[{"role": "user", "content": user_input}]
        )
        return response.content[0].text
    except Exception as e:
        return ("I couldn't identify that item from my local database, and the "
                "AI fallback isn't configured (no API key set). Try describing "
                "it differently, e.g. 'plastic bottle' or 'old phone charger'.")

# ---------------------------
# 3b. Image classification via Google Gemini (free tier)
#    Requires: pip install google-generativeai pillow
#    Requires: GOOGLE_API_KEY set as an environment variable
# ---------------------------
def classify_image(image_bytes, media_type=None, lang="both"):
    try:
        import google.generativeai as genai
        from PIL import Image
        import io, os

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return ("No Google API key found. Set the GOOGLE_API_KEY environment variable "
                    "and restart the terminal, then try again.")

        genai.configure(api_key=api_key)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        model = genai.GenerativeModel("gemini-flash-latest")
        lang_instruction = {
            "en": "Respond in English only.",
            "hi": "Respond in Hinglish only (Hindi words written in Roman/English script).",
            "both": "Respond in English first, then a '---' separator line, then the same content again in Hinglish (Hindi written in Roman script)."
        }[lang]
        prompt = (
            "You are ECObot, a waste segregation guide for Indian users. Identify the item(s) "
            "in this image, then respond in this exact format: first line = category name and "
            "bin color (Wet/Green, Dry-Recyclable/Blue, E-Waste/Yellow, Hazardous/Red, or "
            f"Sanitary-Reject/Black), then a numbered list of 2-4 short, practical disposal steps. {lang_instruction}"
        )
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return (f"Image analysis failed ({e}). Make sure you've run: "
                "pip install google-generativeai pillow — and that GOOGLE_API_KEY is set correctly.")

# ---------------------------
# 4. Streamlit chat UI
# ---------------------------
st.title("♻️ ECObot")
st.caption("Your waste segregation assistant")

mode = st.radio("Choose mode:", ["💬 Free chat (type any item)", "🧭 Guided Q&A (step-by-step)"], horizontal=True)

if mode == "🧭 Guided Q&A (step-by-step)":
    st.subheader("Guided Waste Segregation Assistant")

    if "guided_step" not in st.session_state:
        st.session_state.guided_step = 1

    # Q1
    st.write("**Q1: Is your item wet/organic, or dry?**")
    q1 = st.radio("Select one:", ["Wet (food scraps, peels, leftovers)", "Dry (packaging, containers, paper)"], key="q1", index=None)

    if q1:
        if q1.startswith("Wet"):
            # Wet branch -> Q2
            st.write("**Q2: Does it still have a lot of liquid in it?**")
            q2 = st.radio("Select one:", ["Yes, it's wet/liquid-heavy", "No, mostly dry scraps"], key="q2_wet", index=None)
            if q2:
                if q2.startswith("Yes"):
                    st.success("**Answer:** Drain the liquid first, then put it in the 🟢 GREEN bin. "
                               "Liquid waste can contaminate other recyclables if mixed.")
                else:
                    st.success("**Answer:** Put it directly in the 🟢 GREEN bin for composting. "
                               "No extra prep needed.")
        else:
            # Dry branch -> Q2
            st.write("**Q2: Does it have a battery, plug, or electronic circuit?**")
            q2 = st.radio("Select one:", ["Yes, it's electronic/battery-powered", "No, it's plain packaging/paper/plastic"], key="q2_dry", index=None)
            if q2:
                if q2.startswith("Yes"):
                    # Q3 for e-waste branch
                    st.write("**Q3: Does it contain personal data (phone, laptop, pendrive)?**")
                    q3 = st.radio("Select one:", ["Yes", "No"], key="q3_edata", index=None)
                    if q3:
                        if q3 == "Yes":
                            st.success("**Answer:** Wipe/erase your data first, then drop it at an authorized "
                                       "🟡 E-WASTE collection point. Never bin it with household waste.")
                        else:
                            st.success("**Answer:** Take it to an authorized 🟡 E-WASTE collection point. "
                                       "Remove the battery separately if possible.")
                else:
                    st.success("**Answer:** Rinse if food-contaminated, then put it in the 🔵 BLUE bin for recycling.")

    st.divider()
    if st.button("Restart guided flow"):
        for k in ["q1", "q2_wet", "q2_dry", "q3_edata"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.stop()  # don't render free-chat UI below in guided mode


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm ECObot 👋 Tell me an item and I'll tell you how to dispose of it correctly."}
    ]
    st.session_state.count = 0

import random
if "fact" not in st.session_state:
    st.session_state.fact = random.choice(ECO_FACTS)

st.info(f"🌱 Eco-fact: {st.session_state.fact}")
st.metric("Items segregated this session", st.session_state.count)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

lang_choice = st.radio("Reply language / Jawab kis bhasha mein chahiye:",
                       ["English", "Hinglish", "Both"], horizontal=True, index=2)
lang_map = {"English": "en", "Hinglish": "hi", "Both": "both"}

with st.expander("📷 Or upload/take a photo of the item"):
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    camera_image = st.camera_input("Or take a photo")

    image_file = uploaded_image or camera_image
    if image_file is not None:
        st.image(image_file, width=200)
        if st.button("Identify this item"):
            image_bytes = image_file.getvalue()
            media_type = image_file.type if hasattr(image_file, "type") and image_file.type else "image/png"

            st.session_state.messages.append({"role": "user", "content": "[Uploaded an image]"})
            reply = classify_image(image_bytes, media_type, lang=lang_map[lang_choice])
            st.session_state.count += 1
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

st.write("**Quick pick — tap a common item:**")
quick_items = ["chai patti", "milk packet", "old charger", "gutkha pouch", "diaper"]
cols = st.columns(len(quick_items))
quick_pick = None
for col, item in zip(cols, quick_items):
    if col.button(item):
        quick_pick = item

user_input = st.chat_input("Type any item, e.g. 'newspaper' or 'broken charger'...")
final_input = quick_pick or user_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.write(final_input)

    category, data = match_waste(final_input)

    if category:
        reply = format_guide(category, data, lang=lang_map[lang_choice])
        st.session_state.count += 1
    else:
        reply = ai_fallback(final_input, lang=lang_map[lang_choice])
        st.session_state.count += 1

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
    st.rerun()
