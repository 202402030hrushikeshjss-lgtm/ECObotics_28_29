import streamlit as st
import re
import os
import io
import random
import hashlib

st.set_page_config(page_title="ECObot - Waste Segregation Assistant", page_icon="♻️")

# Change this to whichever Gemini model already works in your account.
GEMINI_MODEL = "gemini-2.5-flash"

# ---------------------------
# 1. Waste category dictionary
# ---------------------------
WASTE_DB = {
    "Wet Waste (Organic/Biodegradable)": {
        "keywords": ["banana peel", "fruit peel", "vegetable peel", "food waste",
                     "banana", "apple", "orange peel", "mango peel",
                     "fruit", "vegetable",
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
        "keywords": ["plastic bottle", "bottle", "water bottle", "paper", "newspaper", "cardboard", "carton",
                     "plastic bag", "wrapper", "glass bottle", "tin can", "metal can", "can",
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
                     "cracker waste", "hand sanitizer bottle", "hand sanitizer"],
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
    "Biomedical/Anatomical Waste": {
        "keywords": ["blood", "blood bag", "human tissue", "body part", "amputated part",
                     "placenta", "body fluid", "animal carcass", "dead animal",
                     "animal remains", "animal tissue", "slaughterhouse waste",
                     "surgical waste", "human waste", "anatomical waste",
                     "biopsy sample", "dialysis waste", "blood soaked", "used syringe with blood"],
        "bin": "🟨 Yellow Biomedical Bag (Authorized Facility Only)",
        "bin_hi": "🟨 Yellow Biomedical Bag (Authorized Facility Only)",
        "steps": [
            "Do NOT put this in any household bin — this is biomedical/anatomical waste.",
            "This must only be handled by a hospital, clinic, veterinary facility, or authorized biomedical waste operator.",
            "If you encounter this outside a medical setting, contact local municipal health authorities immediately.",
            "Never attempt to handle, transport, or dispose of this yourself without protective equipment."
        ],
        "steps_hi": [
            "Isse kisi bhi ghar ke bin mein bilkul mat daalo — yeh biomedical/anatomical waste hai.",
            "Ise sirf hospital, clinic, veterinary facility ya authorized biomedical waste operator hi handle kare.",
            "Agar yeh kahin ghar ke bahar mile, turant local municipal health authorities ko contact karo.",
            "Bina protective equipment ke ise khud handle ya transport karne ki koshish kabhi mat karo."
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

FALLBACK_ERROR_PREFIX = "I couldn't"

# ---------------------------
# 2. Matching logic
#    Whole-word match + longest keyword wins across ALL categories,
#    so "human tissue" beats "tissue" and "hand sanitizer bottle" beats "bottle".
# ---------------------------
def match_waste(user_input):
    text = user_input.lower()
    best_len, best_cat, best_data = 0, None, None
    for category, data in WASTE_DB.items():
        for kw in data["keywords"]:
            if len(kw) > best_len and re.search(rf"\b{re.escape(kw)}(?:s|es)?\b", text):
                best_len, best_cat, best_data = len(kw), category, data
    return best_cat, best_data


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
# 3. Gemini fallback (item not in dictionary, or a general question)
#    Key comes from Streamlit secrets or an environment variable - never hardcode it.
# ---------------------------
def get_google_key():
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return os.environ.get("GOOGLE_API_KEY")


def get_gemini_model():
    import google.generativeai as genai
    key = get_google_key()
    if not key:
        raise RuntimeError("GOOGLE_API_KEY not set")
    genai.configure(api_key=key)
    return genai.GenerativeModel(GEMINI_MODEL)


def ai_fallback(user_input, lang="both"):
    """Returns (text, ok). ok=False means the AI call failed."""
    lang_instruction = {
        "en": "Respond in English only.",
        "hi": "Respond in Hinglish only (Hindi words written in Roman/English script).",
        "both": "Respond in English first, then a '---' separator, then the same content in Hinglish (Hindi written in Roman script).",
    }[lang]
    prompt = (
        "You are ECObot, a waste segregation and sustainability assistant for Indian users.\n"
        "Decide what the user input is:\n"
        "1) A waste ITEM: reply with the first line = category and bin "
        "(Wet/Green, Dry-Recyclable/Blue, E-Waste/Yellow collection point, Hazardous/Red, "
        "Sanitary-Reject/Black, or Biomedical/Yellow-authorized-facility-only), then 2-4 short numbered disposal steps.\n"
        "2) A QUESTION about waste, recycling, composting or sustainability: answer it clearly in 3-6 sentences.\n"
        "3) Unrelated to waste/environment: politely say you only help with waste and sustainability.\n"
        "If the item involves blood, human/animal tissue or medical waste, say it must go only to an "
        "authorized biomedical waste facility. If you are unsure, say so instead of guessing. "
        "Bin colors can vary by municipality.\n"
        f"{lang_instruction} Keep it concise.\n\nUser input: {user_input}"
    )
    try:
        model = get_gemini_model()
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        if not text:
            raise RuntimeError("empty response")
        return text, True
    except Exception:
        return (f"{FALLBACK_ERROR_PREFIX} answer that right now (AI service unavailable or not configured). "
                "Try a simpler item name, e.g. 'plastic bottle' or 'old phone charger'."), False


# ---------------------------
# 3b. Image classification via local BLIP caption model
#     Requires: transformers, torch, pillow. Heavy for free-tier hosting.
# ---------------------------
@st.cache_resource
def load_caption_model():
    from transformers import BlipProcessor, BlipForConditionalGeneration
    model_name = "Salesforce/blip-image-captioning-base"
    processor = BlipProcessor.from_pretrained(model_name)
    model = BlipForConditionalGeneration.from_pretrained(model_name)
    return processor, model


def get_image_caption(image_bytes):
    try:
        from PIL import Image
        processor, model = load_caption_model()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=30)
        caption = processor.decode(out[0], skip_special_tokens=True).strip()
        if not caption:
            return None, "Could not generate a caption for this image."
        return caption, None
    except Exception as e:
        return None, f"Local image model failed to load or run ({e})."


def classify_image(image_bytes, lang="both"):
    """Returns (reply, ok)."""
    caption, error = get_image_caption(image_bytes)
    if error:
        return f"{FALLBACK_ERROR_PREFIX} analyse the image. {error}", False
    category, data = match_waste(caption)
    if category:
        return f"Identified (approximate): {caption}\n\n{format_guide(category, data, lang=lang)}", True
    reply, ok = ai_fallback(caption, lang=lang)
    return f"Identified (approximate): {caption}\n\n{reply}", ok


# ---------------------------
# 3c. Voice (optional): Gemini transcription + gTTS speech (English only)
# ---------------------------
def transcribe(audio_bytes):
    try:
        model = get_gemini_model()
        r = model.generate_content([
            "Transcribe this audio exactly. If it is Hindi, write it in Roman script (Hinglish). "
            "Output only the transcript.",
            {"mime_type": "audio/wav", "data": audio_bytes},
        ])
        return (r.text or "").strip()
    except Exception:
        return ""


def speak(text):
    try:
        from gtts import gTTS
        english = text.split("---")[0]
        clean = re.sub(r"[^\w\s.,!?'-]", " ", english)
        clean = re.sub(r"\s+", " ", clean).strip()[:500]
        if not clean:
            return
        buf = io.BytesIO()
        gTTS(text=clean, lang="en").write_to_fp(buf)
        st.audio(buf.getvalue(), format="audio/mp3", autoplay=True)
    except Exception:
        pass


# ---------------------------
# 4. Streamlit UI
# ---------------------------
st.title("♻️ ECObot")
st.caption("Your waste segregation assistant. Bin colors may vary by municipality — follow your local rules if they differ.")

mode = st.radio("Choose mode:", ["💬 Free chat (type any item)", "🧭 Guided Q&A (step-by-step)"], horizontal=True)

GUIDED_KEYS = ["q0", "q1", "q2_wet", "q2_dry", "q3_edata"]


def reset_guided():
    for k in GUIDED_KEYS:
        st.session_state.pop(k, None)


if mode == "🧭 Guided Q&A (step-by-step)":
    st.subheader("Guided Waste Segregation Assistant")

    # Q0: safety gate
    st.write("**Q0: Is this blood, human/animal tissue, body parts, or medical/surgical waste?**")
    q0 = st.radio("Select one:", ["No, it's regular household waste",
                                  "Yes, it's biomedical/anatomical waste"], key="q0", index=None)

    if q0 == "Yes, it's biomedical/anatomical waste":
        st.error("**Answer:** Do NOT put this in any household bin. This must be handled only by an "
                 "authorized hospital, clinic, veterinary facility, or biomedical waste operator. "
                 "Contact local municipal health authorities if found outside a medical setting.")
        st.button("Restart guided flow", key="restart_q0", on_click=reset_guided)
        st.stop()

    if q0:
        # Q1: broad type
        st.write("**Q1: What kind of item is it?**")
        q1 = st.radio("Select one:", [
            "Food / organic (peels, leftovers, flowers)",
            "Packaging (paper, plastic, glass, metal)",
            "Electronic / battery-powered",
            "Medicine / chemical / paint / pesticide",
            "Hygiene (diaper, pad, mask, bandage, tissue)",
        ], key="q1", index=None)

        if q1:
            if q1.startswith("Food"):
                st.write("**Q2: Does it still have a lot of liquid in it?**")
                q2 = st.radio("Select one:", ["Yes, it's wet/liquid-heavy", "No, mostly dry scraps"],
                              key="q2_wet", index=None)
                if q2:
                    if q2.startswith("Yes"):
                        st.success("**Answer:** Drain the liquid first, then put it in the 🟢 GREEN bin. "
                                   "Liquid waste can contaminate other recyclables if mixed.")
                    else:
                        st.success("**Answer:** Put it directly in the 🟢 GREEN bin for composting. "
                                   "No extra prep needed.")

            elif q1.startswith("Packaging"):
                st.write("**Q2: Is it contaminated with food or liquid?**")
                q2 = st.radio("Select one:", ["Yes, it has food/liquid residue", "No, it's clean"],
                              key="q2_dry", index=None)
                if q2:
                    if q2.startswith("Yes"):
                        st.success("**Answer:** Rinse it first, then put it in the 🔵 BLUE bin for recycling. "
                                   "If it can't be cleaned (greasy paper, for example), use the ⚫ BLACK/reject bin.")
                    else:
                        st.success("**Answer:** Put it in the 🔵 BLUE bin for recycling. "
                                   "Flatten boxes and bottles to save space.")

            elif q1.startswith("Electronic"):
                st.write("**Q2: Does it contain personal data (phone, laptop, pendrive)?**")
                q3 = st.radio("Select one:", ["Yes", "No"], key="q3_edata", index=None)
                if q3:
                    if q3 == "Yes":
                        st.success("**Answer:** Wipe/erase your data first, then drop it at an authorized "
                                   "🟡 E-WASTE collection point. Never bin it with household waste.")
                    else:
                        st.success("**Answer:** Take it to an authorized 🟡 E-WASTE collection point. "
                                   "Remove the battery separately if possible.")

            elif q1.startswith("Medicine"):
                st.success("**Answer:** Do NOT pour it down the drain or mix it with other trash. Keep it in its "
                           "original container, away from children and pets, and hand it to a pharmacy or a "
                           "🔴 HAZARDOUS waste collection point.")

            else:
                st.success("**Answer:** Wrap it fully in paper or a small bag, do NOT flush it, and put it in "
                           "the ⚫ BLACK/reject bin, separate from wet and dry waste.")

    st.divider()
    st.button("Restart guided flow", on_click=reset_guided)
    st.stop()


# ---------------------------
# Free chat mode
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm ECObot 👋 Tell me an item, or ask a question about waste, and I'll help."}
    ]
    st.session_state.count = 0

if "fact" not in st.session_state:
    st.session_state.fact = random.choice(ECO_FACTS)

st.info(f"🌱 Eco-fact: {st.session_state.fact}")
st.metric("Items segregated this session", st.session_state.count)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Play queued voice reply (set on the previous run, before st.rerun)
if st.session_state.get("to_speak"):
    speak(st.session_state.pop("to_speak"))

lang_choice = st.radio("Reply language / Jawab kis bhasha mein chahiye:",
                       ["English", "Hinglish", "Both"], horizontal=True, index=2)
lang = {"English": "en", "Hinglish": "hi", "Both": "both"}[lang_choice]

# Image input
with st.expander("📷 Or upload/take a photo of the item"):
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    camera_image = st.camera_input("Or take a photo")
    image_file = uploaded_image or camera_image
    if image_file is not None:
        st.image(image_file, width=200)
        if st.button("Identify this item"):
            st.session_state.messages.append({"role": "user", "content": "[Uploaded an image]"})
            reply, ok = classify_image(image_file.getvalue(), lang=lang)
            if ok:
                st.session_state.count += 1
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# Voice input (needs Streamlit >= 1.39)
voice_text = None
if hasattr(st, "audio_input"):
    with st.expander("🎤 Ask by voice (replies are spoken in English only)"):
        audio = st.audio_input("Record your question")
        if audio is not None:
            audio_bytes = audio.getvalue()
            audio_hash = hashlib.md5(audio_bytes).hexdigest()
            if st.session_state.get("last_audio") != audio_hash:
                st.session_state.last_audio = audio_hash
                with st.spinner("Transcribing..."):
                    heard = transcribe(audio_bytes)
                if heard:
                    voice_text = heard
                else:
                    st.warning("Couldn't understand the audio. Please try again or type instead.")

# Quick picks
st.write("**Quick pick — tap a common item:**")
quick_items = ["chai patti", "milk packet", "old charger", "gutkha pouch", "diaper"]
cols = st.columns(len(quick_items))
quick_pick = None
for col, item in zip(cols, quick_items):
    if col.button(item):
        quick_pick = item

user_input = st.chat_input("Type an item or ask a question, e.g. 'newspaper' or 'why segregate waste?'")
final_input = quick_pick or user_input or voice_text
from_voice = bool(voice_text) and not (quick_pick or user_input)

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})

    category, data = match_waste(final_input)
    if category:
        reply = format_guide(category, data, lang=lang)
        ok = True
    else:
        reply, ok = ai_fallback(final_input, lang=lang)

    if ok:
        st.session_state.count += 1
    st.session_state.messages.append({"role": "assistant", "content": reply})

    if from_voice and ok and lang != "hi":
        st.session_state.to_speak = reply

    st.rerun()
