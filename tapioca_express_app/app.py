import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="TapiocaExpress - Custom Drink Calculator",
    page_icon="generated-icon.png",
    layout="centered"
)

MIN_ML = 1
MAX_ML = 1000

DRINK_CATEGORIES = {
    "Classic Milk Tea": {
        "price_per_ml": 0.0075,
        "base_price": "$5.09 - $5.49",
        "description": "Traditional milk tea flavors"
    },
    "Flavored Milk Tea with Boba": {
        "price_per_ml": 0.0080,
        "base_price": "$5.60",
        "description": "Milk tea with tapioca pearls"
    },
    "Plain Tea (Black/Green/Fruit)": {
        "price_per_ml": 0.0071,
        "base_price": "$4.99",
        "description": "Simple, refreshing tea options"
    },
    "Snow Bubble / Slush / Smoothie": {
        "price_per_ml": 0.0091,
        "base_price": "$6.29 - $6.49",
        "description": "Icy blended drinks"
    },
    "Snow Bubble (Large Specials)": {
        "price_per_ml": 0.0100,
        "base_price": "$6.99",
        "description": "Premium large snow bubbles"
    },
    "Soda / Italian Soda": {
        "price_per_ml": 0.0100,
        "base_price": "$6.99",
        "description": "Carbonated refreshments"
    },
    "Icy / Fruilush / Fruit-Tea": {
        "price_per_ml": 0.0084,
        "base_price": "~$5.85",
        "description": "Fruity icy drinks"
    },
    "Juice / Fresh-Fruit Drinks": {
        "price_per_ml": 0.0078,
        "base_price": "~$5.49",
        "description": "Fresh fruit beverages"
    },
    "Milk Drinks with Toppings": {
        "price_per_ml": 0.0100,
        "base_price": "~$6.99",
        "description": "Creamy drinks with extras"
    },
    "Seasonal / Premium Drinks": {
        "price_per_ml": 0.0100,
        "base_price": "~$6.99",
        "description": "Limited edition & specialty lattes"
    }
}

PRESET_SIZES = {
    "Small (250ml)": 250,
    "Medium (500ml)": 500,
    "Large (700ml)": 700,
    "Extra Large (1000ml)": 1000,
    "Custom": 0
}

if "initialized" not in st.session_state:
    st.session_state.cart = []
    st.session_state.order_history = []
    st.session_state.animation_key = 0
    st.session_state.selected_volume = 500
    st.session_state.initialized = True

def get_size_label(volume):
    if volume == 250:
        return "Small"
    elif volume == 500:
        return "Medium"
    elif volume == 700:
        return "Large"
    elif volume == 1000:
        return "Extra Large"
    else:
        return "Custom"

