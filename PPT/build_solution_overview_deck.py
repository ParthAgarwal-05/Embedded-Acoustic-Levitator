#!/usr/bin/env python3
"""
Acoustic Levitator - Solution Overview & Technical Pitch Deck Builder
Generates a 15-slide, high-detail, 16:9 widescreen PowerPoint presentation covering:
1. Solution Overview
2. What the Hardware Does (APB timing, 24Vpp push-pull, 6-TX cavity, schematic)
3. What the Software Does (LEDC registers, dynamic phase modulation, dual-core tasks, REST Web UI)
4. Key Features & Innovations (transformerless push-pull, 1.4° phase step, $28 BoM, 5.6W)
5. Uniqueness & Competitive Advantage (benchmarks vs TinyLev, Langevin, Phased Arrays)
6. 45-60 Second Elevator Pitch (structured delivery & timed script)
7. Embedded High-Resolution Illustrations and Diagrams
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.text.text import _Paragraph

# Patch _Paragraph.add_run to accept an optional text argument
_orig_add_run = _Paragraph.add_run
def _patched_add_run(self, text=None):
    run = _orig_add_run(self)
    if text is not None:
        run.text = str(text)
    return run
_Paragraph.add_run = _patched_add_run

# ==========================================
# DESIGN SYSTEM & PALETTE
# ==========================================
BG_COLOR       = RGBColor(10, 17, 40)      # #0A1128 Deep Tech Obsidian
CARD_BG        = RGBColor(21, 32, 60)      # #15203C Slate Card Fill
CARD_BG_LIGHT  = RGBColor(248, 250, 252)  # #F8FAFC White for figure containers
CARD_BORDER    = RGBColor(42, 63, 107)     # #2A3F6B Muted Border
CYAN_ACCENT    = RGBColor(0, 240, 255)     # #00F0FF Neon Cyan Accent
VIOLET_ACCENT  = RGBColor(168, 85, 247)    # #A855F7 Violet Accent
GREEN_ACCENT   = RGBColor(16, 185, 129)    # #10B981 Emerald Green Accent
AMBER_ACCENT   = RGBColor(245, 158, 11)    # #F59E0B Warning Amber
TEXT_PRIMARY   = RGBColor(248, 250, 252)   # #F8FAFC White
TEXT_MUTED     = RGBColor(148, 163, 184)   # #94A3B8 Muted Slate
TEXT_DARK      = RGBColor(15, 23, 42)      # #0F172A Dark Charcoal for white cards

FONT_HEADING = "Helvetica Neue"
FONT_BODY    = "Arial"

project_dir = "/Users/parth-agarwal/Desktop/EMBEDDED/project"
fig_dir     = os.path.join(project_dir, "REPORT/figures")
schematic_p = os.path.join(project_dir, "REPORT/schematic_bw.png")
output_path = os.path.join(project_dir, "PPT/Acoustic_Levitator_Solution_Overview_Deck.pptx")

os.makedirs(os.path.dirname(output_path), exist_ok=True)

prs = pptx.Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide):
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background()
    return bg

def add_header(slide, category, title, subtitle):
    # Category Pill
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.32))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.name = FONT_HEADING
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = CYAN_ACCENT

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_PRIMARY

    # Subtitle
    p_s = tf_t.add_paragraph()
    p_s.text = subtitle
    p_s.font.name = FONT_BODY
    p_s.font.size = Pt(11.5)
    p_s.font.color.rgb = TEXT_MUTED

def add_card(slide, x, y, w, h, bg_color=CARD_BG, border_color=CARD_BORDER, border_width=1.2):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

def add_figure_card(slide, x, y, w, h, img_path, caption=""):
    # Outer white container card for high contrast
    card = add_card(slide, x, y, w, h, bg_color=CARD_BG_LIGHT, border_color=CYAN_ACCENT, border_width=1.5)
    
    # Image inside
    img_pad = 0.15
    caption_h = 0.35 if caption else 0.0
    img_h = h - caption_h - (img_pad * 2)
    img_w = w - (img_pad * 2)
    
    if os.path.exists(img_path):
        slide.shapes.add_picture(
            img_path, Inches(x + img_pad), Inches(y + img_pad), Inches(img_w), Inches(img_h)
        )
    
    if caption:
        cap_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(y + h - caption_h - 0.05), Inches(w - 0.2), Inches(caption_h))
        tf_cap = cap_box.text_frame
        tf_cap.word_wrap = True
        p_cap = tf_cap.paragraphs[0]
        p_cap.alignment = PP_ALIGN.CENTER
        p_cap.text = caption
        p_cap.font.name = FONT_BODY
        p_cap.font.size = Pt(9.5)
        p_cap.font.bold = True
        p_cap.font.color.rgb = TEXT_DARK

# ==========================================
# SLIDE 1: TITLE SLIDE
# ==========================================
print("Building Slide 1: Title Slide...")
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Large Center Glass Card
add_card(s1, 1.0, 0.8, 11.333, 5.9, bg_color=CARD_BG, border_color=CYAN_ACCENT, border_width=1.8)

# Top Badge
tb_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.15), Inches(10.3), Inches(0.4))
tf_tb = tb_box.text_frame
p_tb = tf_tb.paragraphs[0]
p_tb.text = "B.TECH CAPSTONE THESIS PRESENTATION  |  FINAL TECHNICAL EVALUATION"
p_tb.font.name = FONT_HEADING
p_tb.font.size = Pt(11)
p_tb.font.bold = True
p_tb.font.color.rgb = CYAN_ACCENT

# Main Presentation Title
pt_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.55), Inches(10.3), Inches(1.5))
tf_pt = pt_box.text_frame
tf_pt.word_wrap = True
p_pt = tf_pt.paragraphs[0]
p_pt.text = "DESIGN AND IMPLEMENTATION OF AN INTERNET-ENABLED ACOUSTIC LEVITATION MANIPULATION SYSTEM"
p_pt.font.name = FONT_HEADING
p_pt.font.size = Pt(24)
p_pt.font.bold = True
p_pt.font.color.rgb = TEXT_PRIMARY

p_sub_t = tf_pt.add_paragraph()
p_sub_t.text = "ESP32 APB Clock Synchronization, Dual Push-Pull Amplification, and Real-Time IoT Teleoperation"
p_sub_t.font.name = FONT_BODY
p_sub_t.font.size = Pt(13)
p_sub_t.font.color.rgb = TEXT_MUTED
p_sub_t.space_before = Pt(6)

# Divider Line
line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(3.2), Inches(10.3), Inches(0.02))
line.fill.solid()
line.fill.fore_color.rgb = CARD_BORDER
line.line.fill.background()

# Investigators Column
inv_box = s1.shapes.add_textbox(Inches(1.5), Inches(3.4), Inches(5.0), Inches(2.2))
tf_inv = inv_box.text_frame
tf_inv.word_wrap = True
p_ih = tf_inv.paragraphs[0]
p_ih.text = "PROJECT INVESTIGATORS:"
p_ih.font.name = FONT_HEADING
p_ih.font.size = Pt(11)
p_ih.font.bold = True
p_ih.font.color.rgb = CYAN_ACCENT

students = [
    ("RONIL", "24BCE1330"),
    ("TEJAS", "24BCE1360"),
    ("PRIYANSHU", "24BCE1140"),
    ("PRASHANT", "24BCE1118")
]
for s_n, s_r in students:
    p_st = tf_inv.add_paragraph()
    p_st.text = f"•  {s_n} ({s_r})  —  B.Tech CSE"
    p_st.font.name = FONT_BODY
    p_st.font.size = Pt(11)
    p_st.font.color.rgb = TEXT_PRIMARY
    p_st.space_before = Pt(2)

# Guide and Department Column
gd_box = s1.shapes.add_textbox(Inches(6.8), Inches(3.4), Inches(5.0), Inches(2.2))
tf_gd = gd_box.text_frame
tf_gd.word_wrap = True

p_gh = tf_gd.paragraphs[0]
p_gh.text = "FACULTY GUIDANCE & LEADERSHIP:"
p_gh.font.name = FONT_HEADING
p_gh.font.size = Pt(11)
p_gh.font.bold = True
p_gh.font.color.rgb = GREEN_ACCENT

faculty_lines = [
    ("Project Guide: ", "Dr. Mohammed Aarif K.O., Professor, SCOPE"),
    ("Dean: ", "Dr. Viswanathan V, Professor & Dean, SCOPE"),
    ("Associate Dean: ", "Dr. Suganya G, Professor & Associate Dean, SCOPE"),
    ("School: ", "School of Computer Science and Engineering (SCOPE)"),
    ("Institution: ", "Vellore Institute of Technology (VIT), Chennai – Nov 2026")
]
for lbl, val in faculty_lines:
    p_f = tf_gd.add_paragraph()
    r_l = p_f.add_run(lbl)
    r_l.font.name = FONT_BODY
    r_l.font.size = Pt(10)
    r_l.font.bold = True
    r_l.font.color.rgb = TEXT_MUTED
    r_v = p_f.add_run(val)
    r_v.font.name = FONT_BODY
    r_v.font.size = Pt(10)
    r_v.font.color.rgb = TEXT_PRIMARY
    p_f.space_before = Pt(2)

# ==========================================
# SLIDE 2: 45-60 SECOND ELEVATOR PITCH
# ==========================================
print("Building Slide 2: 45-60s Elevator Pitch...")
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "EXECUTIVE SUMMARY", "The 45-60 Second Presentation Pitch", "High-Impact Rapid Project Overview and Core Value Proposition")

# Left Column: The 60-Second Timed Pitch Script
add_card(s2, 0.8, 1.6, 7.6, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
sc_box = s2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(7.0), Inches(4.9))
tf_sc = sc_box.text_frame
tf_sc.word_wrap = True

p_sh = tf_sc.paragraphs[0]
p_sh.text = "TIMED SPEAKER NARRATIVE (45–60 SECONDS):"
p_sh.font.name = FONT_HEADING
p_sh.font.size = Pt(12)
p_sh.font.bold = True
p_sh.font.color.rgb = CYAN_ACCENT

pitch_parts = [
    ("[00–10s] The Challenge: ", "Handling fragile micro-objects, living cells, and pure chemical reagents without solid surface friction, electrostatic distortion, or petri-dish contamination has historically required $5,000+ laboratory setups."),
    ("[10–25s] The Solution: ", "We engineered an autonomous, internet-enabled acoustic levitator using 6 piezoelectric transducers and an ESP32 microcontroller, creating deep ultrasonic potential wells that trap and levitate objects in mid-air."),
    ("[25–45s] The Innovation: ", "We eliminated bulky transformers by inventing a dual L293D push-pull driver delivering 24 Vpp from a 12V supply. We synchronized the ESP32 80 MHz APB clock to achieve 1.4° phase steps, enabling sub-millimeter vertical manipulation (~12 µm/deg)."),
    ("[45–60s] The Impact: ", "Featuring native Wi-Fi REST web teleoperation and a total bill-of-materials under $28 at only 5.6 Watts, this system democratizes contactless handling for cleanrooms, bio-assays, and micro-assembly.")
]

for tag, desc in pitch_parts:
    p_p = tf_sc.add_paragraph()
    p_p.space_before = Pt(8)
    r_tag = p_p.add_run(tag)
    r_tag.font.name = FONT_HEADING
    r_tag.font.size = Pt(11)
    r_tag.font.bold = True
    r_tag.font.color.rgb = GREEN_ACCENT
    r_d = p_p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(10.5)
    r_d.font.color.rgb = TEXT_PRIMARY

# Right Column: Big Value Numbers
add_card(s2, 8.7, 1.6, 3.8, 5.3, bg_color=CARD_BG, border_color=CYAN_ACCENT)
num_box = s2.shapes.add_textbox(Inches(8.9), Inches(1.8), Inches(3.4), Inches(4.9))
tf_num = num_box.text_frame
tf_num.word_wrap = True

p_nh = tf_num.paragraphs[0]
p_nh.text = "KEY METRIC CALLOUTS:"
p_nh.font.name = FONT_HEADING
p_nh.font.size = Pt(12)
p_nh.font.bold = True
p_nh.font.color.rgb = CYAN_ACCENT

metrics = [
    ("154.2 dB", "Peak Cavity Acoustic SPL"),
    ("24 Vpp", "Differential Drive (No Transformers)"),
    ("1.406°", "Hardware Timer Phase Granularity"),
    ("< $28", "Total System Bill of Materials"),
    ("5.6 W", "Ultra-Low Power Consumption"),
    ("< 15 ms", "Embedded Wi-Fi REST Latency")
]

for val, lbl in metrics:
    p_v = tf_num.add_paragraph()
    p_v.space_before = Pt(6)
    r_v = p_v.add_run(val)
    r_v.font.name = FONT_HEADING
    r_v.font.size = Pt(16)
    r_v.font.bold = True
    r_v.font.color.rgb = CYAN_ACCENT
    
    p_l = tf_num.add_paragraph()
    p_l.text = lbl
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(9.5)
    p_l.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 3: SOLUTION OVERVIEW
# ==========================================
print("Building Slide 3: Solution Overview...")
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "SOLUTION OVERVIEW", "End-to-End System Integration & Architecture", "Harmonizing High-Speed Embedded Firmware, Push-Pull Power Drivers, and Acoustic Physics")

# Left Column: Overview Details
add_card(s3, 0.8, 1.6, 5.8, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
ov_box = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.4), Inches(4.9))
tf_ov = ov_box.text_frame
tf_ov.word_wrap = True

p_oh = tf_ov.paragraphs[0]
p_oh.text = "FOUR-TIER INTEGRATED ARCHITECTURE:"
p_oh.font.name = FONT_HEADING
p_oh.font.size = Pt(12)
p_oh.font.bold = True
p_oh.font.color.rgb = CYAN_ACCENT

tiers = [
    ("1. High-Speed Compute Core (ESP32):", "Dual-core 240 MHz Tensilica LX6. Hardware APB timer (LEDC) generates 4 complementary square waves at 40 kHz with zero clock jitter."),
    ("2. Transformerless Power Stage (Dual L293D):", "Differential push-pull H-bridge topology inverts output polarities, boosting a single 12V rail to 24 Vpp directly across transducer terminals."),
    ("3. Resonant Cavity (6x 40 kHz PZT):", "3 top and 3 bottom transducers tilted inward at 12° across a calibrated distance D = 72.25 mm (17 semi-wavelengths), superimposing acoustic waves to exceed 154 dB SPL."),
    ("4. Zero-Install Teleoperation (Wi-Fi Web UI):", "FreeRTOS Core 1 hosts an asynchronous HTTP REST server and interactive web interface for sub-millimeter particle translation and diagnostics.")
]

for t_title, t_desc in tiers:
    p_t = tf_ov.add_paragraph()
    p_t.space_before = Pt(8)
    r_tt = p_t.add_run(t_title + "\n")
    r_tt.font.name = FONT_HEADING
    r_tt.font.size = Pt(10.5)
    r_tt.font.bold = True
    r_tt.font.color.rgb = GREEN_ACCENT
    r_td = p_t.add_run(t_desc)
    r_td.font.name = FONT_BODY
    r_td.font.size = Pt(9.5)
    r_td.font.color.rgb = TEXT_PRIMARY

# Right Column: System Architecture Diagram
add_figure_card(
    s3, 6.9, 1.6, 5.6, 5.3,
    os.path.join(fig_dir, "fig3_1_system_architecture.png"),
    "Figure 3.1: End-to-End System Block Diagram & Hardware Signal Flow"
)

# ==========================================
# SLIDE 4: WHAT THE HARDWARE DOES - PART 1
# ==========================================
print("Building Slide 4: Hardware Part 1...")
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "HARDWARE ENGINE (PART 1)", "What the Hardware Does: Signal Generation & Push-Pull Drive", "Generating 24 Vpp Differential Excitation from a 12V Supply without Step-Up Transformers")

# Left Column: Technical Narrative
add_card(s4, 0.8, 1.6, 5.8, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
h1_box = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.4), Inches(4.9))
tf_h1 = h1_box.text_frame
tf_h1.word_wrap = True

p_h1h = tf_h1.paragraphs[0]
p_h1h.text = "HARDWARE WAVEFORM & POWER STAGE:"
p_h1h.font.name = FONT_HEADING
p_h1h.font.size = Pt(12)
p_h1h.font.bold = True
p_h1h.font.color.rgb = CYAN_ACCENT

hw_p1 = [
    ("Direct APB Clock Sourcing (80 MHz):", "Hardware timer registers lock directly onto the 80 MHz Advanced Peripheral Bus, eliminating CPU-induced jitter and guaranteeing microsecond phase stability."),
    ("Differential Push-Pull Inversion (180°):", "Rather than driving transducers against ground (0 to 12V), each transducer is driven across two opposing half-bridges: Phase A (0°) on terminal 1 and Phase B (180°) on terminal 2."),
    ("Transformerless Voltage Doubling (24 Vpp):", "When Phase A is HIGH (12V) and B is LOW (0V), Vdiff = +12V. In the next half-cycle, polarities invert: Vdiff = -12V. Total swing = 24 V peak-to-peak."),
    ("Acoustic Power Quadrupling (+13.6 dB):", "Acoustic radiation pressure scales with applied voltage (P0 ∝ Vpp) and acoustic power scales quadratically (Pac ∝ Vpp²), boosting energy output 23x compared to 5V driving.")
]

for pt_title, pt_desc in hw_p1:
    p_p = tf_h1.add_paragraph()
    p_p.space_before = Pt(8)
    r_pt = p_p.add_run(pt_title + "\n")
    r_pt.font.name = FONT_HEADING
    r_pt.font.size = Pt(10.5)
    r_pt.font.bold = True
    r_pt.font.color.rgb = GREEN_ACCENT
    r_pd = p_p.add_run(pt_desc)
    r_pd.font.name = FONT_BODY
    r_pd.font.size = Pt(9.5)
    r_pd.font.color.rgb = TEXT_PRIMARY

# Right Column: Push-Pull Waveforms Diagram
add_figure_card(
    s4, 6.9, 1.6, 5.6, 5.3,
    os.path.join(fig_dir, "fig3_4_push_pull_waveforms.png"),
    "Figure 3.4: Complementary PWM Drive and 24 Vpp Differential Waveforms"
)

# ==========================================
# SLIDE 5: WHAT THE HARDWARE DOES - PART 2
# ==========================================
print("Building Slide 5: Hardware Part 2...")
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "HARDWARE ENGINE (PART 2)", "What the Hardware Does: Cavity Geometry & Resonance", "Optimized 6-Transducer Opposing Arrays and Multi-Node Standing Wave Physics")

# Left Column: Cavity Engineering
add_card(s5, 0.8, 1.6, 5.8, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
h2_box = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.4), Inches(4.9))
tf_h2 = h2_box.text_frame
tf_h2.word_wrap = True

p_h2h = tf_h2.paragraphs[0]
p_h2h.text = "ACOUSTIC CAVITY & TRANSDUCER CLUSTERS:"
p_h2h.font.name = FONT_HEADING
p_h2h.font.size = Pt(12)
p_h2h.font.bold = True
p_h2h.font.color.rgb = CYAN_ACCENT

hw_p2 = [
    ("6-Transducer Cluster Topology:", "Six 16 mm 40 kHz piezoelectric transducers arranged as two opposing arrays: 3 top (facing DOWN) and 3 bottom (facing UP) in equilateral triangles (17.5 mm pitch)."),
    ("12.0° Inward Concave Focal Tilt:", "Each transducer is geometrically angled inward at 12° toward the central vertical axis, ensuring constructive acoustic wave superposition at the center trapping node."),
    ("Calibrated Resonant Height (D = 72.25 mm):", "Cavity height enforces the acoustic semi-wavelength resonance condition: D = 17 × (λ / 2) ≈ 72.25 mm at 20°C, establishing 17 stationary trapping nodes in air."),
    ("Power Isolation & Filtering:", "LM2596 buck regulator delivers isolated 5.0V logic power; dual 100 µF electrolytic and 0.1 µF ceramic bypass capacitors absorb 40 kHz inductive switching spikes.")
]

for pt_title, pt_desc in hw_p2:
    p_p = tf_h2.add_paragraph()
    p_p.space_before = Pt(8)
    r_pt = p_p.add_run(pt_title + "\n")
    r_pt.font.name = FONT_HEADING
    r_pt.font.size = Pt(10.5)
    r_pt.font.bold = True
    r_pt.font.color.rgb = GREEN_ACCENT
    r_pd = p_p.add_run(pt_desc)
    r_pd.font.name = FONT_BODY
    r_pd.font.size = Pt(9.5)
    r_pd.font.color.rgb = TEXT_PRIMARY

# Right Column: Cavity Geometry Diagram
add_figure_card(
    s5, 6.9, 1.6, 5.6, 5.3,
    os.path.join(fig_dir, "fig3_2_cavity_geometry.png"),
    "Figure 3.2: 6-Transducer Cavity Geometry, Concave Alignment, and Spacing"
)

# ==========================================
# SLIDE 6: MASTER CIRCUIT SCHEMATIC & WIRING
# ==========================================
print("Building Slide 6: Schematic...")
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "ELECTRICAL INTEGRATION", "Master Circuit Schematic & Pin Interconnections", "Deterministic GPIO Routing, Dual H-Bridge Drivers, and Star-Ground Isolation")

# Left Column: Pin Mapping Matrix Card
add_card(s6, 0.8, 1.6, 5.4, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
pin_box = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.0), Inches(4.9))
tf_pin = pin_box.text_frame
tf_pin.word_wrap = True

p_pinh = tf_pin.paragraphs[0]
p_pinh.text = "HARDWARE PIN INTERCONNECTION MATRIX:"
p_pinh.font.name = FONT_HEADING
p_pinh.font.size = Pt(12)
p_pinh.font.bold = True
p_pinh.font.color.rgb = CYAN_ACCENT

pin_lines = [
    ("ESP32 GPIO 4:", "IC 1 Pins 2 & 15 (1A, 4A)  -> Top Phase A (0° ref)"),
    ("ESP32 GPIO 5:", "IC 1 Pins 7 & 10 (2A, 3A)  -> Top Phase B (180° inv)"),
    ("ESP32 GPIO 18:", "IC 2 Pins 2 & 15 (1A, 4A)  -> Bot Phase A (Phase shift)"),
    ("ESP32 GPIO 19:", "IC 2 Pins 7 & 10 (2A, 3A)  -> Bot Phase B (180° push-pull)"),
    ("5V Rail (LM2596):", "ESP32 VIN, IC 1 & 2 VCC1 (Pin 16), EN (Pins 1 & 9)"),
    ("12V DC Input:", "IC 1 & IC 2 VCC2 (Pin 8) motor power rail"),
    ("IC 1 Outputs:", "Pins 3 & 6 -> Top TX #1, #2 | Pins 14 & 11 -> Top TX #3"),
    ("IC 2 Outputs:", "Pins 3 & 6 -> Bot TX #4, #5 | Pins 14 & 11 -> Bot TX #6")
]

for p_l, p_d in pin_lines:
    p_p = tf_pin.add_paragraph()
    p_p.space_before = Pt(4)
    r_l = p_p.add_run(p_l + " ")
    r_l.font.name = FONT_HEADING
    r_l.font.size = Pt(10)
    r_l.font.bold = True
    r_l.font.color.rgb = GREEN_ACCENT
    r_d = p_p.add_run(p_d)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(9.5)
    r_d.font.color.rgb = TEXT_PRIMARY

# Right Column: Circuit Schematic Diagram
add_figure_card(
    s6, 6.5, 1.6, 6.0, 5.3,
    schematic_p if os.path.exists(schematic_p) else os.path.join(fig_dir, "fig3_3_circuit_schematic_wiring.png"),
    "Figure A2.1: Master Electrical Circuit Schematic & Wiring Layout"
)

# ==========================================
# SLIDE 7: WHAT THE SOFTWARE DOES - PART 1
# ==========================================
print("Building Slide 7: Software Part 1...")
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "SOFTWARE ENGINE (PART 1)", "What the Software Does: APB Timer Registers & Core Isolation", "Hardware-Synchronized Zero-Jitter PWM Synthesis and Dual-Core FreeRTOS Partitioning")

# 3 Column Cards Layout
cards_sw1 = [
    ("LEDC Hardware Timers", CYAN_ACCENT, [
        ("Direct Register Control:", "Configures LEDC_TIMER_0 with high-speed 80 MHz APB clock routing, bypassing software interrupts entirely."),
        ("8-Bit Counter (256 Ticks):", "Each 25 µs period is segmented into 256 discrete ticks, enabling fine 1.406° phase resolution per tick."),
        ("Exact Fractional Divider:", "Prescaler set to 7 + 832/1024, synthesizing exactly 40,000.0 Hz with zero cumulative clock drift.")
    ]),
    ("Dual-Core FreeRTOS Tasks", GREEN_ACCENT, [
        ("Core 0 (Deterministic PWM):", "Dedicated to real-time timer comparator registers, GPIO phase modulation, and 115200 baud USB serial command CLI."),
        ("Core 1 (Asynchronous IoT):", "Runs the 2.4 GHz 802.11n Wi-Fi radio stack, TCP/IP socket buffer, and embedded RESTful HTTP web server."),
        ("Zero Phase Jitter:", "Network traffic and HTTP requests on Core 1 never introduce latency or jitter into the ultrasonic wave generation on Core 0.")
    ]),
    ("Dynamic Frequency Trimming", VIOLET_ACCENT, [
        ("Real-Time Resonant Tuning:", "Allows ±100 Hz frequency adjustment on the fly (38.5 kHz to 41.5 kHz) via web or serial command."),
        ("Thermal Drift Tracking:", "Compensates for transducer piezoelectric warming during extended levitation without rebooting the controller."),
        ("Automated Frequency Sweep:", "Sweeps 38.0 kHz to 42.0 kHz to automatically identify cavity acoustic standing wave resonance.")
    ])
]

for c_idx, (c_title, c_color, c_items) in enumerate(cards_sw1):
    cx = 0.8 + c_idx * 4.0
    add_card(s7, cx, 1.6, 3.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
    c_box = s7.shapes.add_textbox(Inches(cx + 0.2), Inches(1.8), Inches(3.333), Inches(4.9))
    tf_c = c_box.text_frame
    tf_c.word_wrap = True
    
    p_ch = tf_c.paragraphs[0]
    p_ch.text = c_title
    p_ch.font.name = FONT_HEADING
    p_ch.font.size = Pt(13)
    p_ch.font.bold = True
    p_ch.font.color.rgb = c_color
    
    for it_title, it_desc in c_items:
        p_it = tf_c.add_paragraph()
        p_it.space_before = Pt(8)
        r_itt = p_it.add_run(it_title + "\n")
        r_itt.font.name = FONT_HEADING
        r_itt.font.size = Pt(10.5)
        r_itt.font.bold = True
        r_itt.font.color.rgb = TEXT_PRIMARY
        r_itd = p_it.add_run(it_desc)
        r_itd.font.name = FONT_BODY
        r_itd.font.size = Pt(9.5)
        r_itd.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 8: WHAT THE SOFTWARE DOES - PART 2
# ==========================================
print("Building Slide 8: Software Part 2...")
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "SOFTWARE ENGINE (PART 2)", "What the Software Does: Dynamic Phase Shifting & Manipulation", "Linear Axial Particle Translation via On-The-Fly Hardware Timer Offset Registers")

# Left Column: Phase Modulation Math
add_card(s8, 0.8, 1.6, 5.8, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
ph_box = s8.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.4), Inches(4.9))
tf_ph = ph_box.text_frame
tf_ph.word_wrap = True

p_phh = tf_ph.paragraphs[0]
p_phh.text = "PHASE-TO-DISPLACEMENT MANIPULATION:"
p_phh.font.name = FONT_HEADING
p_phh.font.size = Pt(12)
p_phh.font.bold = True
p_phh.font.color.rgb = CYAN_ACCENT

sw_p2 = [
    ("Relative Phase Modulation (Δφ):", "To translate a trapped particle vertically, the bottom array phase is shifted relative to the top reference array by altering LEDC channel hpoint registers."),
    ("Continuous Waveform Update:", "The firmware calls ledc_set_duty_with_hpoint() and ledc_update_duty(), updating phase registers mid-cycle without stopping timer counting—preventing particle drop."),
    ("Linear Sensitivity (11.9 µm / degree):", "A full 360° phase shift shifts the standing wave pattern by exactly one semi-wavelength: Δz = (λ/2) × (Δφ/360°) = 4.25 mm × (Δφ/360°) ≈ 11.9 µm/deg."),
    ("Fine Step Translation (67.5 µm):", "Moving by 4 timer ticks advances phase by 5.625°, translating the trapped particle vertically by exactly 67.5 micrometers with repeatable accuracy.")
]

for pt_title, pt_desc in sw_p2:
    p_p = tf_ph.add_paragraph()
    p_p.space_before = Pt(8)
    r_pt = p_p.add_run(pt_title + "\n")
    r_pt.font.name = FONT_HEADING
    r_pt.font.size = Pt(10.5)
    r_pt.font.bold = True
    r_pt.font.color.rgb = GREEN_ACCENT
    r_pd = p_p.add_run(pt_desc)
    r_pd.font.name = FONT_BODY
    r_pd.font.size = Pt(9.5)
    r_pd.font.color.rgb = TEXT_PRIMARY

# Right Column: Phase vs Displacement Graph
add_figure_card(
    s8, 6.9, 1.6, 5.6, 5.3,
    os.path.join(fig_dir, "fig4_2_phase_vs_displacement.png"),
    "Figure 4.2: Experimental Vertical Particle Displacement vs. Array Phase Shift"
)

# ==========================================
# SLIDE 9: EMBEDDED WEB SERVER & IOT DASHBOARD
# ==========================================
print("Building Slide 9: Web Server...")
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "IOT TELEOPERATION", "Embedded Web Server & Real-Time Dashboard", "Zero-Install Browser GUI, RESTful API Endpoints, and Sub-15 ms Latency")

# Left Column: Web UI & Endpoints
add_card(s9, 0.8, 1.6, 6.0, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
web_box = s9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.6), Inches(4.9))
tf_web = web_box.text_frame
tf_web.word_wrap = True

p_webh = tf_web.paragraphs[0]
p_webh.text = "RESTFUL API ARCHITECTURE (PORT 80):"
p_webh.font.name = FONT_HEADING
p_webh.font.size = Pt(12)
p_webh.font.bold = True
p_webh.font.color.rgb = CYAN_ACCENT

api_endpoints = [
    ("GET /api/status", "Returns live JSON telemetry: frequency, phase tick (0..255), top/bot array status, RSSI, and uptime."),
    ("POST /api/freq?val=40100", "Dynamically updates APB hardware timer frequency in 100 Hz increments on the fly."),
    ("POST /api/move?dir=up&step=4", "Translates standing wave node up or down by updating bottom LEDC offset registers."),
    ("POST /api/phase?mode=toggle", "Instantaneously toggles between 0° in-phase and 180° anti-phase trapping configurations."),
    ("POST /api/sweep", "Executes automated resonant frequency characterization sweep from 38.5 to 41.5 kHz.")
]

for ep, ep_desc in api_endpoints:
    p_e = tf_web.add_paragraph()
    p_e.space_before = Pt(6)
    r_ep = p_e.add_run(ep + "\n")
    r_ep.font.name = "Courier New"
    r_ep.font.size = Pt(10)
    r_ep.font.bold = True
    r_ep.font.color.rgb = CYAN_ACCENT
    r_ed = p_e.add_run(ep_desc)
    r_ed.font.name = FONT_BODY
    r_ed.font.size = Pt(9.5)
    r_ed.font.color.rgb = TEXT_PRIMARY

# Right Column: Dashboard Features Card
add_card(s9, 7.1, 1.6, 5.4, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
feat_box = s9.shapes.add_textbox(Inches(7.3), Inches(1.8), Inches(5.0), Inches(4.9))
tf_feat = feat_box.text_frame
tf_feat.word_wrap = True

p_feath = tf_feat.paragraphs[0]
p_feath.text = "ZERO-INSTALL BROWSER DASHBOARD:"
p_feath.font.name = FONT_HEADING
p_feath.font.size = Pt(12)
p_feath.font.bold = True
p_feath.font.color.rgb = GREEN_ACCENT

web_feats = [
    ("Fully Self-Hosted in Flash:", "Complete HTML5, CSS3, and JavaScript web application stored in ESP32 PROGMEM. No external web server or internet connection required."),
    ("Dual Connection Modalities:", "Connects to local campus/home Wi-Fi (STA mode) or creates its own standalone Access Point ('Acoustic-Levitator' / '12345678')."),
    ("Responsive Smartphone & PC GUI:", "Touch-friendly controls optimized for mobile phones, tablets, and lab laptops with sub-15 ms round-trip execution latency."),
    ("Simultaneous USB Serial CLI:", "Full 115200 baud UART serial interface supports simultaneous terminal control ('+', '-', 'u', 'd', 'p', 'x', '?').")
]

for f_title, f_desc in web_feats:
    p_f = tf_feat.add_paragraph()
    p_f.space_before = Pt(8)
    r_ft = p_f.add_run(f_title + "\n")
    r_ft.font.name = FONT_HEADING
    r_ft.font.size = Pt(10.5)
    r_ft.font.bold = True
    r_ft.font.color.rgb = TEXT_PRIMARY
    r_fd = p_f.add_run(f_desc)
    r_fd.font.name = FONT_BODY
    r_fd.font.size = Pt(9.5)
    r_fd.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 10: ACOUSTIC PHYSICS & GOR'KOV POTENTIAL
# ==========================================
print("Building Slide 10: Acoustic Physics...")
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "THEORETICAL FOUNDATIONS", "Physics of Acoustic Levitation & Gor'kov Potential", "Derivation of Acoustic Radiation Force and Non-Contact Gravitational Balance")

# Left Column: Physics Derivation
add_card(s10, 0.8, 1.6, 5.8, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
phys_box = s10.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.4), Inches(4.9))
tf_phys = phys_box.text_frame
tf_phys.word_wrap = True

p_phyh = tf_phys.paragraphs[0]
p_phyh.text = "GOR'KOV POTENTIAL DERIVATION:"
p_phyh.font.name = FONT_HEADING
p_phyh.font.size = Pt(12)
p_phyh.font.bold = True
p_phyh.font.color.rgb = CYAN_ACCENT

deriv_steps = [
    ("Mean Acoustic Potential (U):", "U = 2πr³ [ (⟨p²⟩ / 3ρ0 c0²) f1 - (ρ0 ⟨v²⟩ / 2) f2 ]\nRepresents acoustic energy density acting across particle volume."),
    ("Contrast Factors (f1 & f2):", "For rigid EPS particles in air: f1 ≈ 1 (monopole compressibility factor) and f2 ≈ 1 (dipole density factor)."),
    ("Axial Acoustic Restoring Force:", "Frad,z = -∂U / ∂z = (5π r³ k P0² / 6ρ0 c0²) sin(2kz)\nActs as an acoustic spring restoring particles back to pressure nodes."),
    ("Gravitational Levitation Threshold:", "Levitation requires Frad,max >= mg:\nP0 >= sqrt( 8 ρ0 ρp c0² g / 5k ) ≈ 1,420 Pa (157.0 dB SPL).")
]

for d_title, d_desc in deriv_steps:
    p_d = tf_phys.add_paragraph()
    p_d.space_before = Pt(8)
    r_dt = p_d.add_run(d_title + "\n")
    r_dt.font.name = FONT_HEADING
    r_dt.font.size = Pt(10.5)
    r_dt.font.bold = True
    r_dt.font.color.rgb = GREEN_ACCENT
    r_dd = p_d.add_run(d_desc)
    r_dd.font.name = FONT_BODY
    r_dd.font.size = Pt(9.5)
    r_dd.font.color.rgb = TEXT_PRIMARY

# Right Column: Gor'kov Potential Well Graph
add_figure_card(
    s10, 6.9, 1.6, 5.6, 5.3,
    os.path.join(fig_dir, "fig2_2_gorkov_potential_force.png"),
    "Figure 2.2: Gor'kov Potential Well U(z) and Acoustic Restoring Force Frad"
)

# ==========================================
# SLIDE 11: EXPERIMENTAL RESULTS & VALIDATION
# ==========================================
print("Building Slide 11: Experimental Results...")
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "EXPERIMENTAL CHARACTERIZATION", "Empirical Validation & Benchmark Results", "Quantitative Acoustic Sound Pressure, Thermal Equilibrium, and Trapping Benchmarks")

# Top-Left: SPL Frequency Curve
add_figure_card(
    s11, 0.8, 1.6, 5.6, 3.2,
    os.path.join(fig_dir, "fig4_1_frequency_resonance_curve.png"),
    "Figure 4.1: Cavity Acoustic SPL Output vs. Frequency Sweep"
)

# Top-Right: Thermal Rise Curve
add_figure_card(
    s11, 6.8, 1.6, 5.7, 3.2,
    os.path.join(fig_dir, "fig4_3_thermal_power_profile.png"),
    "Figure 4.3: L293D Driver Thermal Rise and System Power Profile"
)

# Bottom Full-Width Table Card: Measured Results
add_card(s11, 0.8, 5.0, 11.7, 1.9, bg_color=CARD_BG, border_color=CARD_BORDER)
res_box = s11.shapes.add_textbox(Inches(1.0), Inches(5.1), Inches(11.3), Inches(1.7))
tf_res = res_box.text_frame
tf_res.word_wrap = True

p_resh = tf_res.paragraphs[0]
p_resh.text = "EMPIRICAL PERFORMANCE METRICS SUMMARY:"
p_resh.font.name = FONT_HEADING
p_resh.font.size = Pt(11)
p_resh.font.bold = True
p_resh.font.color.rgb = CYAN_ACCENT

results_summary = [
    ("Center Resonant Frequency: ", "40.05 kHz (±100 Hz tuning)"),
    ("Peak Sound Pressure Level: ", "154.2 dB SPL (re 20 µPa)"),
    ("Acoustic Quality Factor Q: ", "34.8 (Bandwidth = 1.15 kHz)"),
    ("Max Trapped Particle Mass: ", "8.2 mg (EPS bead, d = 3.5 mm)"),
    ("Axial Manipulation Range: ", "4.25 mm (Full semi-wavelength)"),
    ("Steady-State Driver Temp: ", "52.4°C (Safe plateau, <150°C limit)"),
    ("Total Power Consumption: ", "5.58 W (465 mA @ 12.0 V DC)"),
    ("Continuous Trapping Time: ", "> 4 Hours (Zero node drift)")
]

# Display as 2 columns of 4 metrics
for idx, (lbl, val) in enumerate(results_summary):
    if idx % 2 == 0:
        p_row = tf_res.add_paragraph()
        p_row.space_before = Pt(2)
    r_l = p_row.add_run(lbl)
    r_l.font.name = FONT_BODY
    r_l.font.size = Pt(9.5)
    r_l.font.bold = True
    r_l.font.color.rgb = TEXT_MUTED
    r_v = p_row.add_run(val + "    |    ")
    r_v.font.name = FONT_BODY
    r_v.font.size = Pt(9.5)
    r_v.font.color.rgb = TEXT_PRIMARY

# ==========================================
# SLIDE 12: KEY INNOVATIONS & UNIQUE VALUE
# ==========================================
print("Building Slide 12: Key Innovations...")
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "CORE INNOVATIONS", "Key Technical Features & Engineering Breakthroughs", "Architectural Novelties Setting This Acoustic Levitator Apart from Prior Systems")

innovations = [
    ("1. Transformerless Voltage Doubler", CYAN_ACCENT, [
        ("Elimination of Bulky Coils:", "Replaced noisy, fragile step-up transformers with differential push-pull H-bridge polarity inversion."),
        ("24 Vpp from 12V DC Rail:", "Doubles transducer drive voltage and quadruples acoustic radiation power (+13.6 dB SPL)."),
        ("Zero EMI Interference:", "Eliminates high-voltage inductive switching spikes that degrade sensitive Wi-Fi and ADC telemetry.")
    ]),
    ("2. APB Hardware Clock-Lock", GREEN_ACCENT, [
        ("Zero Phase Jitter:", "LEDC timers directly index the internal 80 MHz APB bus, guaranteeing sub-microsecond phase stability."),
        ("1.406° Phase Resolution:", "8-bit timer segmentation (256 ticks/period) provides ~12 µm/deg axial position control resolution."),
        ("Fractional Clock Divider:", "Exact 7 + 832/1024 divider eliminates cumulative phase skew between opposing arrays.")
    ]),
    ("3. Dual-Core RTOS Separation", VIOLET_ACCENT, [
        ("Core 0 (Acoustic Timing):", "High-priority hardware LEDC registers and PWM generation isolated from network stack delays."),
        ("Core 1 (IoT Teleoperation):", "Asynchronous HTTP REST server and WebSocket dashboard run smoothly without dropping trapped particles."),
        ("Deterministic Safety:", "Web client queries and Wi-Fi disconnects never affect ongoing ultrasonic levitation.")
    ]),
    ("4. Sub-$30 Open Hardware Testbed", AMBER_ACCENT, [
        ("90% BoM Cost Reduction:", "Standard laboratory acoustic levitators cost $5,000+; this complete system costs under $28."),
        ("5.6 W Battery Portability:", "Consumes 70% less power than multi-transducer kits (TinyLev 18.5W), enabling hours of battery field operation."),
        ("Zero-Install Web Control:", "Control from any smartphone, tablet, or PC browser without proprietary drivers.")
    ])
]

for i_idx, (i_title, i_color, i_points) in enumerate(innovations):
    ix = 0.8 + (i_idx % 2) * 6.0
    iy = 1.6 + (i_idx // 2) * 2.7
    add_card(s12, ix, iy, 5.7, 2.5, bg_color=CARD_BG, border_color=CARD_BORDER)
    i_box = s12.shapes.add_textbox(Inches(ix + 0.2), Inches(iy + 0.15), Inches(5.3), Inches(2.2))
    tf_i = i_box.text_frame
    tf_i.word_wrap = True
    
    p_ih = tf_i.paragraphs[0]
    p_ih.text = i_title
    p_ih.font.name = FONT_HEADING
    p_ih.font.size = Pt(12)
    p_ih.font.bold = True
    p_ih.font.color.rgb = i_color
    
    for pt_h, pt_d in i_points:
        p_pt = tf_i.add_paragraph()
        p_pt.space_before = Pt(3)
        r_ph = p_pt.add_run(pt_h + " ")
        r_ph.font.name = FONT_HEADING
        r_ph.font.size = Pt(9.5)
        r_ph.font.bold = True
        r_ph.font.color.rgb = TEXT_PRIMARY
        r_pd = p_pt.add_run(pt_d)
        r_pd.font.name = FONT_BODY
        r_pd.font.size = Pt(9)
        r_pd.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 13: UNIQUENESS & COMPETITIVE BENCHMARK
# ==========================================
print("Building Slide 13: Competitive Benchmark...")
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "COMPETITIVE BENCHMARK", "Uniqueness & State-of-the-Art System Comparison", "Comparing Proposed ESP32 System against Landmark Academic and Commercial Levitators")

# Full-Width Benchmark Comparison Table
add_card(s13, 0.8, 1.6, 11.733, 5.3, bg_color=CARD_BG, border_color=CYAN_ACCENT, border_width=1.5)
tbl_box = s13.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.9))
tf_tbl = tbl_box.text_frame
tf_tbl.word_wrap = True

p_th = tf_tbl.paragraphs[0]
p_th.text = "MULTI-CRITERIA ARCHITECTURAL COMPARISON:"
p_th.font.name = FONT_HEADING
p_th.font.size = Pt(12)
p_th.font.bold = True
p_th.font.color.rgb = CYAN_ACCENT

comp_headers = [
    ("System Metric", "Langevin Horn Levitation", "TinyLev (Bristol 2017)", "Phased Array (Nature 2015)", "PROPOSED SYSTEM (THIS WORK)")
]

comp_rows = [
    ("Transducer Configuration", "1 Langevin horn + reflector", "72 Open-type 40 kHz PZT", "64 to 256 PZT Transducers", "6 40 kHz PZT (3 Top + 3 Bot)"),
    ("Driving Power Topology", "Analog linear amplifier (>100W)", "Dual L298N H-Bridges (16V)", "Discrete MOSFET array", "Dual L293D Push-Pull (24Vpp)"),
    ("Microcontroller Architecture", "Laboratory Signal Gen.", "Arduino Nano (ATmega328P)", "FPGA / Cyclone V", "ESP32 Dual-Core (80 MHz APB)"),
    ("Phase Control Granularity", "None (Fixed standing wave)", "Fixed in firmware (No dynamic z)", "Phase shift ICs (Complex)", "1.406° Step (~12 µm/deg shift)"),
    ("Wireless Teleoperation", "None (Lab bench tethered)", "None (USB Serial tether only)", "None (Lab workstation)", "Embedded Wi-Fi REST Web UI"),
    ("Total Power Consumption", "120.0 Watts", "18.5 Watts", "35.0 Watts", "5.58 Watts (Ultra-Low Power)"),
    ("Total System Cost (BoM)", "> $4,500 USD", "~ $140 USD", "> $850 USD", "$28 USD (90% Cost Reduction)")
]

table_shape = s13.shapes.add_table(len(comp_rows) + 1, 5, Inches(1.0), Inches(2.3), Inches(11.333), Inches(4.3))
table = table_shape.table

# Column widths
table.columns[0].width = Inches(2.2)
table.columns[1].width = Inches(2.2)
table.columns[2].width = Inches(2.2)
table.columns[3].width = Inches(2.2)
table.columns[4].width = Inches(2.533)

headers = ["System Metric", "Langevin Horn", "TinyLev (2017)", "Phased Array (2015)", "PROPOSED SYSTEM"]
for c_i, h_text in enumerate(headers):
    cell = table.cell(0, c_i)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
    p = cell.text_frame.paragraphs[0]
    p.text = h_text
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT if c_i == 4 else TEXT_PRIMARY
    p.alignment = PP_ALIGN.CENTER

for r_i, r_data in enumerate(comp_rows):
    for c_i, val in enumerate(r_data):
        cell = table.cell(r_i + 1, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(15, 23, 42) if c_i == 4 else (RGBColor(21, 32, 60) if r_i % 2 == 1 else RGBColor(16, 26, 48))
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.name = FONT_BODY
        p.font.size = Pt(9)
        p.font.bold = (c_i == 4 or c_i == 0)
        p.font.color.rgb = GREEN_ACCENT if (c_i == 4 and r_i in [5, 6]) else (CYAN_ACCENT if c_i == 4 else TEXT_PRIMARY)
        if c_i > 0:
            p.alignment = PP_ALIGN.CENTER

# ==========================================
# SLIDE 14: TARGET APPLICATIONS & IMPACT
# ==========================================
print("Building Slide 14: Applications & Impact...")
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "PRACTICAL APPLICATIONS", "Target Use Cases & Sustainable Development Impact", "Transforming Biomedical Research, Cleanroom Assembly, and Chemical Titration")

apps = [
    ("Contactless Bio-Assays", CYAN_ACCENT, "Pharmaceutical & Medical", [
        ("Cell & Bacteria Handling:", "Levitates living cells, blood samples, and delicate protein crystals without solid shear stress or container contamination."),
        ("Zero Bio-Adhesion Loss:", "Eliminates surface adhesion losses inherent to standard petri dishes and glass test tubes during microscopic assays.")
    ]),
    ("Cleanroom Micro-Assembly", GREEN_ACCENT, "Semiconductor & MEMS", [
        ("Frictionless Positioning:", "Positions tiny semiconductor dies, surface-mount components, and fragile MEMS sensors without mechanical tweezers."),
        ("Electrostatic Protection:", "Contactless handling prevents electrostatic discharge (ESD) shocks that destroy delicate microscopic integrated circuits.")
    ]),
    ("Microfluidic Titration", VIOLET_ACCENT, "Analytical Chemistry", [
        ("Containerless Synthesis:", "Enables ultra-pure droplet coalescence, evaporation, and crystallization in free air without vessel wall impurities."),
        ("Zero Plastic Waste:", "Eliminates consumption of single-use disposable pipette tips and reagent vials, reducing laboratory plastic pollution.")
    ]),
    ("UN SDG Alignment", AMBER_ACCENT, "Global Sustainability", [
        ("SDG 3 (Health):", "Prevents sample bio-contamination and supports rapid disease diagnosis through sterile in-air droplet analysis."),
        ("SDG 9 (Innovation):", "Democratizes access to high-end acoustic manipulation apparatus for developing universities at sub-$30 cost."),
        ("SDG 12 (Responsible):", "Eliminates disposable plastic consumable waste during high-throughput microscopic chemical testing.")
    ])
]

for a_idx, (a_title, a_color, a_cat, a_points) in enumerate(apps):
    ax = 0.8 + (a_idx % 2) * 6.0
    ay = 1.6 + (a_idx // 2) * 2.7
    add_card(s14, ax, ay, 5.7, 2.5, bg_color=CARD_BG, border_color=CARD_BORDER)
    a_box = s14.shapes.add_textbox(Inches(ax + 0.2), Inches(ay + 0.15), Inches(5.3), Inches(2.2))
    tf_a = a_box.text_frame
    tf_a.word_wrap = True
    
    p_ah = tf_a.paragraphs[0]
    p_ah.text = a_title.upper()
    p_ah.font.name = FONT_HEADING
    p_ah.font.size = Pt(12)
    p_ah.font.bold = True
    p_ah.font.color.rgb = a_color
    
    r_ac = p_ah.add_run(f"  [{a_cat}]")
    r_ac.font.name = FONT_BODY
    r_ac.font.size = Pt(9.5)
    r_ac.font.color.rgb = TEXT_MUTED
    r_ac.font.bold = False
    
    for pt_h, pt_d in a_points:
        p_pt = tf_a.add_paragraph()
        p_pt.space_before = Pt(3)
        r_ph = p_pt.add_run(pt_h + " ")
        r_ph.font.name = FONT_HEADING
        r_ph.font.size = Pt(9.5)
        r_ph.font.bold = True
        r_ph.font.color.rgb = TEXT_PRIMARY
        r_pd = p_pt.add_run(pt_d)
        r_pd.font.name = FONT_BODY
        r_pd.font.size = Pt(9)
        r_pd.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 15: CONCLUSION & FUTURE ROADMAP
# ==========================================
print("Building Slide 15: Conclusion & Roadmap...")
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "PROJECT SUMMARY", "Conclusion & Future Research Horizons", "Validated Achievements, Technical Deliverables, and Scaling Opportunities")

# Left Column: Project Deliverables Summary
add_card(s15, 0.8, 1.6, 5.8, 5.3, bg_color=CARD_BG, border_color=GREEN_ACCENT, border_width=1.5)
con_box = s15.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.4), Inches(4.9))
tf_con = con_box.text_frame
tf_con.word_wrap = True

p_conh = tf_con.paragraphs[0]
p_conh.text = "CORE PROJECT CONTRIBUTIONS:"
p_conh.font.name = FONT_HEADING
p_conh.font.size = Pt(12)
p_conh.font.bold = True
p_conh.font.color.rgb = GREEN_ACCENT

con_pts = [
    ("Fully Realized Hardware Testbed:", "Engineered and validated a 6-transducer acoustic levitator delivering 24 Vpp differential push-pull drive from a 12V supply with peak 154.2 dB SPL."),
    ("Hardware APB Clock Synchronization:", "Achieved zero-jitter 40 kHz square wave generation with 1.406° timer resolution (~12 µm/deg axial displacement sensitivity)."),
    ("Asynchronous IoT Web Teleoperation:", "Served single-page HTML5/JS dashboard natively on Core 1 over 2.4 GHz Wi-Fi with sub-15 ms latency and zero node drop."),
    ("Comprehensive Academic Documentation:", "Produced full 43-page B.Tech thesis, 10 scientific figures (300 DPI), schematic diagrams, complete Arduino firmware, and presentations.")
]

for ct, cd in con_pts:
    p_c = tf_con.add_paragraph()
    p_c.space_before = Pt(8)
    r_ct = p_c.add_run(ct + "\n")
    r_ct.font.name = FONT_HEADING
    r_ct.font.size = Pt(10.5)
    r_ct.font.bold = True
    r_ct.font.color.rgb = TEXT_PRIMARY
    r_cd = p_c.add_run(cd)
    r_cd.font.name = FONT_BODY
    r_cd.font.size = Pt(9.5)
    r_cd.font.color.rgb = TEXT_MUTED

# Right Column: Future Roadmap
add_card(s15, 6.9, 1.6, 5.6, 5.3, bg_color=CARD_BG, border_color=CYAN_ACCENT, border_width=1.5)
road_box = s15.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.9))
tf_road = road_box.text_frame
tf_road.word_wrap = True

p_rodh = tf_road.paragraphs[0]
p_rodh.text = "FUTURE RESEARCH ROADMAP:"
p_rodh.font.name = FONT_HEADING
p_rodh.font.size = Pt(12)
p_rodh.font.bold = True
p_rodh.font.color.rgb = CYAN_ACCENT

road_pts = [
    ("1. 3D Phased Array Scaling (32–64 TX):", "Expand beyond axial z-manipulation to full 3D Cartesian positioning (x, y, z) using multichannel shift register drivers."),
    ("2. Closed-Loop Optical Vision Feedback:", "Integrate an ESP32-CAM module running edge optical flow tracking to automatically compensate for ambient air currents and evaporation."),
    ("3. Multi-Droplet Coalescence:", "Acoustically suspend and merge distinct chemical reagent droplets in mid-air to synthesize pharmaceutical compounds without container walls."),
    ("4. Commercial Cleanroom Integration:", "Design standardized industrial mounting fixtures for contactless silicon wafer micro-component pick-and-place.")
]

for rt, rd in road_pts:
    p_r = tf_road.add_paragraph()
    p_r.space_before = Pt(8)
    r_rt = p_r.add_run(rt + "\n")
    r_rt.font.name = FONT_HEADING
    r_rt.font.size = Pt(10.5)
    r_rt.font.bold = True
    r_rt.font.color.rgb = TEXT_PRIMARY
    r_rd = p_r.add_run(rd)
    r_rd.font.name = FONT_BODY
    r_rd.font.size = Pt(9.5)
    r_rd.font.color.rgb = TEXT_MUTED

# Save presentation
print(f"Saving presentation to {output_path}...")
prs.save(output_path)
print("Presentation successfully created!")
