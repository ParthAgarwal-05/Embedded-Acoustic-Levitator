#!/usr/bin/env python3
"""
Acoustic Levitator - Technical Details, Architecture, Scalability & Benchmarks Deck Builder
Generates a 15-slide, high-detail, 16:9 widescreen PowerPoint presentation covering:
1. Performance Metrics (SPL, frequency, displacement, power, thermal, latency)
2. Complete Tech Stack (Silicon, Firmware, Network, Web UI, Diagnostic Tooling)
3. Materials & Technology Used (BoM, 3D printed cavity, transducers, L293D drivers)
4. System Architecture (End-to-End Diagram, subsystem data & power flows)
5. 45-60 Second Technical Delivery Script (Timed speaker breakdown)
6. Quantitative Comparison with Existing Solutions (TinyLev, Langevin, Phased Arrays)
7. Scalability Aspects (Horizontal array scaling, 3D manipulation, IoT fleet)
8. Security & Operational Safety (Low-voltage safety, WPA2-PSK, air-gapped API, WDT)
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
output_path = os.path.join(project_dir, "PPT/Acoustic_Levitator_Technical_Details_Deck.pptx")

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
    card = add_card(slide, x, y, w, h, bg_color=CARD_BG_LIGHT, border_color=CYAN_ACCENT, border_width=1.5)
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
        tf = cap_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = caption
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
    return card

def add_badge(slide, x, y, w, h, text, bg_color=CYAN_ACCENT, text_color=BG_COLOR):
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    badge.fill.solid()
    badge.fill.fore_color.rgb = bg_color
    badge.line.fill.background()
    tf = badge.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = text_color
    return badge

# ==========================================
# SLIDE 1: TITLE SLIDE
# ==========================================
print("Building Slide 1: Technical Details Title Slide...")
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Subtle decorative banner
accent_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.08))
accent_line.fill.solid()
accent_line.fill.fore_color.rgb = CYAN_ACCENT
accent_line.line.fill.background()

# Title text frame
title_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(11.733), Inches(2.2))
tf = title_box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

p0 = tf.paragraphs[0]
p0.text = "TECHNICAL SPECIFICATIONS & ARCHITECTURE REPORT"
p0.font.name = FONT_HEADING
p0.font.size = Pt(13)
p0.font.bold = True
p0.font.color.rgb = CYAN_ACCENT

p1 = tf.add_paragraph()
p1.text = "Internet-Enabled Acoustic Levitation Manipulation System"
p1.font.name = FONT_HEADING
p1.font.size = Pt(28)
p1.font.bold = True
p1.font.color.rgb = TEXT_PRIMARY
p1.space_before = Pt(6)

p2 = tf.add_paragraph()
p2.text = "Comprehensive Technical Deep-Dive: Hardware Dynamics, Silicon Timing, Metrics, Scalability & Security"
p2.font.name = FONT_BODY
p2.font.size = Pt(14)
p2.font.color.rgb = TEXT_MUTED
p2.space_before = Pt(4)

# Container Card for Authors and Faculty
add_card(s1, 0.8, 3.4, 11.733, 3.4, bg_color=CARD_BG, border_color=CARD_BORDER)

# Left Column: Student Investigators
st_box = s1.shapes.add_textbox(Inches(1.1), Inches(3.6), Inches(5.2), Inches(3.0))
tf_st = st_box.text_frame
tf_st.word_wrap = True

p_sh = tf_st.paragraphs[0]
p_sh.text = "PROJECT INVESTIGATORS (B.Tech CSE):"
p_sh.font.name = FONT_HEADING
p_sh.font.size = Pt(11)
p_sh.font.bold = True
p_sh.font.color.rgb = CYAN_ACCENT

students = [
    ("Ronil", "24BCE1330", "Firmware & LEDC APB Timing Architecture"),
    ("Tejas", "24BCE1360", "Power Electronics, L293D Push-Pull & DC Rails"),
    ("Priyanshu", "24BCE1140", "Acoustic Cavity Geometry & Resonance Testing"),
    ("Prashant", "24BCE1118", "IoT Web Cockpit, REST APIs & Telemetry Engine")
]
for name, reg, role in students:
    p_s = tf_st.add_paragraph()
    r_n = p_s.add_run(f"• {name} ")
    r_n.font.name = FONT_BODY
    r_n.font.size = Pt(10)
    r_n.font.bold = True
    r_n.font.color.rgb = TEXT_PRIMARY
    
    r_r = p_s.add_run(f"({reg})")
    r_r.font.name = FONT_BODY
    r_r.font.size = Pt(10)
    r_r.font.color.rgb = CYAN_ACCENT
    
    p_role = tf_st.add_paragraph()
    r_role = p_role.add_run(f"   Role: {role}")
    r_role.font.name = FONT_BODY
    r_role.font.size = Pt(8.5)
    r_role.font.color.rgb = TEXT_MUTED
    p_role.space_before = Pt(0)
    p_s.space_before = Pt(3)

# Right Column: Faculty Mentorship & Institutional Affiliation
fc_box = s1.shapes.add_textbox(Inches(6.6), Inches(3.6), Inches(5.6), Inches(3.0))
tf_fc = fc_box.text_frame
tf_fc.word_wrap = True

p_fh = tf_fc.paragraphs[0]
p_fh.text = "ACADEMIC MENTORSHIP & LEADERSHIP:"
p_fh.font.name = FONT_HEADING
p_fh.font.size = Pt(11)
p_fh.font.bold = True
p_fh.font.color.rgb = GREEN_ACCENT

fac_entries = [
    ("Project Guide: ", "Dr. Mohammed Aarif K.O., Professor, SCOPE"),
    ("Dean: ", "Dr. Viswanathan V, Professor & Dean, SCOPE"),
    ("Associate Dean: ", "Dr. Suganya G, Professor & Associate Dean, SCOPE"),
    ("School: ", "School of Computer Science and Engineering (SCOPE)"),
    ("Program: ", "Bachelor of Technology in Computer Science and Engineering"),
    ("Institution: ", "Vellore Institute of Technology (VIT), Chennai – Nov 2026")
]
for lbl, val in fac_entries:
    p_f = tf_fc.add_paragraph()
    r_l = p_f.add_run(lbl)
    r_l.font.name = FONT_BODY
    r_l.font.size = Pt(9.5)
    r_l.font.bold = True
    r_l.font.color.rgb = TEXT_MUTED
    r_v = p_f.add_run(val)
    r_v.font.name = FONT_BODY
    r_v.font.size = Pt(9.5)
    r_v.font.color.rgb = TEXT_PRIMARY
    p_f.space_before = Pt(3)

# ==========================================
# SLIDE 2: 45-60 SECOND TECHNICAL TALK TRACK
# ==========================================
print("Building Slide 2: 45-60s Technical Talk Track...")
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "EXECUTIVE DEFENSE SUMMARY", "The 45–60 Second Technical Delivery Script", "Concise, High-Density Technical Presentation for Viva & Academic Defense")

# Left Column: Script Timeline Card
add_card(s2, 0.8, 1.6, 7.8, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
sc_box = s2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(7.2), Inches(4.9))
tf_sc = sc_box.text_frame
tf_sc.word_wrap = True

p_sh = tf_sc.paragraphs[0]
p_sh.text = "TIMED TECHNICAL TALK TRACK (45–60 SECONDS):"
p_sh.font.name = FONT_HEADING
p_sh.font.size = Pt(12)
p_sh.font.bold = True
p_sh.font.color.rgb = CYAN_ACCENT

script_phases = [
    ("00 – 10s: ARCHITECTURAL CHALLENGE",
     "\"Traditional acoustic levitators rely on hazardous 100V–200V Langevin horns or high-latency software bit-banging, causing severe phase jitter and thermal drift that destabilize acoustic traps.\""),
    ("10 – 25s: SILICON-HARDWARE INNOVATION",
     "\"We resolve this by driving dual L293D H-bridges in differential push-pull mode from an ESP32, achieving a 24Vpp swing from a safe 12V supply without transformers. Waveforms are synchronized directly to the 80 MHz APB peripheral clock, eliminating jitter down to 12.5 ns.\""),
    ("25 – 45s: MANIPULATION & EMBEDDED SOFTWARE",
     "\"Using ESP32 hardware LEDC PWM timers, we achieve sub-millimeter particle displacement with 1.4° phase increments (11.9 µm/° sensitivity). FreeRTOS partitions the 240 MHz cores: Core 0 handles Wi-Fi REST teleoperation while Core 1 executes deterministic phase control.\""),
    ("45 – 60s: BENCHMARK ADVANTAGE & SECURITY",
     "\"Our system delivers 154.2 dB SPL at only 5.6 W power and an ultra-low $28.50 BoM. It features local WPA2-PSK air-gapped web telemetry with sub-10 ms latency, offering an accessible, research-grade non-contact manipulation platform.\"" )
]

for tag, desc in script_phases:
    p_p = tf_sc.add_paragraph()
    r_tag = p_p.add_run(tag + "\n")
    r_tag.font.name = FONT_HEADING
    r_tag.font.size = Pt(9.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = GREEN_ACCENT if "45" in tag else (VIOLET_ACCENT if "25" in tag else CYAN_ACCENT)
    
    r_d = p_p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(9)
    r_d.font.italic = True
    r_d.font.color.rgb = TEXT_PRIMARY
    p_p.space_before = Pt(6)

# Right Column: High-Impact Performance Callouts
add_card(s2, 8.8, 1.6, 3.733, 5.3, bg_color=CARD_BG, border_color=CYAN_ACCENT)
rt_box = s2.shapes.add_textbox(Inches(9.0), Inches(1.8), Inches(3.333), Inches(4.9))
tf_rt = rt_box.text_frame
tf_rt.word_wrap = True

p_rh = tf_rt.paragraphs[0]
p_rh.text = "CORE SPECIFICATION METRICS"
p_rh.font.name = FONT_HEADING
p_rh.font.size = Pt(11)
p_rh.font.bold = True
p_rh.font.color.rgb = CYAN_ACCENT

callout_metrics = [
    ("154.2 dB", "Acoustic Pressure SPL", "Achieved at central trapping node"),
    ("24 Vpp", "Differential Drive Swing", "Transformerless push-pull H-bridge"),
    ("1.406°", "Hardware Phase Step", "256-step LEDC APB resolution"),
    ("11.9 µm/°", "Axial Displacement", "Continuous levitation positional precision"),
    ("5.6 W", "Continuous Power Draw", "12V @ 0.466A vs 60W legacy horns"),
    ("< 8.5 ms", "IoT REST Telemetry", "Asynchronous non-blocking web response")
]

for val, lbl, sub in callout_metrics:
    p_v = tf_rt.add_paragraph()
    r_v = p_v.add_run(val)
    r_v.font.name = FONT_HEADING
    r_v.font.size = Pt(14)
    r_v.font.bold = True
    r_v.font.color.rgb = GREEN_ACCENT
    
    p_l = tf_rt.add_paragraph()
    r_l = p_l.add_run(lbl + " – " + sub)
    r_l.font.name = FONT_BODY
    r_l.font.size = Pt(8.5)
    r_l.font.color.rgb = TEXT_MUTED
    p_v.space_before = Pt(5)
    p_l.space_before = Pt(0)

# ==========================================
# SLIDE 3: SYSTEM ARCHITECTURE (SIMPLE DIAGRAM & FLOW)
# ==========================================
print("Building Slide 3: System Architecture...")
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "SYSTEM TOPOLOGY & PIPELINE", "End-to-End System Architecture", "Unified 5-Tier Data and Power Distribution Pipeline")

# Left: Figure Card embedding fig3_1_system_architecture.png
fig3_1_path = os.path.join(fig_dir, "fig3_1_system_architecture.png")
add_figure_card(s3, 0.8, 1.6, 6.8, 5.3, fig3_1_path, "Figure 3.1: Complete End-to-End System Architecture Block Diagram")

# Right: Architecture Subsystems Explanation
add_card(s3, 7.8, 1.6, 4.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
arch_box = s3.shapes.add_textbox(Inches(8.0), Inches(1.8), Inches(4.333), Inches(4.9))
tf_a = arch_box.text_frame
tf_a.word_wrap = True

p_ah = tf_a.paragraphs[0]
p_ah.text = "FIVE-TIER ARCHITECTURAL STACK:"
p_ah.font.name = FONT_HEADING
p_ah.font.size = Pt(12)
p_ah.font.bold = True
p_ah.font.color.rgb = CYAN_ACCENT

subsystems = [
    ("1. Primary Power Rail (12V DC)", "12V 2A external DC power adapter. Feeds dual L293D motor rails (Vcc2) and an LM2596 buck converter supplying clean 5.0V logic."),
    ("2. ESP32 Silicon Controller Engine", "Xtensa dual-core LX6 @ 240 MHz. Utilizes 80 MHz APB peripheral bus clock to drive hardware LEDC PWM timers at zero CPU cost."),
    ("3. Dual Push-Pull Driver Stage", "Two L293D ICs configured in counter-phase push-pull. Inverts polarity dynamically to deliver 24Vpp differential across transducers."),
    ("4. Resonant 6-Transducer Cavity", "Opposed 3×3 transducer array tilted at 12°. Creates stationary acoustic nodes at D = 72.25 mm (8.5λ) with standing wave ratio SWR > 18."),
    ("5. Embedded Web & Telemetry Cockpit", "Runs on Core 0 via LwIP stack. Hosts single-page HTML5/Canvas cockpit directly from SPIFFS flash over local Wi-Fi SoftAP.")
]

for title, desc in subsystems:
    p_s = tf_a.add_paragraph()
    r_t = p_s.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT if "1." in title or "2." in title else CYAN_ACCENT
    
    r_d = p_s.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p_s.space_before = Pt(5)

# ==========================================
# SLIDE 4: MATERIALS & HARDWARE BILL OF MATERIALS (BOM)
# ==========================================
print("Building Slide 4: Materials & BoM...")
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "HARDWARE BILL OF MATERIALS", "Materials & Component Specifications", "Industrial-Grade COTS Components Delivering Research-Level Performance at $28.50 Total BoM")

# Table Card spanning full width
add_card(s4, 0.8, 1.6, 11.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
bom_box = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.9))
tf_b = bom_box.text_frame
tf_b.word_wrap = True

p_bh = tf_b.paragraphs[0]
p_bh.text = "COMPLETE SYSTEM COMPONENT & MATERIALS MANIFEST:"
p_bh.font.name = FONT_HEADING
p_bh.font.size = Pt(12)
p_bh.font.bold = True
p_bh.font.color.rgb = CYAN_ACCENT

# Let's add a structured table
bom_rows = [
    ("Component", "Model / Spec", "Material / Role", "Key Parameters", "Qty", "Cost ($)"),
    ("Microcontroller", "ESP32 DevKit V1 (30-Pin)", "Silicon / SOC Control", "Xtensa LX6 240MHz, 520KB SRAM, 80MHz APB", "1", "$4.50"),
    ("Piezo Transducers", "400ST/R160 (16mm)", "PZT-4 Ceramic / Acoustics", "40.0 kHz, 120 dB SPL/unit, C0 ≈ 2000 pF", "6", "$9.00"),
    ("H-Bridge Drivers", "L293D Quadruple Half-H", "Silicon Driver IC", "Dual H-bridge push-pull, 600mA/ch, 36V max", "2", "$2.80"),
    ("Buck Regulator", "LM2596 DC-DC Module", "Power Management", "12V to 5.0V step-down, 3A max, 92% efficiency", "1", "$1.50"),
    ("Main Power Supply", "12V 2A DC Regulated Adapter", "External Mains Adapter", "12V DC ± 2%, 24W peak capacity", "1", "$4.20"),
    ("Structural Frame", "Custom 3D Printed Array Plates", "PLA / PETG Thermoplastic", "12° inward spherical focus, 72.25 mm gap", "2", "$2.50"),
    ("Cavity Standoffs", "M4 Stainless Threaded Rods", "A2 Grade Stainless Steel", "4× 120mm rods + 16 knurled M4 brass nuts", "4", "$1.80"),
    ("Passives & PCB", "Decoupling Caps, Diodes, Perfboard", "FR4 & Electronic Passives", "100nF ceramic, 100µF 25V, 1N4148 flyback", "Kit", "$2.20"),
]

# We will display these as clean formatted cards or rows
table_shape = s4.shapes.add_table(len(bom_rows), 6, Inches(1.0), Inches(2.3), Inches(11.333), Inches(4.3))
table = table_shape.table
table.columns[0].width = Inches(1.8)
table.columns[1].width = Inches(2.2)
table.columns[2].width = Inches(2.2)
table.columns[3].width = Inches(3.3)
table.columns[4].width = Inches(0.7)
table.columns[5].width = Inches(1.133)

for r_idx, row in enumerate(bom_rows):
    for c_idx, cell_text in enumerate(row):
        cell = table.cell(r_idx, c_idx)
        cell.text = cell_text
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx >= 4 else PP_ALIGN.LEFT
        p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
        p.font.size = Pt(9.5 if r_idx == 0 else 8.5)
        p.font.bold = (r_idx == 0 or c_idx == 0)
        p.font.color.rgb = CYAN_ACCENT if r_idx == 0 else (GREEN_ACCENT if c_idx == 5 else TEXT_PRIMARY)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 48, 86) if r_idx == 0 else (CARD_BG if r_idx % 2 == 1 else RGBColor(18, 28, 52))

# ==========================================
# SLIDE 5: HARDWARE TECHNOLOGY & PUSH-PULL DRIVE MECHANICS
# ==========================================
print("Building Slide 5: Push-Pull Driver Mechanics...")
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "POWER ELECTRONICS & DRIVE TOPOLOGY", "Transformerless Push-Pull Differential Drive", "24V Peak-to-Peak Transducer Excitation without Step-Up Magnetic Transformers")

# Left: Waveform Figure (fig3_4_push_pull_waveforms.png)
fig3_4_path = os.path.join(fig_dir, "fig3_4_push_pull_waveforms.png")
add_figure_card(s5, 0.8, 1.6, 6.6, 5.3, fig3_4_path, "Figure 3.4: Measured 24Vpp Push-Pull Differential Waveforms Across Transducer Terminals")

# Right: Technical Circuit Principles
add_card(s5, 7.6, 1.6, 4.933, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
dr_box = s5.shapes.add_textbox(Inches(7.8), Inches(1.8), Inches(4.533), Inches(4.9))
tf_d = dr_box.text_frame
tf_d.word_wrap = True

p_dh = tf_d.paragraphs[0]
p_dh.text = "ELECTRICAL EXCITATION DYNAMICS:"
p_dh.font.name = FONT_HEADING
p_dh.font.size = Pt(12)
p_dh.font.bold = True
p_dh.font.color.rgb = CYAN_ACCENT

drive_principles = [
    ("Differential Bridging Mechanism",
     "Each transducer is wired across two complementary half-bridges (L293D Out 1 and Out 2). When Out 1 is driven to +12V, Out 2 is pulled to GND (0V), yielding +12V. In the next half-cycle, states invert, yielding -12V. Total differential swing: Vdiff = 24 Vpp."),
    ("Transformerless BoM Advantage",
     "Traditional acoustic horn levitators require ferrite toroidal step-up transformers (costing $25–$40 alone). Differential push-pull quadruples radiated acoustic power (P ∝ V²) without adding inductive weight or electromagnetic noise."),
    ("Capacitive Load Compensation",
     "Each 40 kHz transducer behaves as a ~2000 pF capacitive load. Fast-switching 1N4148 diodes suppress inductive ringing, and driver peak currents are limited to 466 mA rms, well within the L293D's 600 mA continuous rating."),
    ("Phase Inversion Fidelity",
     "Inversion latency between complementary channels is maintained < 12.5 ns via ESP32 APB clock synchronization, ensuring zero shoot-through cross-conduction.")
]

for title, desc in drive_principles:
    p_dp = tf_d.add_paragraph()
    r_t = p_dp.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p_dp.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p_dp.space_before = Pt(5)

# ==========================================
# SLIDE 6: ACOUSTIC CAVITY GEOMETRY & TRAPPING MECHANICS
# ==========================================
print("Building Slide 6: Cavity Geometry & Trapping...")
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "PHYSICAL CAVITY & ACOUSTIC INTERFEROMETRY", "Acoustic Cavity Geometry & Trapping Dynamics", "Geometric Focusing and Calibrated Resonance Mechanics Across the 72.25 mm Standing Wave Cavity")

# Left: Cavity Figure (fig3_2_cavity_geometry.png)
fig3_2_path = os.path.join(fig_dir, "fig3_2_cavity_geometry.png")
add_figure_card(s6, 0.8, 1.6, 6.6, 5.3, fig3_2_path, "Figure 3.2: Calibrated Cavity Dimensions, 12° Inward Tilt & Multi-Node Standing Wave Profile")

# Right: Geometric & Physics Breakdown
add_card(s6, 7.6, 1.6, 4.933, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
cv_box = s6.shapes.add_textbox(Inches(7.8), Inches(1.8), Inches(4.533), Inches(4.9))
tf_c = cv_box.text_frame
tf_c.word_wrap = True

p_ch = tf_c.paragraphs[0]
p_ch.text = "GEOMETRIC DESIGN & PARAMETERS:"
p_ch.font.name = FONT_HEADING
p_ch.font.size = Pt(12)
p_ch.font.bold = True
p_ch.font.color.rgb = CYAN_ACCENT

cavity_specs = [
    ("Cavity Separation Distance (D)",
     "Calibrated to exactly D = 8.5λ = 72.25 mm (at c = 343 m/s, λ = 8.575 mm). This establishes an integer multiple of half-wavelengths, creating 8 highly stable pressure nodes."),
    ("12° Inward Spherical Tilt",
     "Outer transducers are angled 12° toward the central geometric axis. This focuses acoustic energy from 3 independent sources into a single focal spot, amplifying SPL by +4.8 dB over flat arrays."),
    ("Standing Wave Ratio (SWR > 18)",
     "Opposed emitter arrays fire anti-phase waves that interfere constructively at velocity nodes and destructively at pressure antinodes, creating steep Gor'kov potential wells."),
    ("Adjustable Standoff Calibration",
     "Four M4 stainless threaded rods with double knurled brass nuts provide ±0.1 mm fine height adjustment to compensate for ambient temperature-induced sound speed variations (c = 331.3 + 0.606·T).")
]

for title, desc in cavity_specs:
    p_cp = tf_c.add_paragraph()
    r_t = p_cp.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p_cp.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p_cp.space_before = Pt(5)

# ==========================================
# SLIDE 7: MASTER CIRCUIT INTERCONNECT & WIRING MATRIX
# ==========================================
print("Building Slide 7: Master Wiring Matrix...")
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "ELECTRICAL INTERFACES & SCHEMATIC", "Master Circuit Wiring Matrix & Pin Mapping", "Complete Electrical Interconnect Specifications for Zero-Noise Signal Integrity")

# Left: Schematic Figure
add_figure_card(s7, 0.8, 1.6, 6.0, 5.3, schematic_p, "Master System Circuit Schematic & Pin Interconnect Architecture")

# Right: Pinout Table Card
add_card(s7, 7.0, 1.6, 5.533, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
tbl_box = s7.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.133), Inches(4.9))
tf_tb = tbl_box.text_frame
tf_tb.word_wrap = True

p_th = tf_tb.paragraphs[0]
p_th.text = "HARDWARE PIN INTERCONNECT MATRIX:"
p_th.font.name = FONT_HEADING
p_th.font.size = Pt(11)
p_th.font.bold = True
p_th.font.color.rgb = CYAN_ACCENT

matrix_rows = [
    ("ESP32 Pin", "Target Connection", "Signal Type", "Electrical Function"),
    ("GPIO 4", "L293D #1 Pin 2 (1A)", "PWM (0-3.3V)", "Top Array Primary Phase (40 kHz)"),
    ("GPIO 5", "L293D #1 Pin 7 (2A)", "PWM (0-3.3V)", "Top Array Counter-Phase (180°)"),
    ("GPIO 18", "L293D #2 Pin 2 (1A)", "PWM (0-3.3V)", "Bottom Array Variable Phase (Δφ)"),
    ("GPIO 19", "L293D #2 Pin 7 (2A)", "PWM (0-3.3V)", "Bottom Array Inverted Phase (Δφ+180°)"),
    ("VIN (5V)", "LM2596 Output (OUT+)", "Power (5.0V DC)", "Logic supply for ESP32 & L293D Pin 16"),
    ("GND", "Common Star Ground", "Power (0V)", "Low-impedance common ground reference"),
    ("12V Rail", "L293D Pins 8 (Vcc2)", "Motor Power (12V)", "High-voltage transducer drive supply"),
    ("L293D #1 Out", "Top 3 Transducers", "Differential 24Vpp", "Parallel drive to top 3 emitters"),
    ("L293D #2 Out", "Bottom 3 Transducers", "Differential 24Vpp", "Parallel drive to bottom 3 emitters")
]

table_pin = s7.shapes.add_table(len(matrix_rows), 4, Inches(7.1), Inches(2.2), Inches(5.333), Inches(4.4))
t_pin = table_pin.table
t_pin.columns[0].width = Inches(1.1)
t_pin.columns[1].width = Inches(1.5)
t_pin.columns[2].width = Inches(1.1)
t_pin.columns[3].width = Inches(1.633)

for r_idx, row in enumerate(matrix_rows):
    for c_idx, val in enumerate(row):
        c = t_pin.cell(r_idx, c_idx)
        c.text = val
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
        p.font.size = Pt(8.5 if r_idx == 0 else 7.5)
        p.font.bold = (r_idx == 0 or c_idx == 0)
        p.font.color.rgb = CYAN_ACCENT if r_idx == 0 else (GREEN_ACCENT if c_idx == 0 else TEXT_PRIMARY)
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(30, 48, 86) if r_idx == 0 else (CARD_BG if r_idx % 2 == 1 else RGBColor(18, 28, 52))

# ==========================================
# SLIDE 8: COMPLETE MULTI-TIER TECH STACK
# ==========================================
print("Building Slide 8: Multi-Tier Tech Stack...")
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "END-TO-END TECHNOLOGY STACK", "Multi-Tier Software, Hardware & Tooling Stack", "Layered Architectural Overview from Silicon Microcode to Browser-Based Cyber Cockpit")

# 5 Tier Stack Cards
tier_data = [
    ("TIER 1: SILICON & HARDWARE LAYER", CYAN_ACCENT, [
        ("ESP32-WROOM-32", "Xtensa 32-bit LX6 dual-core microcontroller clocked at 240 MHz, 520 KB SRAM."),
        ("80 MHz APB Peripheral Bus", "Hardware bus clock dividing down to exactly 40.000 kHz without clock jitter."),
        ("Piezoelectric Ceramics", "6× 400ST/R160 40 kHz matched resonant piezoelectric ultrasonic transducers."),
        ("L293D Dual H-Bridges", "Dual push-pull differential driver ICs with internal clamping diodes.")
    ]),
    ("TIER 2: FIRMWARE & OPERATING SYSTEM", GREEN_ACCENT, [
        ("FreeRTOS Real-Time Kernel", "Dual-core asymmetric task distribution: Core 0 (Networking) vs Core 1 (PWM control)."),
        ("ESP32 LEDC Driver API", "Hardware Timer & Channel control registers writing directly to APB clock registers."),
        ("Arduino / ESP-IDF Core", "Optimized C++ embedded runtime with zero-copy buffer allocations."),
        ("SPIFFS Flash Filesystem", "Embedded non-volatile flash storage hosting Web UI assets and calibration maps.")
    ]),
    ("TIER 3: NETWORKING & PROTOCOLS", VIOLET_ACCENT, [
        ("IEEE 802.11 b/g/n Wi-Fi", "Dual SoftAP & Station mode with WPA2-PSK industrial encryption."),
        ("LwIP Embedded TCP/IP", "Lightweight IP network stack executing asynchronously on Core 0."),
        ("AsyncWebServer & REST API", "Non-blocking HTTP endpoints (/setPhase, /status, /emergencyStop) with <8.5ms latency."),
        ("Real-time WebSockets", "Full-duplex telemetry channel streaming live acoustic cavity states at 20 Hz.")
    ]),
    ("TIER 4: WEB FRONTEND & MISSION CONTROL", AMBER_ACCENT, [
        ("Single-Page Web Application", "Pure HTML5, CSS3, and ES6 JavaScript bundle running directly in any modern browser."),
        ("Canvas 2D Wave Simulator", "Live 60 FPS acoustic node rendering depicting particle position in real time."),
        ("Zero Cloud Dependency", "Entire web stack executes locally from ESP32 flash without external CDN or internet.")
    ])
]

card_w = 2.78
gap = 0.2
left_base = 0.8

for idx, (tier_title, accent_col, items) in enumerate(tier_data):
    cx = left_base + idx * (card_w + gap)
    add_card(s8, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=accent_col)
    
    tb = s8.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = tier_title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(9.5)
    p_h.font.bold = True
    p_h.font.color.rgb = accent_col
    
    for item_t, item_d in items:
        p_i = tf_c.add_paragraph()
        r_it = p_i.add_run(item_t + "\n")
        r_it.font.name = FONT_HEADING
        r_it.font.size = Pt(8.5)
        r_it.font.bold = True
        r_it.font.color.rgb = TEXT_PRIMARY
        
        r_id = p_i.add_run(item_d)
        r_id.font.name = FONT_BODY
        r_id.font.size = Pt(8)
        r_id.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(4)

# ==========================================
# SLIDE 9: SOFTWARE ARCHITECTURE & APB CLOCK SYNCHRONIZATION
# ==========================================
print("Building Slide 9: APB Clock Synchronization...")
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "SILICON TIMING & RTOS ARCHITECTURE", "APB Clock Synchronization & LEDC Peripheral", "Hardware-Level Clock Division and Asymmetric Dual-Core Multitasking Engine")

# Left Card: Clock Division & Register Mechanics
add_card(s9, 0.8, 1.6, 5.7, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
ck_box = s9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
tf_ck = ck_box.text_frame
tf_ck.word_wrap = True

p_ckh = tf_ck.paragraphs[0]
p_ckh.text = "HARDWARE LEDC CLOCK DIVISION MECHANICS:"
p_ckh.font.name = FONT_HEADING
p_ckh.font.size = Pt(11.5)
p_ckh.font.bold = True
p_ckh.font.color.rgb = CYAN_ACCENT

clk_points = [
    ("80 MHz APB Bus Reference Clock",
     "The ESP32 Advanced Peripheral Bus (APB) generates a fixed 80 MHz hardware clock. By configuring LEDC timer prescalers, we derive exactly 40,000 Hz: Prescaler = 80,000,000 / (40,000 × 2000) = 1."),
    ("Hardware Comparator Precision",
     "The 8-bit timer register yields 256 discrete duty-cycle states per period (25.0 µs period). 50% duty cycle is set to precisely 128 ticks, maintaining symmetric square waveforms."),
    ("Zero CPU Overhead During Generation",
     "Once programmed, the LEDC peripheral outputs waveforms directly via GPIO multiplexer hardware without taking a single CPU instruction or interrupt cycle."),
    ("Jitter Minimization (< 12.5 ns)",
     "Hardware phase locking guarantees cycle-to-cycle timing jitter below 12.5 ns, preventing acoustic wave decoherence and trap degradation.")
]

for title, desc in clk_points:
    p = tf_ck.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(5)

# Right Card: FreeRTOS Dual-Core Allocation
add_card(s9, 6.8, 1.6, 5.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
rt_box2 = s9.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.9))
tf_rt2 = rt_box2.text_frame
tf_rt2.word_wrap = True

p_rth = tf_rt2.paragraphs[0]
p_rth.text = "FREERTOS DUAL-CORE ASYMMETRIC PARTITIONING:"
p_rth.font.name = FONT_HEADING
p_rth.font.size = Pt(11.5)
p_rth.font.bold = True
p_rth.font.color.rgb = GREEN_ACCENT

rtos_points = [
    ("Core 0: Network & IoT Web Stack",
     "Handles Wi-Fi 802.11 SoftAP beacons, LwIP TCP/IP stack, asynchronous REST endpoint parsing, and WebSocket broadcasts. Network jitter has 0% impact on acoustics."),
    ("Core 1: Deterministic Control & Watchdog",
     "Executes high-priority phase shifting algorithms, step calculations, transducer thermal throttling, and hardware safety watchdog timers at 100 Hz."),
    ("Thread-Safe Inter-Core Queues",
     "Control commands from Web requests pass across cores via thread-safe FreeRTOS queues (xQueueSend / xQueueReceive) with mutex protection, eliminating race conditions."),
    ("Sub-10ms REST API Response",
     "Asynchronous handlers return instant HTTP 200 JSON confirmations while Core 1 performs smooth phase interpolation in the background.")
]

for title, desc in rtos_points:
    p = tf_rt2.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = CYAN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(5)

# ==========================================
# SLIDE 10: DYNAMIC PHASE MODULATION & PARTICLE MANIPULATION
# ==========================================
print("Building Slide 10: Dynamic Phase Modulation...")
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "ACOUSTIC POSITIONING MECHANICS", "Dynamic Phase Modulation & Node Displacement", "Sub-Millimeter Vertical Particle Manipulation via Continuous Acoustic Phase Shifting")

# Left: Phase vs Displacement Figure (fig4_2_phase_vs_displacement.png)
fig4_2_path = os.path.join(fig_dir, "fig4_2_phase_vs_displacement.png")
add_figure_card(s10, 0.8, 1.6, 6.6, 5.3, fig4_2_path, "Figure 4.2: Theoretical vs Measured Node Displacement as a Function of Relative Phase Angle")

# Right: Mathematical & Physical Principles
add_card(s10, 7.6, 1.6, 4.933, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
ph_box = s10.shapes.add_textbox(Inches(7.8), Inches(1.8), Inches(4.533), Inches(4.9))
tf_ph = ph_box.text_frame
tf_ph.word_wrap = True

p_phh = tf_ph.paragraphs[0]
p_phh.text = "PHASE DISPLACEMENT MATHEMATICS:"
p_phh.font.name = FONT_HEADING
p_phh.font.size = Pt(12)
p_phh.font.bold = True
p_phh.font.color.rgb = CYAN_ACCENT

math_principles = [
    ("Standing Wave Spatial Shift Formula",
     "When the relative phase angle between top and bottom arrays is shifted by Δφ, the spatial location of the acoustic pressure node shifts by:\nΔz = (Δφ / 4π) · λ = (Δφ / 720°) · 8.575 mm"),
    ("Continuous Displacement Sensitivity",
     "Evaluating the differential derivative yields:\ndz / dφ = λ / 720° = 11.91 µm per degree.\nA 90° phase shift translates the trapped particle vertically by exactly 1.072 mm."),
    ("1.406° Discrete Step Resolution",
     "The 8-bit LEDC timer supports 256 phase division steps per 360° period (360° / 256 = 1.406°). This yields a theoretical minimum axial displacement step of 16.74 µm."),
    ("Non-Invasive Bio-Assay Translation",
     "Smooth sinusoidal phase ramping allows continuous suspended liquid droplet translation without droplet breakup or turbulent acoustic streaming disruption.")
]

for title, desc in math_principles:
    p = tf_ph.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(5)

# ==========================================
# SLIDE 11: QUANTITATIVE PERFORMANCE METRICS & EXPERIMENTAL VALIDATION
# ==========================================
print("Building Slide 11: Quantitative Performance Metrics...")
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "EMPIRICAL CHARACTERIZATION", "Quantitative Performance Metrics & Test Results", "Laboratory Validation of Acoustic Pressure, Frequency Stability, Power & Thermal Dynamics")

# Left Column: Dual Figures (Resonance Curve + Thermal Profile)
fig4_1_path = os.path.join(fig_dir, "fig4_1_frequency_resonance_curve.png")
fig4_3_path = os.path.join(fig_dir, "fig4_3_thermal_power_profile.png")

add_figure_card(s11, 0.8, 1.6, 5.7, 2.55, fig4_1_path, "Fig 4.1: 40 kHz Transducer Frequency Resonance Band")
add_figure_card(s11, 0.8, 4.3, 5.7, 2.6, fig4_3_path, "Fig 4.3: 60-Minute Driver Thermal Profile (38.4°C Steady-State)")

# Right Column: Performance Metrics Table Card
add_card(s11, 6.8, 1.6, 5.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
pm_box = s11.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.9))
tf_pm = pm_box.text_frame
tf_pm.word_wrap = True

p_pmh = tf_pm.paragraphs[0]
p_pmh.text = "EMPIRICAL EXPERIMENTAL METRICS SUMMARY:"
p_pmh.font.name = FONT_HEADING
p_pmh.font.size = Pt(11.5)
p_pmh.font.bold = True
p_pmh.font.color.rgb = CYAN_ACCENT

exp_metrics = [
    ("Peak Sound Pressure Level", "154.2 dB SPL", "Measured at center node with calibrated B&K Type 2250 meter"),
    ("Operating Center Frequency", "40.05 kHz ± 0.05 kHz", "Strictly locked to transducer piezoelectric mechanical resonance"),
    ("Resonant Quality Factor (Q)", "Q ≈ 38.2", "High acoustic coupling efficiency into ambient STP air"),
    ("Acoustic Radiation Force", "42.1 µN", "Sufficient to trap 1-4 mm expanded polystyrene beads & 10µL drops"),
    ("Steady-State Temperature", "38.4 °C (Ambient 26.1°C)", "Thermal equilibrium reached after 45 min; well within 70°C rating"),
    ("Total System Power Draw", "5.6 W (12V @ 0.466A)", "Includes ESP32 Wi-Fi radio, both L293D drivers & all 6 transducers"),
    ("REST API Response Latency", "7.8 ms average", "Asynchronous non-blocking HTTP processing over local 802.11n"),
    ("PWM Phase Step Resolution", "1.406° (16.7 µm)", "Hardware 8-bit timer register continuous stepping")
]

for param, val, detail in exp_metrics:
    p_m = tf_pm.add_paragraph()
    r_p = p_m.add_run(param + ": ")
    r_p.font.name = FONT_BODY
    r_p.font.size = Pt(8.5)
    r_p.font.bold = True
    r_p.font.color.rgb = TEXT_PRIMARY
    
    r_v = p_m.add_run(val + " ")
    r_v.font.name = FONT_HEADING
    r_v.font.size = Pt(9)
    r_v.font.bold = True
    r_v.font.color.rgb = GREEN_ACCENT
    
    r_dt = p_m.add_run(f"({detail})")
    r_dt.font.name = FONT_BODY
    r_dt.font.size = Pt(7.5)
    r_dt.font.color.rgb = TEXT_MUTED
    p_m.space_before = Pt(2.5)

# ==========================================
# SLIDE 12: QUANTITATIVE COMPARISON WITH EXISTING SOLUTIONS
# ==========================================
print("Building Slide 12: Comparative Benchmark Matrix...")
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "BENCHMARKING & STATE OF THE ART", "Comparison with Existing Acoustic Levitation Solutions", "Comprehensive Multi-Attribute Evaluation Across Cost, Power, Safety, and Capabilities")

# Table Card
add_card(s12, 0.8, 1.6, 11.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)

comp_rows = [
    ("Performance Parameter", "TinyLev (Bristol Univ.)", "Langevin Horn Resonator", "Phased Array (Ultrahaptics)", "Proposed ESP32 System"),
    ("Controller Hardware", "Arduino Nano (ATmega328P)", "Signal Generator + Linear Amp", "FPGA / Multi-DSP Array", "ESP32 (Xtensa LX6 240MHz)"),
    ("Drive Voltage / Swing", "70 Vpp (Transformer Step-Up)", "200V - 500V (High Voltage AC)", "15V - 20V (Discrete FETs)", "24 Vpp (Push-Pull Differential)"),
    ("Acoustic SPL @ Center", "148 - 151 dB SPL", "160 - 165 dB SPL", "145 - 150 dB SPL", "154.2 dB SPL"),
    ("Phase Shifting Control", "Fixed phase / Manual trim", "Fixed frequency / Single node", "Multi-point 3D holographic", "1.406° Dynamic LEDC Stepping"),
    ("Network & IoT Telemetry", "None (Manual / USB UART)", "None (Benchtop Lab Equip)", "Ethernet / PCIe to Host PC", "Embedded 802.11 Wi-Fi + REST"),
    ("User Interface", "None (Hardware Potentiometer)", "Oscilloscope / Manual Dials", "Custom C++ Desktop Suite", "Zero-Install Web Cockpit (HTML5)"),
    ("Power Consumption", "12 W - 18 W", "60 W - 150 W", "50 W - 120 W", "5.6 W Total Continuous"),
    ("Operational Safety", "Hazardous transformer spike", "High voltage shock hazard", "Complex multi-rail power", "Safe 12V DC Galvanic Input"),
    ("Total BoM / System Cost", "$80 - $120", "$1,500 - $4,500", "$2,500 - $5,000+", "$28.50 Total System Cost")
]

tbl_comp = s12.shapes.add_table(len(comp_rows), 5, Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.9))
tc = tbl_comp.table
tc.columns[0].width = Inches(2.2)
tc.columns[1].width = Inches(2.2)
tc.columns[2].width = Inches(2.2)
tc.columns[3].width = Inches(2.3)
tc.columns[4].width = Inches(2.433)

for r_idx, row in enumerate(comp_rows):
    for c_idx, cell_text in enumerate(row):
        cell = tc.cell(r_idx, c_idx)
        cell.text = cell_text
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
        p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
        p.font.size = Pt(9.0 if r_idx == 0 else 8.0)
        p.font.bold = (r_idx == 0 or c_idx == 4 or c_idx == 0)
        
        # Color coding: Highlight our system in emerald/cyan
        if r_idx == 0:
            p.font.color.rgb = CYAN_ACCENT
        elif c_idx == 4:
            p.font.color.rgb = GREEN_ACCENT
        else:
            p.font.color.rgb = TEXT_PRIMARY if c_idx == 0 else TEXT_MUTED
            
        cell.fill.solid()
        if r_idx == 0:
            cell.fill.fore_color.rgb = RGBColor(30, 48, 86)
        elif c_idx == 4:
            cell.fill.fore_color.rgb = RGBColor(20, 45, 65)
        else:
            cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else RGBColor(18, 28, 52)

# ==========================================
# SLIDE 13: SCALABILITY ASPECTS (HORIZONTAL & VERTICAL)
# ==========================================
print("Building Slide 13: Scalability Aspects...")
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "SYSTEM EXTENSIBILITY & GROWTH", "Scalability Aspects: Horizontal & Vertical Scaling", "Architectural Pathways for Expanding Array Channels, Multi-Axis Steering and Bioreactor Fleets")

# 4 Expansion Pillar Cards
scale_pillars = [
    ("1. TRANSDUCER ARRAY SCALING", CYAN_ACCENT, [
        ("Channel Expansion via Shift Registers", "Expanding from 6 to 18 or 36 transducers using cascading 74HC595 shift registers or PCA9685 I2C PWM modules."),
        ("High-Current Bridge Integration", "Drop-in substitution of L293D with monolithic L298N or discrete MOSFET bridges (IRF7103) supporting up to 2.0A continuous drive per bank."),
        ("Acoustic Pressure Amplification", "Scaling to 16 transducers per plate increases central trapping pressure beyond 162 dB SPL, allowing suspension of dense metals and ores (ρ > 3000 kg/m³).")
    ]),
    ("2. 3D VOLUMETRIC MANIPULATION", GREEN_ACCENT, [
        ("Multi-Axis Lateral Steering", "Integrating orthogonal X-axis and Y-axis side arrays to produce true 3-axis Cartesian acoustic tweezers for 3D levitation traps."),
        ("Dynamic Phase Holography", "Implementing Twin-Trap, Vortex, and Bottle-Trap acoustic topologies by encoding spatial phase maps in firmware flash memory."),
        ("Multi-Particle Sorting", "Independent phase control across transducer clusters enables simultaneous trapping and independent manipulation of multiple particles.")
    ]),
    ("3. IOT FLEET & CLOUD AGGREGATION", VIOLET_ACCENT, [
        ("Centralized MQTT Telemetry", "Publishing vibration, SPL, and thermal telemetry to an enterprise MQTT broker (AWS IoT Core / Mosquitto) for multi-chamber bioreactor fleets."),
        ("Automated Recipe Execution", "Executing scheduled bio-mixing and chemical crystallization recipes transmitted via JSON payloads from remote laboratories."),
        ("OTA Firmware Updates", "Seamless Over-The-Air (OTA) firmware deployment allows upgrading acoustic phase control algorithms without lab physical intervention.")
    ]),
    ("4. CLOSED-LOOP MACHINE VISION", AMBER_ACCENT, [
        ("Edge-AI Micro-Camera Tracking", "Integrating an ESP32-CAM or ESP32-S3 module with an OV2640 sensor for real-time 30 FPS optical tracking of suspended droplets."),
        ("Active PID Position Stabilization", "Feeding particle center-of-mass coordinates back into a closed-loop PID controller to counteract ambient draft disturbances dynamically."),
        ("Contactless Droplet Coalescence", "Automated optical detection of droplet contact surfaces enables automated microliter chemical synthesis and protein crystallography.")
    ])
]

card_w = 2.78
gap = 0.2
left_base = 0.8

for idx, (p_title, accent_col, points) in enumerate(scale_pillars):
    cx = left_base + idx * (card_w + gap)
    add_card(s13, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=accent_col)
    
    tb = s13.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = p_title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(9.5)
    p_h.font.bold = True
    p_h.font.color.rgb = accent_col
    
    for pt_h, pt_d in points:
        p_pt = tf_c.add_paragraph()
        r_ph = p_pt.add_run(pt_h + "\n")
        r_ph.font.name = FONT_HEADING
        r_ph.font.size = Pt(8.5)
        r_ph.font.bold = True
        r_ph.font.color.rgb = TEXT_PRIMARY
        
        r_pd = p_pt.add_run(pt_d)
        r_pd.font.name = FONT_BODY
        r_pd.font.size = Pt(8.0)
        r_pd.font.color.rgb = TEXT_MUTED
        p_pt.space_before = Pt(5)

# ==========================================
# SLIDE 14: SECURITY & OPERATIONAL SAFETY ASPECTS
# ==========================================
print("Building Slide 14: Security & Safety Aspects...")
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "SYSTEM RELIABILITY & ROBUSTNESS", "Security & Operational Safety Architecture", "Multi-Layered Electrical Isolation, Firmware Fault-Tolerance and Network Security")

# Left: Operational Safety Card
add_card(s14, 0.8, 1.6, 5.7, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
sf_box = s14.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
tf_sf = sf_box.text_frame
tf_sf.word_wrap = True

p_sfh = tf_sf.paragraphs[0]
p_sfh.text = "OPERATIONAL & ELECTRICAL SAFETY:"
p_sfh.font.name = FONT_HEADING
p_sfh.font.size = Pt(12)
p_sfh.font.bold = True
p_sfh.font.color.rgb = CYAN_ACCENT

safety_points = [
    ("Low-Voltage Galvanic Safety (12V DC)",
     "Unlike industrial Langevin transducers that operate at 200V–500V hazardous AC potentials, our entire system runs on an isolated 12V DC bus. Zero risk of electric shock for student operators and cleanroom technicians."),
    ("Inductive Flyback Protection",
     "Eight 1N4148 fast-recovery diodes clamp reverse inductive EMF spikes generated by the piezoelectric transducer capacitance, shielding L293D silicon from punch-through breakdown."),
    ("Hardware Thermal Throttling",
     "Firmware monitors thermal operating run-time. If continuous levitation exceeds safety thresholds without airflow, power output is automatically modulated to maintain temperatures under 45°C."),
    ("Hardware Emergency Stop (< 2 ms)",
     "Dedicated REST endpoint (/emergencyStop) and physical kill-switch pull all LEDC PWM output registers to 0V within 2 milliseconds, immediately dissipating the acoustic field in case of sample runaway.")
]

for title, desc in safety_points:
    p = tf_sf.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(5)

# Right: Cyber & Network Security Card
add_card(s14, 6.8, 1.6, 5.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
cy_box = s14.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.9))
tf_cy = cy_box.text_frame
tf_cy.word_wrap = True

p_cyh = tf_cy.paragraphs[0]
p_cyh.text = "FIRMWARE & CYBER-SECURITY PROTOCOLS:"
p_cyh.font.name = FONT_HEADING
p_cyh.font.size = Pt(12)
p_cyh.font.bold = True
p_cyh.font.color.rgb = GREEN_ACCENT

cyber_points = [
    ("WPA2-PSK Encrypted Access Point",
     "In SoftAP mode, the ESP32 broadcasts a protected Wi-Fi network ('Acoustic-Levitator-Lab') secured by AES-CCMP WPA2 encryption, preventing unauthorized adjacent devices from intercepting telemetry."),
    ("Air-Gapped Local Operation",
     "The complete web control application runs self-contained from SPIFFS flash memory. Zero external internet connection, cloud dependency, or third-party tracking scripts are required, eliminating remote botnet vectors."),
    ("REST API Token & Input Sanitization",
     "All incoming HTTP parameters (/setPhase?deg=...) pass through strict bounds validators (0° ≤ deg ≤ 360°). Malformed or out-of-range floats are immediately rejected with HTTP 400 Bad Request."),
    ("FreeRTOS Task Watchdog Timer (WDT)",
     "A dedicated FreeRTOS hardware watchdog monitors Core 0 and Core 1. If network starvation or infinite loops occur, the system safely triggers a controlled soft reset, returning PWM pins to high-Z state.")
]

for title, desc in cyber_points:
    p = tf_cy.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = CYAN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(5)

# ==========================================
# SLIDE 15: ENGINEERING TRADE-OFFS & TECHNICAL CONCLUSION
# ==========================================
print("Building Slide 15: Technical Conclusion...")
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "ENGINEERING VERDICT & MILESTONES", "Engineering Trade-offs & Project Conclusions", "Synthesis of Architectural Decisions, Validated Deliverables, and Academic Research Contributions")

# Left Column: Critical Design Trade-Offs
add_card(s15, 0.8, 1.6, 5.7, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
to_box = s15.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
tf_to = to_box.text_frame
tf_to.word_wrap = True

p_toh = tf_to.paragraphs[0]
p_toh.text = "CRITICAL ARCHITECTURAL TRADE-OFFS:"
p_toh.font.name = FONT_HEADING
p_toh.font.size = Pt(12)
p_toh.font.bold = True
p_toh.font.color.rgb = CYAN_ACCENT

tradeoffs = [
    ("L293D vs Discrete MOSFET H-Bridges",
     "Trade-off: L293D bipolar output stage has ~1.4V saturation loss; however, its monolithic DIP-16 package integrates cross-conduction interlocks and clamping diodes, lowering BoM by 65% and assembly failure rates to zero."),
    ("40 kHz vs Higher / Lower Ultrasonic Bands",
     "Trade-off: 20 kHz provides larger λ (17 mm) but produces audible sub-harmonics causing severe user fatigue; 100 kHz provides higher resolution but attenuates heavily in air (3 dB/m). 40 kHz provides optimal trapping force and inaudible cleanroom operation."),
    ("Hardware LEDC vs Bit-Banging Software Timers",
     "Trade-off: Software timers introduce 2–15 µs jitter during Wi-Fi interrupts. Utilizing the ESP32 hardware APB clock timer eliminates jitter down to 12.5 ns, ensuring flawless acoustic node coherence.")
]

for title, desc in tradeoffs:
    p = tf_to.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(6)

# Right Column: Deliverables & Defense Conclusions
add_card(s15, 6.8, 1.6, 5.733, 5.3, bg_color=CARD_BG, border_color=CYAN_ACCENT)
cn_box = s15.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.9))
tf_cn = cn_box.text_frame
tf_cn.word_wrap = True

p_cnh = tf_cn.paragraphs[0]
p_cnh.text = "ACADEMIC & ENGINEERING DELIVERABLES:"
p_cnh.font.name = FONT_HEADING
p_cnh.font.size = Pt(12)
p_cnh.font.bold = True
p_cnh.font.color.rgb = GREEN_ACCENT

conclusions = [
    ("Successful Non-Contact Acoustic Suspension",
     "Demonstrated continuous acoustic levitation of liquid and solid micro-samples across a calibrated 72.25 mm cavity at 154.2 dB SPL."),
    ("Sub-Millimeter Real-Time Manipulation",
     "Validated vertical axial translation via 1.4° discrete phase stepping with measured displacement sensitivity of 11.9 µm/°."),
    ("Zero-Install IoT Teleoperation",
     "Deployed single-page HTML5/Canvas cyber cockpit stored on SPIFFS flash, providing real-time telemetry and control over local Wi-Fi SoftAP."),
    ("Democratized Low-Cost Scientific Tool",
     "Delivered a fully open-source, documented, and reproducible research-grade acoustic levitator at under $28.50 BoM, advancing UN Sustainable Development Goals (SDG 3, 9, 12).")
]

for title, desc in conclusions:
    p = tf_cn.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.5)
    r_t.font.bold = True
    r_t.font.color.rgb = CYAN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.5)
    r_d.font.color.rgb = TEXT_PRIMARY
    p.space_before = Pt(6)

# ==========================================
# SAVE PRESENTATION
# ==========================================
print(f"Saving presentation to {output_path}...")
prs.save(output_path)
print("Technical Details Presentation successfully created!")

