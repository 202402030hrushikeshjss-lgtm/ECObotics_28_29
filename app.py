import streamlit as st
import re

st.set_page_config(page_title="ECObot - Waste Segregation Assistant", page_icon="♻️")

# ---------------------------
# 1. Waste category dictionary
# ---------------------------
WASTE_DB = {
    "Wet Waste (Organic/Biodegradable)": {
        "keywords": ["banana peel", "fruit peel", "vegetable peel", "food waste",
                     "banana", "bananas", "apple", "orange peel", "mango peel",
                     "fruit", "vegetables", "vegetable",
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
                "Hazardous/Red, Sanitary-Reject/Black, or Biomedical-Anatomical/Yellow-authorized-facility-only), then a numbered list of 2-4 short, practical "
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
# 3b. Image classification via FREE, fully OFFLINE local model
#    Requires: pip install transformers torch pillow
#    First run downloads the model (~1GB) from huggingface.co (the main site,
#    NOT the api-inference subdomain) - needs internet once, then works fully offline.
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
        import io
        processor, model = load_caption_model()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=30)
        caption = processor.decode(out[0], skip_special_tokens=True).strip()
        if not caption:
            return None, "Could not generate a caption for this image."
        return caption, None
    except Exception as e:
        return None, (f"Local image model failed to load or run ({e}). Make sure you've run: "
                       "pip install transformers torch pillow — and that you had internet access "
                       "for the first run (one-time model download).")

def classify_image(image_bytes, media_type=None, lang="both"):
    caption, error = get_image_caption(image_bytes)
    if error:
        return f"Image analysis failed. {error}"

    # Feed the caption into our existing keyword dictionary, same as Free Chat mode
    category, data = match_waste(caption)
    if category:
        guide = format_guide(category, data, lang=lang)
        return f"Identified item: {caption}\n\n{guide}"
    else:
        # Fall back to the AI text fallback (Gemini) using the caption as the query,
        # or a plain message if that's also unavailable
        fallback_reply = ai_fallback(caption, lang=lang)
        return f"Identified item: {caption}\n\n{fallback_reply}"


# ---------------------------
# 3c. Interactive guided flow
# ---------------------------
BIO = "Biomedical/Anatomical Waste"
HAZ = "Hazardous Waste"
SAN = "Sanitary/Reject Waste"
WET = "Wet Waste (Organic/Biodegradable)"
DRY = "Dry Waste (Recyclable)"
EWS = "E-Waste"

# Each node: question (en/hi) + options [(label, next)].
# next = another node id (str) OR a result dict {"cat", "note", "note_hi"}.
GUIDED_TREE = {
    "start": {
        "q": "Is this blood, human/animal tissue, body parts, or medical/surgical waste?",
        "q_hi": "Kya yeh blood, human/animal tissue, body part ya medical/surgical waste hai?",
        "opts": [
            ("No, regular household waste", "type"),
            ("Yes, biomedical waste", {"cat": BIO, "note": "", "note_hi": ""}),
        ],
    },
    "type": {
        "q": "What kind of item is it?",
        "q_hi": "Yeh kis type ka item hai?",
        "opts": [
            ("🍌 Food / organic", "wet"),
            ("📦 Packaging (paper, plastic, glass, metal)", "pack"),
            ("🔌 Electronic / battery", "edata"),
            ("💊 Medicine / chemical / paint / pesticide", {"cat": HAZ, "note": "", "note_hi": ""}),
            ("🧻 Hygiene (diaper, pad, mask, bandage, tissue)", {"cat": SAN, "note": "", "note_hi": ""}),
            ("❓ Not sure / something else", {"cat": None, "note": "", "note_hi": ""}),
        ],
    },
    "wet": {
        "q": "Does it still have a lot of liquid in it?",
        "q_hi": "Kya isme abhi bhi bahut liquid hai?",
        "opts": [
            ("Yes, liquid-heavy", {"cat": WET,
                                   "note": "Drain the liquid first so it doesn't leak or contaminate other bins.",
                                   "note_hi": "Pehle liquid nikaal lo taaki doosre bins gande na ho."}),
            ("No, mostly dry scraps", {"cat": WET, "note": "", "note_hi": ""}),
        ],
    },
    "pack": {
        "q": "Is it clean, or does it have food/liquid residue?",
        "q_hi": "Kya yeh saaf hai, ya isme khana/liquid laga hai?",
        "opts": [
            ("Clean and dry", {"cat": DRY, "note": "", "note_hi": ""}),
            ("Has food/liquid residue", {"cat": DRY,
                                         "note": "Rinse it first. If it can't be cleaned (very greasy), use the black reject bin.",
                                         "note_hi": "Pehle dho lo. Agar saaf nahi ho sakta (bahut chikna), toh kaale reject bin mein daalo."}),
        ],
    },
    "edata": {
        "q": "Does it store personal data (phone, laptop, pendrive)?",
        "q_hi": "Kya isme personal data store hota hai (phone, laptop, pendrive)?",
        "opts": [
            ("Yes", {"cat": EWS, "note": "Back up and wipe your data BEFORE handing it over.",
                     "note_hi": "Dene se PEHLE apna data backup aur wipe karo."}),
            ("No", {"cat": EWS, "note": "", "note_hi": ""}),
        ],
    },
}

GUIDED_WHY = {
    WET: "Wet waste becomes compost. Mixing it with plastic ruins both.",
    DRY: "Clean dry waste can be recycled. Dirty recyclables often end up in landfill.",
    EWS: "E-waste holds toxic metals and valuable materials, so it needs proper recycling.",
    HAZ: "Chemicals and medicines can poison soil and water if binned or poured away.",
    SAN: "Sanitary waste is a health risk to sanitation workers, so it is kept separate.",
    BIO: "Biomedical waste can carry infection, so only authorized facilities may handle it.",
}


def _g_pick(node_id, question, label, nxt):
    ss = st.session_state
    ss.g_trail.append((node_id, question, label))
    if isinstance(nxt, dict):
        ss.g_result = nxt
        ss.g_done += 1
        ss.g_celebrate = nxt["cat"] not in (None, BIO)
    else:
        ss.g_node = nxt


def _g_back():
    ss = st.session_state
    if ss.g_trail:
        if ss.g_result is not None:
            ss.g_done = max(0, ss.g_done - 1)
        node_id, _, _ = ss.g_trail.pop()
        ss.g_node = node_id
        ss.g_result = None
        ss.g_celebrate = False


def _g_reset():
    ss = st.session_state
    ss.g_node, ss.g_trail, ss.g_result, ss.g_celebrate = "start", [], None, False


def render_guided():
    ss = st.session_state
    ss.setdefault("g_node", "start")
    ss.setdefault("g_trail", [])
    ss.setdefault("g_result", None)
    ss.setdefault("g_done", 0)
    ss.setdefault("g_celebrate", False)

    st.subheader("🧭 Guided Waste Segregation Assistant")
    g_lang_choice = st.radio("Language / Bhasha:", ["English", "Hinglish", "Both"],
                             horizontal=True, index=2, key="g_lang")
    glang = {"English": "en", "Hinglish": "hi", "Both": "both"}[g_lang_choice]
    st.metric("Items guided this session", ss.g_done)

    # Trail of answers so far
    if ss.g_trail:
        st.caption("Your answers: " + "  →  ".join(label for _, _, label in ss.g_trail))

    # ---------- RESULT ----------
    if ss.g_result is not None:
        res = ss.g_result
        cat = res["cat"]
        st.progress(1.0, text="Done")

        if cat is None:
            st.info("I can't place this one with a few questions. Switch to **💬 Free chat** and type "
                    "the item's name (or ask a question) and I'll look it up.")
        else:
            data = WASTE_DB[cat]
            box = st.error if cat == BIO else st.success
            box(format_guide(cat, data, lang=glang))
            if res["note"]:
                if glang in ("en", "both"):
                    st.warning("⚠️ " + res["note"])
                if glang in ("hi", "both"):
                    st.warning("⚠️ " + res["note_hi"])
            st.info("💡 Why: " + GUIDED_WHY[cat])
            if ss.g_celebrate:
                st.balloons()
                ss.g_celebrate = False

        c1, c2 = st.columns(2)
        c1.button("⬅ Back (change last answer)", on_click=_g_back, key="g_back_res")
        c2.button("🔄 Sort another item", on_click=_g_reset, key="g_new")
        return

    # ---------- QUESTION ----------
    node = GUIDED_TREE[ss.g_node]
    st.progress(min(len(ss.g_trail) / 3, 0.9), text=f"Step {len(ss.g_trail) + 1}")

    if glang in ("en", "both"):
        st.markdown(f"### {node['q']}")
    if glang in ("hi", "both"):
        (st.caption if glang == "both" else st.markdown)(node["q_hi"])

    for i, (label, nxt) in enumerate(node["opts"]):
        st.button(label, key=f"g_{ss.g_node}_{i}", use_container_width=True,
                  on_click=_g_pick, args=(ss.g_node, node["q"], label, nxt))

    if ss.g_trail:
        st.button("⬅ Back", on_click=_g_back, key="g_back_q")


# ---------------------------
# 4. Streamlit chat UI
# ---------------------------
st.title("♻️ ECObot")
st.caption("Your waste segregation assistant")

mode = st.radio("Choose mode:", ["💬 Free chat (type any item)", "🧭 Guided Q&A (step-by-step)"], horizontal=True)

if mode == "🧭 Guided Q&A (step-by-step)":
    render_guided()
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