def get_fill_percentage(volume):
    return min(100, (volume / MAX_ML) * 100)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .price-display {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    
    /* No Ice Banner */
    .no-ice-banner {
        background: linear-gradient(135deg, #1a5f7a 0%, #2E86AB 50%, #57a0d3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3);
        position: relative;
        overflow: hidden;
    }
    .no-ice-banner::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255,255,255,0.1) 50%,
            transparent 70%
        );
        animation: shimmer 3s infinite;
    }
    @keyframes shimmer {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    .no-ice-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    .no-ice-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    .no-ice-badge {
        display: inline-block;
        background: #FFD700;
        color: #1a5f7a;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        margin-top: 0.8rem;
        position: relative;
        z-index: 1;
    }
    
    /* Category Card */
    .category-info {
        background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    .category-name {
        font-size: 1.3rem;
        font-weight: bold;
        color: #856404;
        margin-bottom: 0.3rem;
    }
    .category-price {
        font-size: 1rem;
        color: #666;
    }
    
    /* Pouring Animation Container */
    .pour-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 320px;
        margin: 1.5rem 0;
        position: relative;
    }
    
    /* Pitcher */
    .pitcher {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(20px);
        width: 60px;
        height: 80px;
        animation: tilt-pour 2s ease-in-out forwards;
        transform-origin: bottom left;
        z-index: 10;
    }
    .pitcher-body {
        width: 50px;
        height: 60px;
        background: linear-gradient(135deg, #87CEEB 0%, #5BA3C6 100%);
        border: 3px solid #4A90A4;
        border-radius: 5px 5px 10px 10px;
        position: relative;
    }
    .pitcher-handle {
        position: absolute;
        right: -15px;
        top: 10px;
        width: 15px;
        height: 35px;
        border: 3px solid #4A90A4;
        border-left: none;
        border-radius: 0 10px 10px 0;
        background: transparent;
    }
    .pitcher-spout {
        position: absolute;
        left: -8px;
        top: 0;
        width: 15px;
        height: 20px;
        background: #5BA3C6;
        border: 3px solid #4A90A4;
        border-right: none;
        border-radius: 10px 0 0 0;
        clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 100%);
    }
    
    @keyframes tilt-pour {
        0% { transform: translateX(20px) rotate(0deg); }
        20% { transform: translateX(20px) rotate(-45deg); }
        80% { transform: translateX(20px) rotate(-45deg); }
        100% { transform: translateX(20px) rotate(0deg); }
    }
    
    /* Pouring Stream */
    .pour-stream {
        position: absolute;
        top: 60px;
        left: 50%;
        transform: translateX(-25px);
        width: 12px;
        height: 0;
        background: linear-gradient(to bottom, #DEB887, #F5DEB3);
        border-radius: 0 0 6px 6px;
        animation: pour-flow 2s ease-in-out forwards;
        opacity: 0;
        z-index: 5;
    }
    
    @keyframes pour-flow {
        0% { height: 0; opacity: 0; }
        15% { height: 0; opacity: 0; }
        25% { height: 120px; opacity: 1; }
        75% { height: 120px; opacity: 1; }
        85% { height: 0; opacity: 0; }
        100% { height: 0; opacity: 0; }
    }
    
    /* Transparent Cup with Scale */
    .cup-with-scale {
        position: relative;
        display: flex;
        align-items: flex-end;
    }
    
    .scale-markers {
        position: absolute;
        right: -50px;
        bottom: 0;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        font-size: 0.65rem;
        color: #666;
    }
    .scale-mark {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .scale-line {
        width: 10px;
        height: 2px;
        background: #999;
    }
    
    .transparent-cup {
        width: 100px;
        height: 180px;
        border: 4px solid rgba(150, 150, 150, 0.6);
        border-radius: 0 0 20px 20px;
        position: relative;
        background: linear-gradient(to right, 
            rgba(255,255,255,0.3) 0%, 
            rgba(255,255,255,0.1) 50%, 
            rgba(255,255,255,0.3) 100%);
        overflow: hidden;
        box-shadow: inset 0 0 20px rgba(255,255,255,0.5);
    }
    
    .liquid-fill {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, #DEB887, #F5DEB3);
        border-radius: 0 0 16px 16px;
        animation: fill-up 2s ease-out forwards;
    }
    
    @keyframes fill-up {
        0% { height: 0; }
        25% { height: 0; }
        100% { height: var(--fill-height); }
    }
    
    .bubbles-animated {
        position: absolute;
        bottom: 5px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 5px;
        opacity: 0;
        animation: show-bubbles 2s ease-out forwards;
    }
    
    @keyframes show-bubbles {
        0%, 90% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    .bubble {
        width: 12px;
        height: 12px;
        background: #4A3728;
        border-radius: 50%;
    }
    
    .ml-indicator {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: bold;
        opacity: 0;
        animation: show-indicator 2s ease-out forwards;
        z-index: 20;
    }
    
    @keyframes show-indicator {
        0%, 80% { opacity: 0; transform: translateX(-50%) translateY(10px); }
        100% { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
    
    .volume-label {
        text-align: center;
        margin-top: 1rem;
        font-size: 1.2rem;
        color: #333;
        font-weight: 600;
    }
    
    /* Receipt styles */
    .receipt {
        background: #fffef5;
        border: 2px dashed #ccc;
        padding: 1.5rem;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
    }
    .receipt-header {
        text-align: center;
        border-bottom: 1px dashed #999;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .receipt-item {
        display: flex;
        justify-content: space-between;
        margin: 0.3rem 0;
    }
    .receipt-total {
        border-top: 1px dashed #999;
        padding-top: 0.5rem;
        margin-top: 0.5rem;
        font-weight: bold;
    }
    
    /* Pricing table */
    .pricing-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .pricing-table th {
        background: #2E86AB;
        color: white;
        padding: 0.5rem;
        text-align: left;
    }
    .pricing-table td {
        padding: 0.5rem;
        border-bottom: 1px solid #ddd;
    }
    .pricing-table tr:hover {
        background: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("generated-icon.png", width=100)
st.markdown("</div>", unsafe_allow_html=True)

st.title("TapiocaExpress")
st.subheader("Custom Liquid Measurement Calculator")

st.markdown("""
<div class='no-ice-banner'>
    <div class='no-ice-title'>100% PURE LIQUID - NO ICE!</div>
    <div class='no-ice-subtitle'>
        When you order 500ml, you get exactly 500ml of delicious drink.<br>
        No ice taking up space. No surprises. Just pure refreshment.
    </div>
    <div class='no-ice-badge'>THE ONLY BRAND THAT DOES THIS</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div class='info-box'>
    <strong>Welcome to TapiocaExpress!</strong><br>
    Customize your drink by selecting a category and entering the exact amount of liquid you want. 
    Each drink category has its own pricing based on ingredients and preparation.<br><br>
    <strong>Why choose us?</strong> Unlike other brands that fill your cup with ice, 
    every milliliter you pay for is pure, delicious drink!
</div>
""", unsafe_allow_html=True)

st.markdown("### Step 1: Select Your Drink Category")

category_options = list(DRINK_CATEGORIES.keys())
selected_category = st.selectbox(
    "Choose a drink category:",
    category_options,
    index=0,
    key="category_selection"
)

category_info = DRINK_CATEGORIES[selected_category]
price_per_ml = category_info["price_per_ml"]

st.markdown(f"""
<div class='category-info'>
    <div class='category-name'>{selected_category}</div>
    <div class='category-price'>
        {category_info["description"]}<br>
        <strong>Base price: {category_info["base_price"]}</strong> (for 700ml) | 
        <strong>${price_per_ml:.4f} per ml</strong>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Step 2: Choose Your Exact Amount")

st.markdown("""
<div style='background: #e8f5e9; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;'>
    <strong>Enter any amount from 1ml to 1000ml - you get exactly what you pay for!</strong>
</div>
""", unsafe_allow_html=True)

st.markdown("**Quick Select:**")
quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
with quick_col1:
    if st.button("250ml", use_container_width=True):
        st.session_state.selected_volume = 250
        st.rerun()
with quick_col2:
    if st.button("500ml", use_container_width=True):
        st.session_state.selected_volume = 500
        st.rerun()
with quick_col3:
    if st.button("700ml", use_container_width=True):
        st.session_state.selected_volume = 700
        st.rerun()
with quick_col4:
    if st.button("1000ml", use_container_width=True):
        st.session_state.selected_volume = 1000
        st.rerun()

prev_volume = st.session_state.get("prev_volume", 500)
prev_category = st.session_state.get("prev_category", "Classic Milk Tea")

volume_ml = st.number_input(
    "Or enter exact amount (ml):",
    min_value=MIN_ML,
    max_value=MAX_ML,
    value=st.session_state.selected_volume,
    step=1,
    help="Type any number from 1 to 1000"
)

st.session_state.selected_volume = volume_ml

if volume_ml != prev_volume or selected_category != prev_category:
    st.session_state.animation_key += 1
    st.session_state.prev_volume = volume_ml
    st.session_state.prev_category = selected_category

total_cost = volume_ml * price_per_ml

st.markdown("### Watch Your Drink Being Poured")
fill_percent = get_fill_percentage(volume_ml)

anim_key = st.session_state.animation_key

cup_col1, cup_col2, cup_col3 = st.columns([1, 2, 1])
with cup_col2:
    animation_html = f"""
<div class='pour-container' key='{anim_key}'>
<div class='pitcher'>
<div class='pitcher-body'>
<div class='pitcher-handle'></div>
<div class='pitcher-spout'></div>
</div>
</div>
<div class='pour-stream'></div>
<div class='cup-with-scale'>
<div class='transparent-cup'>
<div class='liquid-fill' style='--fill-height: {fill_percent}%;'></div>
<div class='bubbles-animated'>
<div class='bubble'></div>
<div class='bubble'></div>
<div class='bubble'></div>
</div>
<div class='ml-indicator'>{volume_ml}ml</div>
</div>
<div class='scale-markers'>
<div class='scale-mark'><div class='scale-line'></div>1000ml</div>
<div class='scale-mark'><div class='scale-line'></div>750ml</div>
<div class='scale-mark'><div class='scale-line'></div>500ml</div>
<div class='scale-mark'><div class='scale-line'></div>250ml</div>
<div class='scale-mark'><div class='scale-line'></div>0ml</div>
</div>
</div>
</div>
<p class='volume-label'>{get_size_label(volume_ml)} - {volume_ml}ml of PURE DRINK (No Ice!)</p>
"""
    st.markdown(animation_html, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### Your Order Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Category",
        value=selected_category.split()[0]
    )

with col2:
    st.metric(
        label="Volume",
        value=f"{volume_ml} ml"
    )

with col3:
    st.metric(
        label="Price/ml",
        value=f"${price_per_ml:.4f}"
    )

st.markdown(f"""
<div class='price-display'>
    Total Cost: ${total_cost:.2f}
</div>
""", unsafe_allow_html=True)

if st.button("Add to Cart", type="primary", use_container_width=True):
    st.session_state.cart.append({
        "category": selected_category,
        "volume": volume_ml,
        "price_per_ml": price_per_ml,
        "cost": total_cost,
        "added_at": datetime.now().strftime("%H:%M:%S")
    })
    st.toast(f"Added {selected_category} ({volume_ml}ml) - ${total_cost:.2f} to cart!")
    st.rerun()

st.markdown("---")

st.markdown("### Your Order")

if st.session_state.cart:
    employee_msg = """
<div style='background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4); border: 3px solid #fff;'>
<div style='font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;'>SHOW THIS SCREEN TO EMPLOYEE</div>
<div style='font-size: 1.2rem;'>Present your order to our staff at the counter to complete your purchase</div>
</div>
"""
    st.markdown(employee_msg, unsafe_allow_html=True)
    
    for idx, item in enumerate(st.session_state.cart):
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.write(f"**{item['category']}** - {item['volume']}ml (No Ice!)")
        with col2:
            st.write(f"${item['cost']:.2f}")
        with col3:
            if st.button("X", key=f"remove_{idx}"):
                st.session_state.cart.pop(idx)
                st.rerun()
    
    cart_total = sum(item["cost"] for item in st.session_state.cart)
    
    total_display = f"""
<div style='background: linear-gradient(135deg, #2E86AB 0%, #1a5276 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0; font-size: 2rem; font-weight: bold;'>
TOTAL: ${cart_total:.2f}
<div style='font-size: 1rem; margin-top: 0.5rem;'>{len(st.session_state.cart)} item(s) - 100% Pure Liquid, No Ice!</div>
</div>
"""
    st.markdown(total_display, unsafe_allow_html=True)
    
    ready_msg = """
<div style='background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);'>
<div style='font-size: 1.3rem; font-weight: bold;'>Ready to pay?</div>
<div style='font-size: 1.1rem; margin-top: 0.5rem;'>Show this screen to our employee at the counter to finalize your order and complete payment.</div>
<div style='margin-top: 1rem; font-size: 0.9rem;'>Thank you for choosing TapiocaExpress!</div>
</div>
"""
    st.markdown(ready_msg, unsafe_allow_html=True)
    
    if st.button("Start New Order", use_container_width=True):
        st.session_state.cart = []
        st.session_state.selected_volume = 500
        st.rerun()
else:
    st.info("Your cart is empty. Add some drinks to get started!")

st.markdown("---")

with st.expander("Drink Category Pricing Guide"):
    st.markdown("""
    **All measurements are PURE LIQUID - No ice taking up space!**
    
    | Category | Base Price (700ml) | Price per ml |
    |----------|-------------------|--------------|
    | Classic Milk Tea | $5.09 - $5.49 | $0.0075/ml |
    | Flavored Milk Tea with Boba | $5.60 | $0.0080/ml |
    | Plain Tea (Black/Green/Fruit) | $4.99 | $0.0071/ml |
    | Snow Bubble / Slush / Smoothie | $6.29 - $6.49 | $0.0091/ml |
    | Snow Bubble (Large Specials) | $6.99 | $0.0100/ml |
    | Soda / Italian Soda | $6.99 | $0.0100/ml |
    | Icy / Fruilush / Fruit-Tea | ~$5.85 | $0.0084/ml |
    | Juice / Fresh-Fruit Drinks | ~$5.49 | $0.0078/ml |
    | Milk Drinks with Toppings | ~$6.99 | $0.0100/ml |
    | Seasonal / Premium Drinks | ~$6.99 | $0.0100/ml |
    
    *Other brands fill your cup with ice. We fill it with flavor!*
    """)

st.markdown("---")

st.markdown("""
<div style='text-align: center; color: #888; padding: 1rem;'>
    <small><strong>TapiocaExpress</strong> - Your Custom Bubble Tea Experience</small><br>
    <small><em>The ONLY brand where 500ml means 500ml of drink, not ice!</em></small>
</div>
""", unsafe_allow_html=True)
