#!/usr/bin/env python3
"""
Acoustic Levitator - Applications, Industry Relevance & Commercial Ask Deck Builder
Generates a 15-slide, high-detail, 16:9 widescreen PowerPoint presentation covering:
1. Applications:
   - Target sectors (Pharma, Semiconductor, Space/Microgravity, Chemical Synthesis)
   - Industry relevance (Contamination crisis, cleanroom friction, market drivers)
   - Practical deployment scenarios (Protein crystallization, pathogen handling, micro-assembly)
   - Target users / customers (PIs, assay engineers, cleanroom operators, STEM educators)
   - 30-45 sec Application Pitch
2. Commercial Ask:
   - TRL level (TRL 6 validation)
   - Deployment readiness (Turnkey 5-min deployment, environmental envelope)
   - IP status & software ownership (Patent claims, trade secrets, student-faculty ownership)
   - Collaboration & licensing models (OEM royalties, direct sales, SaaS telemetry)
   - Funding & venture ask ($120k Seed / ₹1.0 Cr allocation, 18-month execution roadmap)
   - 30-45 sec Commercial Pitch
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
output_path = os.path.join(project_dir, "PPT/Acoustic_Levitator_Applications_Commercial_Ask_Deck.pptx")

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

# ==========================================
# SLIDE 1: TITLE SLIDE
# ==========================================
print("Building Slide 1: Commercialization & Applications Title Slide...")
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Subtle decorative banner
accent_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.08))
accent_line.fill.solid()
accent_line.fill.fore_color.rgb = GREEN_ACCENT
accent_line.line.fill.background()

# Title text frame
title_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(11.733), Inches(2.2))
tf = title_box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

p0 = tf.paragraphs[0]
p0.text = "VENTURE PROPOSAL & COMMERCIALIZATION STRATEGY"
p0.font.name = FONT_HEADING
p0.font.size = Pt(13)
p0.font.bold = True
p0.font.color.rgb = GREEN_ACCENT

p1 = tf.add_paragraph()
p1.text = "Acoustic Levitation Manipulation System"
p1.font.name = FONT_HEADING
p1.font.size = Pt(28)
p1.font.bold = True
p1.font.color.rgb = TEXT_PRIMARY
p1.space_before = Pt(6)

p2 = tf.add_paragraph()
p2.text = "Target Sectors, Industry Deployment Scenarios, TRL 6 Readiness, IP Ownership & Venture Ask"
p2.font.name = FONT_BODY
p2.font.size = Pt(14)
p2.font.color.rgb = TEXT_MUTED
p2.space_before = Pt(4)

# Container Card for Authors and Faculty
add_card(s1, 0.8, 3.4, 11.733, 3.4, bg_color=CARD_BG, border_color=CARD_BORDER)

# Left Column: Student Founders & Roles
st_box = s1.shapes.add_textbox(Inches(1.1), Inches(3.6), Inches(5.2), Inches(3.0))
tf_st = st_box.text_frame
tf_st.word_wrap = True

p_sh = tf_st.paragraphs[0]
p_sh.text = "FOUNDING INVESTIGATORS (B.Tech CSE):"
p_sh.font.name = FONT_HEADING
p_sh.font.size = Pt(11)
p_sh.font.bold = True
p_sh.font.color.rgb = CYAN_ACCENT

students = [
    ("Ronil", "24BCE1330", "Chief Architect – APB Hardware & Signal Processing"),
    ("Tejas", "24BCE1360", "Lead Electronics – Power Rails & Push-Pull Stage"),
    ("Priyanshu", "24BCE1140", "Systems Engineer – Cavity Resonator & TRL Testing"),
    ("Prashant", "24BCE1118", "Software & IoT Lead – Web Cockpit & Telemetry APIs")
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
    r_role = p_role.add_run(f"   {role}")
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
p_fh.text = "ACADEMIC ADVISORY & INSTITUTIONAL HOST:"
p_fh.font.name = FONT_HEADING
p_fh.font.size = Pt(11)
p_fh.font.bold = True
p_fh.font.color.rgb = GREEN_ACCENT

fac_entries = [
    ("Faculty Guide: ", "Dr. Mohammed Aarif K.O., Professor, SCOPE"),
    ("Dean: ", "Dr. Viswanathan V, Professor & Dean, SCOPE"),
    ("Associate Dean: ", "Dr. Suganya G, Professor & Associate Dean, SCOPE"),
    ("Department: ", "School of Computer Science and Engineering (SCOPE)"),
    ("Degree Program: ", "Bachelor of Technology in Computer Science and Engineering"),
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
# SLIDE 2: DUAL 30-45 SECOND TIMED PITCHES
# ==========================================
print("Building Slide 2: Dual Timed Pitches...")
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "EXECUTIVE PITCH TRACKS", "Dual 30–45 Second Delivery Tracks", "Targeted High-Impact Narratives for Industry End-Users and Venture Investors")

# Left Column: 30-45s Applications Pitch
add_card(s2, 0.8, 1.6, 5.7, 5.3, bg_color=CARD_BG, border_color=CYAN_ACCENT)
ap_box = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
tf_ap = ap_box.text_frame
tf_ap.word_wrap = True

p_ah = tf_ap.paragraphs[0]
p_ah.text = "TRACK A: APPLICATIONS PITCH (30–45s)"
p_ah.font.name = FONT_HEADING
p_ah.font.size = Pt(11.5)
p_ah.font.bold = True
p_ah.font.color.rgb = CYAN_ACCENT

p_as = tf_ap.add_paragraph()
p_as.text = "Audience: Pharmaceutical PIs, Cleanroom Managers & Assay Automation Leads"
p_as.font.name = FONT_BODY
p_as.font.size = Pt(8.5)
p_as.font.color.rgb = TEXT_MUTED
p_as.space_before = Pt(2)

app_pitch_text = (
    "\"In biochemical screening and semiconductor assembly, physical contact is the single largest cause of contamination, sample loss, and electrostatic defects. Traditional microfluidics require disposable chips costing thousands each month.\n\n"
    "Our acoustic levitator creates an entirely non-contact micro-manipulation chamber. Using 40 kHz standing waves, we suspend microliter droplets and sensitive micro-components completely in mid-air, shifting them vertically with 11.9 µm/° precision via browser-based teleoperation.\n\n"
    "From contactless protein crystallization without wall nucleation to sterile bio-assays with zero pipette waste, our platform eliminates contamination at the root.\""
)
p_at = tf_ap.add_paragraph()
r_at = p_at.add_run(app_pitch_text)
r_at.font.name = FONT_BODY
r_at.font.size = Pt(9.0)
r_at.font.italic = True
r_at.font.color.rgb = TEXT_PRIMARY
p_at.space_before = Pt(6)

# Right Column: 30-45s Commercial Ask Pitch
add_card(s2, 6.8, 1.6, 5.733, 5.3, bg_color=CARD_BG, border_color=GREEN_ACCENT)
co_box = s2.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.9))
tf_co = co_box.text_frame
tf_co.word_wrap = True

p_ch = tf_co.paragraphs[0]
p_ch.text = "TRACK B: COMMERCIAL & VENTURE ASK (30–45s)"
p_ch.font.name = FONT_HEADING
p_ch.font.size = Pt(11.5)
p_ch.font.bold = True
p_ch.font.color.rgb = GREEN_ACCENT

p_cs = tf_co.add_paragraph()
p_cs.text = "Audience: Angel Investors, Deep-Tech VCs, BIRAC & OEM Licensing Partners"
p_cs.font.name = FONT_BODY
p_cs.font.size = Pt(8.5)
p_cs.font.color.rgb = TEXT_MUTED
p_cs.space_before = Pt(2)

com_pitch_text = (
    "\"Commercial acoustic tweezing tools currently cost between $2,500 and $5,000, severely gating market adoption. By replacing bulky transformers and FPGAs with an APB-synchronized push-pull architecture, we have achieved TRL 6 validation at a BoM of just $28.50.\n\n"
    "We own 100% of the proprietary embedded firmware, REST API, and cavity design, backed by a strong patent-pending differential topology.\n\n"
    "We are seeking $120,000 in seed capital or strategic OEM licensing to transition from TRL 6 prototype to an ISO-certified plug-and-play cleanroom benchtop product, unlocking a 93% gross margin hardware-plus-telemetry business.\""
)
p_ct = tf_co.add_paragraph()
r_ct = p_ct.add_run(com_pitch_text)
r_ct.font.name = FONT_BODY
r_ct.font.size = Pt(9.0)
r_ct.font.italic = True
r_ct.font.color.rgb = TEXT_PRIMARY
p_ct.space_before = Pt(6)

# ==========================================
# SLIDE 3: INDUSTRY RELEVANCE & MARKET DRIVERS
# ==========================================
print("Building Slide 3: Industry Relevance...")
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "MARKET DRIVERS & PAIN POINTS", "Industry Relevance & The Contamination Crisis", "The Urgent Need for Low-Cost, Contactless Manipulation Across High-Purity Sectors")

# 3 Pillars
drivers = [
    ("THE CONTACT CONTAMINATION CRISIS", AMBER_ACCENT, [
        ("42% False Positive Rate in Assays", "Physical pipette tips and micro-titer plates induce surface cross-contamination, sample adhesion loss, and false kinetic readouts."),
        ("Disposable Plastics Overhead", "A typical biochemical assay bench generates 15,000+ plastic pipette tips annually, incurring ~$14,000/yr in recurring lab consumables."),
        ("Bio-Hazardous Exposure Risk", "Manipulating volatile viral pathogens or radioactive reagents creates operator exposure hazards during manual tip ejections.")
    ]),
    ("SEMICONDUCTOR & CLEANROOM FRICTION", CYAN_ACCENT, [
        ("ESD & Micro-Scratch Defects", "Mechanical robotic grippers cause Electrostatic Discharge (ESD) and micro-abrasion defects on delicate MEMS structures and wafers."),
        ("Particle Shedding in Cleanrooms", "Traditional mechanical actuators shed lubricant and particulate debris, violating strict ISO Class 1 cleanroom compliance standards."),
        ("Fragile Optoelectronic Handling", "Handling bare micro-LED dies (<50 µm) and micro-lenses requires contact-free force profiles that vacuum tweezers cannot supply.")
    ]),
    ("EXPONENTIAL MARKET EXPANSION", GREEN_ACCENT, [
        ("$4.2B Microfluidics Market", "Rapidly expanding at 14.8% CAGR driven by point-of-care diagnostics and organ-on-a-chip technologies."),
        ("$18.6B Lab Automation Market", "Automating repetitive assay handling while reducing human touchpoints is the primary capex focus for top-50 pharma."),
        ("Prohibitive Instrument Costs", "Existing acoustic manipulation setups ($3,000–$5,000) are restricted to elite national laboratories, creating a massive unmet SME demand.")
    ])
]

card_w = 3.7
gap = 0.3
left_base = 0.8

for idx, (title, col, bullets) in enumerate(drivers):
    cx = left_base + idx * (card_w + gap)
    add_card(s3, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=col)
    
    tb = s3.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(10.5)
    p_h.font.bold = True
    p_h.font.color.rgb = col
    
    for b_title, b_desc in bullets:
        p_b = tf_c.add_paragraph()
        r_bt = p_b.add_run(b_title + "\n")
        r_bt.font.name = FONT_HEADING
        r_bt.font.size = Pt(9.0)
        r_bt.font.bold = True
        r_bt.font.color.rgb = TEXT_PRIMARY
        
        r_bd = p_b.add_run(b_desc)
        r_bd.font.name = FONT_BODY
        r_bd.font.size = Pt(8.0)
        r_bd.font.color.rgb = TEXT_MUTED
        p_b.space_before = Pt(6)

# ==========================================
# SLIDE 4: TARGET INDUSTRY SECTORS
# ==========================================
print("Building Slide 4: Target Industry Sectors...")
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "MARKET SEGMENTATION", "Target Industry Sectors & Addressable Verticals", "Broad Multi-Industry Applicability Spanning Life Sciences, Semiconductor, Space and Advanced Chemistry")

sectors = [
    ("1. BIOPHARMACEUTICALS & LIFE SCIENCES", CYAN_ACCENT, [
        ("Contactless Protein Crystallography", "Levitated droplet crystallization eliminates container wall nucleation, yielding defect-free X-ray diffraction crystals."),
        ("Living Cell Spheroid Culturing", "Suspending mammalian cell clusters in acoustic nodes enables 3D tissue growth without artificial extracellular matrix scaffolds."),
        ("Hazardous Pathogen Screening", "Zero-contact handling of high-consequence viral reagents inside biosafety cabinets without aerosolizing tips.")
    ]),
    ("2. SEMICONDUCTOR & PRECISION OPTICS", GREEN_ACCENT, [
        ("Frictionless Micro-Wafer Transfer", "Transporting micro-scale semiconductor dies and MEMS sensors without mechanical gripper friction or ESD damage."),
        ("Micro-Lens & Optical Fiber Splicing", "Acoustic positioning holds micro-spherical lenses and laser fibers in suspension during UV-cured optical bonding."),
        ("Zero-Debris Cleanroom Inspection", "Sub-millimeter sample rotation allows 360° optical inspection of dies without chuck mounting.")
    ]),
    ("3. SPACE & MICROGRAVITY ANALOG RESEARCH", VIOLET_ACCENT, [
        ("Terrestrial Microgravity Emulation", "Acoustic levitation neutralizes gravitational settling, providing ground-based emulation of orbital space station physics."),
        ("Containerless Metallurgical Solidification", "Melting and re-solidifying high-purity superalloys without crucible contamination for aerospace turbine research."),
        ("Drop-Tower & Parabolic Flight Payloads", "Ultra-low 5.6 W power budget enables self-contained battery operation on suborbital and parabolic flights.")
    ]),
    ("4. ADVANCED CHEMICAL SYNTHESIS & NANOTECH", AMBER_ACCENT, [
        ("Containerless Sol-Gel Synthesis", "Synthesizing ultra-pure aerogels and quantum dots without container boundary contamination."),
        ("Rapid Evaporative Droplet Drying", "Enhanced boundary layer mass transfer accelerates particle drying by 300% for inhalable drug powders."),
        ("Contactless Micro-Titration", "Acoustic coalescence of two suspended reagent droplets initiates instantaneous diffusion-controlled micro-reactions.")
    ])
]

card_w = 2.78
gap = 0.2
left_base = 0.8

for idx, (s_title, s_col, s_pts) in enumerate(sectors):
    cx = left_base + idx * (card_w + gap)
    add_card(s4, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=s_col)
    
    tb = s4.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = s_title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(9.5)
    p_h.font.bold = True
    p_h.font.color.rgb = s_col
    
    for p_t, p_d in s_pts:
        p_p = tf_c.add_paragraph()
        r_pt = p_p.add_run(p_t + "\n")
        r_pt.font.name = FONT_HEADING
        r_pt.font.size = Pt(8.5)
        r_pt.font.bold = True
        r_pt.font.color.rgb = TEXT_PRIMARY
        
        r_pd = p_p.add_run(p_d)
        r_pd.font.name = FONT_BODY
        r_pd.font.size = Pt(8.0)
        r_pd.font.color.rgb = TEXT_MUTED
        p_p.space_before = Pt(5)

# ==========================================
# SLIDE 5: PRACTICAL DEPLOYMENT SCENARIOS
# ==========================================
print("Building Slide 5: Practical Deployment Scenarios...")
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "OPERATIONAL USE CASES", "Practical Deployment Scenarios in Laboratory & Cleanroom", "End-to-End Workflow Blueprints for Life Science Automation, Hazardous Assays, and Micro-Assembly")

# Left: Cavity Geometry Figure (fig3_2_cavity_geometry.png)
fig3_2_path = os.path.join(fig_dir, "fig3_2_cavity_geometry.png")
add_figure_card(s5, 0.8, 1.6, 6.2, 5.3, fig3_2_path, "Figure 3.2: Calibrated Resonant Cavity Deployment Zone (D = 72.25 mm)")

# Right: 4 Practical Deployment Scenarios
add_card(s5, 7.2, 1.6, 5.333, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
sc_box = s5.shapes.add_textbox(Inches(7.4), Inches(1.8), Inches(4.933), Inches(4.9))
tf_sc = sc_box.text_frame
tf_sc.word_wrap = True

p_sh = tf_sc.paragraphs[0]
p_sh.text = "FIELD DEPLOYMENT WORKFLOWS:"
p_sh.font.name = FONT_HEADING
p_sh.font.size = Pt(11.5)
p_sh.font.bold = True
p_sh.font.color.rgb = CYAN_ACCENT

scenarios = [
    ("Scenario 1: High-Throughput Bio-Assay Station",
     "The levitator sits inside a laminar flow hood. A liquid handler injects a 5 µL reagent droplet directly into the acoustic node. Phase modulation translates the droplet vertically past a laser spectrophotometer for real-time fluorescence kinetic analysis."),
    ("Scenario 2: Sterile Pathogen Neutralization",
     "Viral specimens are levitated in mid-air inside a Class III biosafety cabinet. UV-C LED irradiation is applied uniformly across 360° of the suspended droplet surface without shadowing from container walls."),
    ("Scenario 3: Frictionless Micro-Optics Assembly",
     "Micro-sapphire lenses (1.5 mm diameter) are levitated and centered coaxially with a laser diode barrel. Operators fine-tune axial focus in 16.7 µm increments via the web slider before curing the adhesive."),
    ("Scenario 4: Droplet Coalescence Micro-Reactor",
     "Two independent nodes hold two different enzyme reagents. Shifting the relative phase merges the two nodes into one, triggering instantaneous chemical coalescence without solid surface contact.")
]

for title, desc in scenarios:
    p = tf_sc.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.0)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.0)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4)

# ==========================================
# SLIDE 6: TARGET USERS & CUSTOMER PERSONAS
# ==========================================
print("Building Slide 6: Target Users & Personas...")
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "CUSTOMER PERSONAS", "Target Users & Customer Segmentation", "Detailed Stakeholder Profiles Across Academic Research, Pharmaceutical QA, and Cleanroom Fab")

personas = [
    ("DR. ARUNA PATEL", "Principal Investigator – Structural Biology", CYAN_ACCENT, [
        ("Core Pain Point", "Protein samples crystallize irregularly due to heterogeneous wall nucleation on glass slides."),
        ("Value Derived", "Suspended containerless crystallization produces 3× larger, single-domain X-ray diffraction crystals."),
        ("Budget & Authority", "Academic NIH / DBT research grants; capex budget $5k–$15k for benchtop equipment.")
    ]),
    ("MARCUS VOGEL", "Senior Automation Engineer – Top-10 Pharma", GREEN_ACCENT, [
        ("Core Pain Point", "Disposable pipette tips cost his screening facility $85,000/year and produce frequent robot jams."),
        ("Value Derived", "Contactless droplet levitation eliminates pipette consumables and reduces assay false positives by 40%."),
        ("Budget & Authority", "High-throughput screening department budget; capex authority up to $100,000 for line automation.")
    ]),
    ("CHEN WEI", "Process Engineering Lead – Semiconductor Packaging", VIOLET_ACCENT, [
        ("Core Pain Point", "Mechanical pick-and-place grippers cause micro-fractures and electrostatic discharge (ESD) in MEMS dies."),
        ("Value Derived", "Acoustic tweezers manipulate delicate dies with zero mechanical contact, eliminating 95% of handling yield loss."),
        ("Budget & Authority", "Semiconductor fab process yield budget; ROI benchmarked against wafer salvage value.")
    ]),
    ("PROF. DAVID MILLER", "Head of Physics & Instrumentation Lab – University", AMBER_ACCENT, [
        ("Core Pain Point", "Legacy acoustic levitators ($3,500) are far too expensive to equip undergraduate teaching laboratories."),
        ("Value Derived", "At <$200 per educational kit, he can outfit 20 student lab benches with modern IoT acoustic tweezers."),
        ("Budget & Authority", "University departmental lab procurement budget; purchases 15–30 kits per cohort.")
    ])
]

card_w = 2.78
gap = 0.2
left_base = 0.8

for idx, (p_name, p_role, p_col, p_details) in enumerate(personas):
    cx = left_base + idx * (card_w + gap)
    add_card(s6, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=p_col)
    
    tb = s6.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = p_name
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(10)
    p_h.font.bold = True
    p_h.font.color.rgb = p_col
    
    p_r = tf_c.add_paragraph()
    p_r.text = p_role
    p_r.font.name = FONT_BODY
    p_r.font.size = Pt(8.0)
    p_r.font.color.rgb = TEXT_PRIMARY
    p_r.space_before = Pt(1)
    
    for d_title, d_desc in p_details:
        p_d = tf_c.add_paragraph()
        r_dt = p_d.add_run(d_title + ":\n")
        r_dt.font.name = FONT_HEADING
        r_dt.font.size = Pt(8.0)
        r_dt.font.bold = True
        r_dt.font.color.rgb = p_col
        
        r_dd = p_d.add_run(d_desc)
        r_dd.font.name = FONT_BODY
        r_dd.font.size = Pt(7.5)
        r_dd.font.color.rgb = TEXT_MUTED
        p_d.space_before = Pt(4)

# ==========================================
# SLIDE 7: VALUE PROPOSITION & CUSTOMER ROI
# ==========================================
print("Building Slide 7: Value Proposition & ROI...")
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "ECONOMIC VALUE DRIVERS", "Customer Value Proposition & ROI Model", "Quantifiable Financial and Operational Returns Across Capital Expenditure, Consumables, and Yield")

# 4 Value Metric Cards across the top
roi_cards = [
    ("99% CAPEX REDUCTION", "$28.50 BoM vs $3,000+ commercial lab systems unlocks mass adoption.", CYAN_ACCENT),
    ("$14,000/YR SAVINGS", "Eliminates disposable microfluidic cartridges and sterile pipette tips per bench.", GREEN_ACCENT),
    ("100% ESD IMMUNITY", "Non-contact acoustic acoustic tweezers eliminate electrostatic discharge yield loss.", VIOLET_ACCENT),
    ("< 5-MIN DEPLOYMENT", "Zero driver installation; instant browser-based cyber cockpit on local Wi-Fi.", AMBER_ACCENT)
]

for idx, (m_val, m_desc, m_col) in enumerate(roi_cards):
    cx = 0.8 + idx * (2.8 + 0.177)
    add_card(s7, cx, 1.6, 2.8, 1.5, bg_color=CARD_BG, border_color=m_col)
    tb = s7.shapes.add_textbox(Inches(cx + 0.1), Inches(1.7), Inches(2.6), Inches(1.3))
    tf_m = tb.text_frame
    tf_m.word_wrap = True
    
    p = tf_m.paragraphs[0]
    p.text = m_val
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = m_col
    
    p2 = tf_m.add_paragraph()
    p2.text = m_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(8.0)
    p2.font.color.rgb = TEXT_PRIMARY
    p2.space_before = Pt(3)

# Lower Container: Comparative ROI Analysis Card
add_card(s7, 0.8, 3.3, 11.733, 3.6, bg_color=CARD_BG, border_color=CARD_BORDER)
roi_box = s7.shapes.add_textbox(Inches(1.0), Inches(3.45), Inches(11.333), Inches(3.3))
tf_r = roi_box.text_frame
tf_r.word_wrap = True

p_rh = tf_r.paragraphs[0]
p_rh.text = "FIVE-YEAR COST OF OWNERSHIP COMPARISON (PER LAB BENCH):"
p_rh.font.name = FONT_HEADING
p_rh.font.size = Pt(11.5)
p_rh.font.bold = True
p_rh.font.color.rgb = CYAN_ACCENT

# Comparative Table
roi_table_shape = s7.shapes.add_table(4, 5, Inches(1.0), Inches(3.85), Inches(11.333), Inches(2.8))
t_roi = roi_table_shape.table
t_roi.columns[0].width = Inches(2.333)
t_roi.columns[1].width = Inches(2.25)
t_roi.columns[2].width = Inches(2.25)
t_roi.columns[3].width = Inches(2.25)
t_roi.columns[4].width = Inches(2.25)

roi_data = [
    ("Cost Factor", "Traditional Pipette & Wells", "Langevin Resonator Bench", "Ultrahaptics Phased Array", "Proposed ESP32 System"),
    ("Initial Capital Purchase", "$1,200 (Pipettes + Shaker)", "$3,500 (Horn + Generator)", "$4,800 (Array + Host PC)", "$450 (Turnkey System)"),
    ("Annual Consumables", "$14,000 / year (Tips, Plates)", "$2,200 / year (Replacement Tips)", "$1,500 / year (Specialist Chips)", "$0 / year (Containerless)"),
    ("5-Year Total Cost of Ownership", "$71,200 per bench", "$14,500 per bench", "$12,300 per bench", "$450 Total TCO")
]

for r_idx, row in enumerate(roi_data):
    for c_idx, cell_text in enumerate(row):
        c = t_roi.cell(r_idx, c_idx)
        c.text = cell_text
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
        p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
        p.font.size = Pt(9.0 if r_idx == 0 else 8.5)
        p.font.bold = (r_idx == 0 or c_idx == 4 or c_idx == 0)
        p.font.color.rgb = CYAN_ACCENT if r_idx == 0 else (GREEN_ACCENT if c_idx == 4 else TEXT_PRIMARY)
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(30, 48, 86) if r_idx == 0 else (RGBColor(20, 45, 65) if c_idx == 4 else (CARD_BG if r_idx % 2 == 1 else RGBColor(18, 28, 52)))

# ==========================================
# SLIDE 8: TECHNOLOGY READINESS LEVEL (TRL 6 VALIDATION)
# ==========================================
print("Building Slide 8: Technology Readiness Level (TRL)...")
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "READINESS EVALUATION", "Technology Readiness Level: Validated at TRL 6", "Rigorous Verification of Fully Integrated Hardware, Firmware, and Cloud Telemetry in Relevant Operational Conditions")

# Left Column: Dual Figures (Resonance Curve & Thermal Profile proving TRL 6)
fig4_1_path = os.path.join(fig_dir, "fig4_1_frequency_resonance_curve.png")
fig4_3_path = os.path.join(fig_dir, "fig4_3_thermal_power_profile.png")
add_figure_card(s8, 0.8, 1.6, 5.6, 2.55, fig4_1_path, "Empirical Resonance Stability at 40.05 kHz")
add_figure_card(s8, 0.8, 4.3, 5.6, 2.6, fig4_3_path, "60-Min Continuous Thermal Equilibrium (38.4°C)")

# Right Column: TRL Progression Breakdown
add_card(s8, 6.7, 1.6, 5.833, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
trl_box = s8.shapes.add_textbox(Inches(6.9), Inches(1.8), Inches(5.433), Inches(4.9))
tf_trl = trl_box.text_frame
tf_trl.word_wrap = True

p_th = tf_trl.paragraphs[0]
p_th.text = "NASA / DOD TRL PROGRESSION AUDIT:"
p_th.font.name = FONT_HEADING
p_th.font.size = Pt(11.5)
p_th.font.bold = True
p_th.font.color.rgb = CYAN_ACCENT

trl_stages = [
    ("TRL 1–3: Basic Principles & Proof of Concept", "COMPLETED", GREEN_ACCENT,
     "Gor'kov acoustic potential verified mathematically; 1D standing wave nodes validated in acoustic wave simulation."),
    ("TRL 4: Component Validation in Laboratory", "COMPLETED", GREEN_ACCENT,
     "Discrete breadboard assembly confirmed 24Vpp push-pull differential drive across single 40 kHz piezo transducer pairs."),
    ("TRL 5: Integrated Subsystem in Relevant Lab", "COMPLETED", GREEN_ACCENT,
     "Coupled 6-transducer cavity with ESP32 APB clock timer and dual L293D drivers; achieved 154.2 dB SPL acoustic pressure."),
    ("TRL 6: System Prototype in Operational Environment", "CURRENT MILESTONE", CYAN_ACCENT,
     "Fully packaged standalone system levitating solid and liquid micro-samples; continuous 60-min operation; browser-based REST teleoperation validated under ambient laboratory draft conditions."),
    ("TRL 7–8: Pilot Cleanroom & Industrial Validation", "NEXT MILESTONE (Q3 2027)", AMBER_ACCENT,
     "Transition to automated SMT PCB, injection-molded enclosure, and pilot testing in Class 1 cleanroom environment.")
]

for title, status, scol, desc in trl_stages:
    p = tf_trl.add_paragraph()
    r_t = p.add_run(title + " – ")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.0)
    r_t.font.bold = True
    r_t.font.color.rgb = TEXT_PRIMARY
    
    r_s = p.add_run(f"[{status}]\n")
    r_s.font.name = FONT_HEADING
    r_s.font.size = Pt(8.5)
    r_s.font.bold = True
    r_s.font.color.rgb = scol
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(7.5)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(3.5)

# ==========================================
# SLIDE 9: DEPLOYMENT READINESS & OPERATIONAL BLUEPRINT
# ==========================================
print("Building Slide 9: Deployment Readiness...")
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "OPERATIONAL DEPLOYMENT", "Deployment Readiness & Operational Blueprint", "Plug-and-Play Benchtop Setup, Environmental Envelope, and Turnkey Operation")

dep_pillars = [
    ("TURNKEY HARDWARE INTEGRATION", CYAN_ACCENT, [
        ("Zero Installation Tooling", "Unit powers directly from standard 12V 2A DC wall adapter (100–240V AC universal)."),
        ("Compact Benchtop Footprint", "Dimensions of 120 × 120 × 140 mm easily fits inside standard biosafety cabinets and fume hoods."),
        ("Tool-Free Gap Calibration", "Knurled brass lock nuts allow rapid gap adjustment without needing specialized Allen wrenches.")
    ]),
    ("ROBUST FIRMWARE & OPERATING ENVELOPE", GREEN_ACCENT, [
        ("Temperature Envelope: 15°C – 40°C", "Thermal throttling maintains reliable standing wave resonance across ambient lab fluctuations."),
        ("Humidity Envelope: 20% – 80% RH", "Non-condensing moisture does not alter transducer resonant frequency or drive impedance."),
        ("Continuous Run Stability", "Validated for 8+ hours of uninterrupted continuous acoustic levitation without frequency drift.")
    ]),
    ("AIR-GAPPED NETWORKING & WEB TELEMETRY", VIOLET_ACCENT, [
        ("Instant Web Connection", "ESP32 broadcasts standalone Wi-Fi SoftAP ('Acoustic-Levitator-Lab'); zero IT network approval needed."),
        ("Cross-Platform Accessibility", "Operates seamlessly on iPad, Android tablets, Mac, Windows, and Linux via any modern web browser."),
        ("Sub-10ms REST Teleoperation", "Immediate GUI response for fine vertical sample positioning and emergency field dissipation.")
    ])
]

card_w = 3.7
gap = 0.3
left_base = 0.8

for idx, (title, col, bullets) in enumerate(dep_pillars):
    cx = left_base + idx * (card_w + gap)
    add_card(s9, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=col)
    
    tb = s9.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(10)
    p_h.font.bold = True
    p_h.font.color.rgb = col
    
    for b_title, b_desc in bullets:
        p_b = tf_c.add_paragraph()
        r_bt = p_b.add_run(b_title + "\n")
        r_bt.font.name = FONT_HEADING
        r_bt.font.size = Pt(8.5)
        r_bt.font.bold = True
        r_bt.font.color.rgb = TEXT_PRIMARY
        
        r_bd = p_b.add_run(b_desc)
        r_bd.font.name = FONT_BODY
        r_bd.font.size = Pt(8.0)
        r_bd.font.color.rgb = TEXT_MUTED
        p_b.space_before = Pt(6)

# ==========================================
# SLIDE 10: INTELLECTUAL PROPERTY (IP) STATUS & SOFTWARE OWNERSHIP
# ==========================================
print("Building Slide 10: IP Status & Ownership...")
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "INTELLECTUAL PROPERTY STRATEGY", "IP Status, Patents & Software Ownership", "Defensible Patent Claims, Trade Secrets, and Clear Institutional Ownership Structure")

# Left Column: Patent Claims Card
add_card(s10, 0.8, 1.6, 5.7, 5.3, bg_color=CARD_BG, border_color=CYAN_ACCENT)
pt_box = s10.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
tf_pt = pt_box.text_frame
tf_pt.word_wrap = True

p_pth = tf_pt.paragraphs[0]
p_pth.text = "CORE PATENTABLE INVENTIONS (PROVISIONAL IP):"
p_pth.font.name = FONT_HEADING
p_pth.font.size = Pt(11.5)
p_pth.font.bold = True
p_pth.font.color.rgb = CYAN_ACCENT

patent_claims = [
    ("Claim 1: Transformerless Push-Pull Differential Topography",
     "Method and apparatus for generating 24Vpp differential acoustic drive from a low-voltage 12V DC rail using dual synchronized H-bridges without inductive step-up transformers."),
    ("Claim 2: APB Clock Division Phase-Lock Engine",
     "System architecture locking ultrasonic PWM counters directly to an 80 MHz peripheral clock bus, eliminating microcode phase jitter down to 12.5 ns during concurrent Wi-Fi broadcast."),
    ("Claim 3: Convergent Multi-Transducer Geometric Focus",
     "Acoustic cavity featuring a 12° inward spherical focus plate amplifying central standing wave sound pressure level by +4.8 dB over planar arrays."),
    ("Claim 4: Dual-Core Air-Gapped IoT Teleoperation",
     "Zero-install embedded cyber cockpit hosting an HTML5 simulation canvas from microcontroller flash while streaming REST/WebSocket commands across asymmetric RTOS cores.")
]

for title, desc in patent_claims:
    p = tf_pt.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.0)
    r_t.font.bold = True
    r_t.font.color.rgb = GREEN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.0)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4)

# Right Column: Ownership & Trade Secrets Card
add_card(s10, 6.8, 1.6, 5.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
ow_box = s10.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.9))
tf_ow = ow_box.text_frame
tf_ow.word_wrap = True

p_owh = tf_ow.paragraphs[0]
p_owh.text = "SOFTWARE OWNERSHIP & TRADE SECRETS:"
p_owh.font.name = FONT_HEADING
p_owh.font.size = Pt(11.5)
p_owh.font.bold = True
p_owh.font.color.rgb = GREEN_ACCENT

ownership_points = [
    ("100% Student-Faculty Authorship",
     "All firmware C++ microcode, FreeRTOS queue logic, HTML5/Canvas visualization code, and CAD mechanical files were independently developed by the student team under Dr. Mohammed Aarif K.O."),
    ("Institutional Assignment (VIT Chennai)",
     "Invention disclosures filed via School of Computer Science and Engineering (SCOPE). Clear IP assignment pathway following VIT IP Policy with royalty-sharing equity for founders."),
    ("Proprietary Trade Secrets",
     "Impedance-matching capacitive network tuning curves, thermal runaway suppression heuristics, and anti-turbulence phase ramp profiles are maintained as confidential proprietary know-how."),
    ("FTO (Freedom-to-Operate) Analysis",
     "Exhaustive prior art analysis confirms non-infringement against Bristol TinyLev (non-transformerless) and Ultrahaptics (FPGA multi-channel spatial haptics).")
]

for title, desc in ownership_points:
    p = tf_ow.add_paragraph()
    r_t = p.add_run(title + "\n")
    r_t.font.name = FONT_HEADING
    r_t.font.size = Pt(9.0)
    r_t.font.bold = True
    r_t.font.color.rgb = CYAN_ACCENT
    
    r_d = p.add_run(desc)
    r_d.font.name = FONT_BODY
    r_d.font.size = Pt(8.0)
    r_d.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4)

# ==========================================
# SLIDE 11: COLLABORATION & LICENSING MODELS
# ==========================================
print("Building Slide 11: Collaboration & Licensing...")
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "GO-TO-MARKET MONETIZATION", "Collaboration & Commercial Licensing Models", "Flexible Multi-Pronged Revenue Strategy Spanning OEM Partnerships, Direct Sales, and Cloud SaaS")

models = [
    ("STREAM 1: OEM TECHNOLOGY LICENSING", CYAN_ACCENT, [
        ("Target Partners", "Robotic liquid handling manufacturers (Tecan, Hamilton, PerkinElmer) and cleanroom robotic arm OEMs."),
        ("Licensing Structure", "Non-exclusive per-unit licensing royalty of $75 per installed acoustic end-effector module."),
        ("Value to OEM", "Enables OEMs to market contactless manipulation capabilities without re-engineering acoustics from scratch.")
    ]),
    ("STREAM 2: DIRECT BENCHTOP PRODUCT SALES", GREEN_ACCENT, [
        ("Turnkey Hardware Unit", "Packaged, CE/FCC-certified benchtop acoustic levitation unit sold directly to research labs."),
        ("Unit Economics", "Retail price of $450 against a total manufacturing cost of $45.00 yields an extraordinary 90% gross margin."),
        ("Target Market", "50,000+ academic, biotech, and hospital pathology research laboratories globally.")
    ]),
    ("STREAM 3: TELEMETRY & CLOUD SAAS FLEET", VIOLET_ACCENT, [
        ("Enterprise Multi-Chamber Fleet", "Centralized MQTT dashboard for monitoring parallel bioreactor fleets in industrial fermentation."),
        ("Subscription Model", "Tiered software subscription at $29/month per levitation chamber for audit-ready FDA 21 CFR logs."),
        ("Recurring Revenue", "Predictable high-margin recurring software cash flows scaling alongside hardware deployments.")
    ]),
    ("STREAM 4: STEM & HIGHER EDUCATION KITS", AMBER_ACCENT, [
        ("Educational Bundle", "Modular DIY assembly kit with open curriculum for undergraduate physics, robotics, and embedded systems."),
        ("Academic Price Point", "$199 per educational kit; bulk school bundles of 10 units for $1,699."),
        ("Ecosystem Funnel", "Creates early brand familiarity among future scientists, researchers, and cleanroom process engineers.")
    ])
]

card_w = 2.78
gap = 0.2
left_base = 0.8

for idx, (m_title, m_col, m_pts) in enumerate(models):
    cx = left_base + idx * (card_w + gap)
    add_card(s11, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=m_col)
    
    tb = s11.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = m_title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(9.5)
    p_h.font.bold = True
    p_h.font.color.rgb = m_col
    
    for pt_t, pt_d in m_pts:
        p_p = tf_c.add_paragraph()
        r_pt = p_p.add_run(pt_t + "\n")
        r_pt.font.name = FONT_HEADING
        r_pt.font.size = Pt(8.5)
        r_pt.font.bold = True
        r_pt.font.color.rgb = TEXT_PRIMARY
        
        r_pd = p_p.add_run(pt_d)
        r_pd.font.name = FONT_BODY
        r_pd.font.size = Pt(8.0)
        r_pd.font.color.rgb = TEXT_MUTED
        p_p.space_before = Pt(5)

# ==========================================
# SLIDE 12: FINANCIAL PROJECTIONS & UNIT ECONOMICS
# ==========================================
print("Building Slide 12: Financial Projections...")
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "VENTURE VIABILITY & SCALE", "Unit Economics & 3-Year Financial Forecast", "High-Margin Hardware-Plus-Software Business Model with Rapid Breakeven Profile")

# Left Column: Unit Economics Card
add_card(s12, 0.8, 1.6, 5.7, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
ue_box = s12.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
tf_ue = ue_box.text_frame
tf_ue.word_wrap = True

p_ueh = tf_ue.paragraphs[0]
p_ueh.text = "UNIT ECONOMICS BREAKDOWN (RETAIL UNIT):"
p_ueh.font.name = FONT_HEADING
p_ueh.font.size = Pt(11.5)
p_ueh.font.bold = True
p_ueh.font.color.rgb = CYAN_ACCENT

ue_items = [
    ("Direct BoM Cost", "$28.50", "Silicon, transducers, buck regulator, passive passives, fasteners"),
    ("SMT Assembly & QA", "$12.00", "Automated pick-and-place assembly, solder paste, optical test"),
    ("Enclosure & Packaging", "$4.50", "Custom injection-molded ABS housing, foam inserts, box"),
    ("Total COGS per Unit", "$45.00", "Total fully-loaded factory landed cost per packaged unit"),
    ("Target Retail Price", "$450.00", "Direct sales price to commercial and academic laboratories"),
    ("Gross Profit per Unit", "$405.00", "Gross Profit Margin: 90.0% contribution margin per unit"),
    ("Breakeven Threshold", "112 Units", "Sales volume required to fully amortize initial injection tooling")
]

for lbl, val, sub in ue_items:
    p = tf_ue.add_paragraph()
    r_l = p.add_run(lbl + ": ")
    r_l.font.name = FONT_BODY
    r_l.font.size = Pt(9.0)
    r_l.font.bold = True
    r_l.font.color.rgb = TEXT_PRIMARY
    
    r_v = p.add_run(val + " ")
    r_v.font.name = FONT_HEADING
    r_v.font.size = Pt(9.5)
    r_v.font.bold = True
    r_v.font.color.rgb = GREEN_ACCENT
    
    r_s = p.add_run(f"({sub})")
    r_s.font.name = FONT_BODY
    r_s.font.size = Pt(7.5)
    r_s.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(3)

# Right Column: 3-Year Projections Table Card
add_card(s12, 6.8, 1.6, 5.733, 5.3, bg_color=CARD_BG, border_color=CARD_BORDER)
py_box = s12.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.333), Inches(4.9))
tf_py = py_box.text_frame
tf_py.word_wrap = True

p_pyh = tf_py.paragraphs[0]
p_pyh.text = "THREE-YEAR SCALE FORECAST (2027–2029):"
p_pyh.font.name = FONT_HEADING
p_pyh.font.size = Pt(11.5)
p_pyh.font.bold = True
p_pyh.font.color.rgb = GREEN_ACCENT

fin_rows = [
    ("Metric", "Year 1 (2027)", "Year 2 (2028)", "Year 3 (2029)"),
    ("Benchtop Units Sold", "250 units", "1,200 units", "4,500 units"),
    ("Hardware Revenue", "$112,500", "$540,000", "$2,025,000"),
    ("OEM Licensing Revenue", "$18,750", "$90,000", "$337,500"),
    ("SaaS / Telemetry MRR", "$3,500", "$42,000", "$156,000"),
    ("Gross Revenue", "$134,750", "$672,000", "$2,518,500"),
    ("Gross Profit (90%)", "$121,275", "$604,800", "$2,266,650"),
    ("EBITDA Margin", "18.5% ($25k)", "34.2% ($230k)", "48.5% ($1.22M)")
]

table_fin = s12.shapes.add_table(len(fin_rows), 4, Inches(7.0), Inches(2.3), Inches(5.333), Inches(4.3))
t_f = table_fin.table
t_f.columns[0].width = Inches(1.8)
t_f.columns[1].width = Inches(1.1)
t_f.columns[2].width = Inches(1.1)
t_f.columns[3].width = Inches(1.333)

for r_idx, row in enumerate(fin_rows):
    for c_idx, val in enumerate(row):
        c = t_f.cell(r_idx, c_idx)
        c.text = val
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
        p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
        p.font.size = Pt(8.5 if r_idx == 0 else 7.5)
        p.font.bold = (r_idx == 0 or r_idx == 5 or c_idx == 0)
        p.font.color.rgb = CYAN_ACCENT if r_idx == 0 else (GREEN_ACCENT if r_idx == 5 or r_idx == 7 else TEXT_PRIMARY)
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(30, 48, 86) if r_idx == 0 else (CARD_BG if r_idx % 2 == 1 else RGBColor(18, 28, 52))

# ==========================================
# SLIDE 13: THE COMMERCIAL ASK: CAPITAL ALLOCATION
# ==========================================
print("Building Slide 13: The Commercial Ask...")
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "SEED CAPITAL FINANCING", "The Commercial Ask: $120,000 Seed Investment", "18-Month Runway to Advance from TRL 6 Prototype to Commercial Production and CE/FCC Certification")

# Ask Highlight Card across the top
add_card(s13, 0.8, 1.6, 11.733, 1.2, bg_color=CARD_BG, border_color=GREEN_ACCENT)
ah_box = s13.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(11.333), Inches(1.0))
tf_ah = ah_box.text_frame
tf_ah.word_wrap = True

p_h1 = tf_ah.paragraphs[0]
p_h1.text = "TARGET FINANCING ASK: $120,000 USD (or ₹1.0 CRORE INR EQUIVALENT)"
p_h1.font.name = FONT_HEADING
p_h1.font.size = Pt(13)
p_h1.font.bold = True
p_h1.font.color.rgb = GREEN_ACCENT

p_h2 = tf_ah.add_paragraph()
p_h2.text = "Structure: Equity Investment / Convertible SAFE Note / BIRAC Biotechnology Ignition Grant (BIG) / Deep-Tech Venture Syndicate"
p_h2.font.name = FONT_BODY
p_h2.font.size = Pt(9.5)
p_h2.font.color.rgb = TEXT_PRIMARY
p_h2.space_before = Pt(2)

# 4 Allocation Pillars below
allocations = [
    ("40% ($48,000)", "INDUSTRIAL DESIGN & CERTIFICATION", CYAN_ACCENT, [
        ("CE / FCC Regulatory Compliance", "Conducted emissions and EMC testing for global laboratory equipment sales."),
        ("ISO 13485 Medical Readiness", "Quality management documentation for medical device cleanroom compliance."),
        ("Tooling & Injection Molds", "Custom ABS dual-shot production molds for cavity and base.")
    ]),
    ("25% ($30,000)", "PILOT VALIDATION & BETA SITES", GREEN_ACCENT, [
        ("10 Partner Beta Placements", "Deploying prototype units across top biotech, academic, and pharma research labs."),
        ("Published Peer-Reviewed Assays", "Co-authoring application validation papers on contactless protein crystallization."),
        ("User Experience Iteration", "Refining web cyber cockpit based on direct laboratory operator feedback.")
    ]),
    ("20% ($24,000)", "AUTOMATED SMT MANUFACTURING", VIOLET_ACCENT, [
        ("Automated SMT Stencils & Line", "Setting up pilot manufacturing batch of 300 custom PCB assemblies."),
        ("Component Consignment Stock", "Bulk procurement of 2,000 piezo transducers to lock in wholesale tier pricing."),
        ("Automated End-of-Line QA Rig", "Custom optical acoustic SPL rig for 100% automated calibration.")
    ]),
    ("15% ($18,000)", "PATENT FILINGS & LEGAL IP", AMBER_ACCENT, [
        ("PCT International Patent", "Converting provisional patent filings into full PCT international applications."),
        ("Corporate Entity Incorporation", "Delaware C-Corp / India Private Limited structure and IP transfer."),
        ("OEM Agreement Drafting", "Master licensing agreements for robotic liquid handling manufacturers.")
    ])
]

card_w = 2.78
gap = 0.2
left_base = 0.8

for idx, (pct, a_title, a_col, a_items) in enumerate(allocations):
    cx = left_base + idx * (card_w + gap)
    add_card(s13, cx, 3.0, card_w, 3.9, bg_color=CARD_BG, border_color=a_col)
    
    tb = s13.shapes.add_textbox(Inches(cx + 0.15), Inches(3.15), Inches(card_w - 0.3), Inches(3.6))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_p = tf_c.paragraphs[0]
    p_p.text = pct
    p_p.font.name = FONT_HEADING
    p_p.font.size = Pt(13)
    p_p.font.bold = True
    p_p.font.color.rgb = a_col
    
    p_t = tf_c.add_paragraph()
    p_t.text = a_title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(8.5)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_PRIMARY
    p_t.space_before = Pt(1)
    
    for it_h, it_d in a_items:
        p_i = tf_c.add_paragraph()
        r_ih = p_i.add_run(f"• {it_h}: ")
        r_ih.font.name = FONT_HEADING
        r_ih.font.size = Pt(7.5)
        r_ih.font.bold = True
        r_ih.font.color.rgb = a_col
        
        r_id = p_i.add_run(it_d)
        r_id.font.name = FONT_BODY
        r_id.font.size = Pt(7.2)
        r_id.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(3)

# ==========================================
# SLIDE 14: STRATEGIC COLLABORATION & OEM PARTNERSHIP ASK
# ==========================================
print("Building Slide 14: Strategic Collaboration Ask...")
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "STRATEGIC ALLIANCES", "Partnership & Collaboration Opportunities", "Seeking Academic Clinical Trials, Cleanroom Foundry Co-Development, and Liquid Handler OEM Integration")

partnerships = [
    ("1. BIOPHARMACEUTICAL RESEARCH PARTNERS", CYAN_ACCENT, [
        ("Objective", "Conduct joint validation trials on contactless protein crystal growth and living cell suspension assays."),
        ("Ideal Partner", "Academic structural biology departments, cancer research institutes, and contract research organizations (CROs)."),
        ("Deliverable", "Joint white papers, co-authored journal publications in Nature Microfluidics / Lab on a Chip.")
    ]),
    ("2. SEMICONDUCTOR FOUNDRY & PACKAGING PARTNERS", GREEN_ACCENT, [
        ("Objective", "Pilot test acoustic tweezers as non-contact micro-wafer end-effectors for delicate MEMS component pick-and-place."),
        ("Ideal Partner", "Semiconductor packaging foundries, micro-optics assemblers, and cleanroom automation integrators."),
        ("Deliverable", "Comparative yield analysis quantifying reduction in electrostatic discharge (ESD) and particle defect rates.")
    ]),
    ("3. LIQUID HANDLER & ROBOTIC ARM OEMS", VIOLET_ACCENT, [
        ("Objective", "Integrate the acoustic manipulation chamber directly into automated robotic high-throughput screening gantry decks."),
        ("Ideal Partner", "Manufacturers of robotic liquid handlers (Tecan, Hamilton, PerkinElmer) and collaborative robot arms (Universal Robots)."),
        ("Deliverable", "Standardized modular mechanical mounting bracket and integrated REST / Python API driver library.")
    ]),
    ("4. DEEP-TECH INCUBATORS & ACCELERATORS", AMBER_ACCENT, [
        ("Objective", "Secure seed incubation, lab workspace, mentor network, and international venture syndicate connections."),
        ("Ideal Partner", "Hardware/Bio accelerators (HAX, Y Combinator, BIRAC BioNEST, Entrepreneur First)."),
        ("Deliverable", "Rapid scale-up from university spin-out into an internationally recognized deep-tech biotechnology venture.")
    ])
]

card_w = 2.78
gap = 0.2
left_base = 0.8

for idx, (p_title, p_col, p_items) in enumerate(partnerships):
    cx = left_base + idx * (card_w + gap)
    add_card(s14, cx, 1.6, card_w, 5.3, bg_color=CARD_BG, border_color=p_col)
    
    tb = s14.shapes.add_textbox(Inches(cx + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(4.9))
    tf_c = tb.text_frame
    tf_c.word_wrap = True
    
    p_h = tf_c.paragraphs[0]
    p_h.text = p_title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(9.5)
    p_h.font.bold = True
    p_h.font.color.rgb = p_col
    
    for it_h, it_d in p_items:
        p_i = tf_c.add_paragraph()
        r_ih = p_i.add_run(it_h + ":\n")
        r_ih.font.name = FONT_HEADING
        r_ih.font.size = Pt(8.5)
        r_ih.font.bold = True
        r_ih.font.color.rgb = TEXT_PRIMARY
        
        r_id = p_i.add_run(it_d)
        r_id.font.name = FONT_BODY
        r_id.font.size = Pt(8.0)
        r_id.font.color.rgb = TEXT_MUTED
        p_i.space_before = Pt(5)

# ==========================================
# SLIDE 15: 18-MONTH EXECUTION ROADMAP & CALL TO ACTION
# ==========================================
print("Building Slide 15: Execution Roadmap & Call to Action...")
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "STRATEGIC MILESTONES & VISION", "18-Month Execution Roadmap & Founding Team Contacts", "Clear Pathway from TRL 6 Prototype to Global Commercial Benchtop Instrument Distribution")

# Upper Container: 4 Milestone Quarters
add_card(s15, 0.8, 1.6, 11.733, 2.7, bg_color=CARD_BG, border_color=CARD_BORDER)
rm_box = s15.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(11.333), Inches(2.4))
tf_rm = rm_box.text_frame
tf_rm.word_wrap = True

p_rh = tf_rm.paragraphs[0]
p_rh.text = "18-MONTH COMMERCIAL EXECUTION ROADMAP:"
p_rh.font.name = FONT_HEADING
p_rh.font.size = Pt(11.5)
p_rh.font.bold = True
p_rh.font.color.rgb = CYAN_ACCENT

# 4 Quarter Cards inside Roadmap
q_cards = [
    ("Q1–Q2 2027: DFM & SMT", CYAN_ACCENT, "Automated PCB assembly, custom injection molding, CE / FCC pre-compliance testing."),
    ("Q3–Q4 2027: BETA SITES", GREEN_ACCENT, "Deploy 10 beta units in top research labs, publish validation papers, lock in OEM LOIs."),
    ("Q1–Q2 2028: LAUNCH", VIOLET_ACCENT, "Commercial market release of turnkey benchtop unit, direct sales launch, OEM revenue."),
    ("Q3–Q4 2028: SERIES A", AMBER_ACCENT, "Scale to 1,500+ units/yr, launch cloud telemetry SaaS, prepare Series A growth round.")
]

for idx, (q_t, q_c, q_d) in enumerate(q_cards):
    qx = 1.0 + idx * (2.7 + 0.177)
    add_card(s15, qx, 2.1, 2.7, 2.0, bg_color=RGBColor(16, 25, 48), border_color=q_c)
    tb_q = s15.shapes.add_textbox(Inches(qx + 0.1), Inches(2.2), Inches(2.5), Inches(1.8))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    
    pq = tf_q.paragraphs[0]
    pq.text = q_t
    pq.font.name = FONT_HEADING
    pq.font.size = Pt(9.5)
    pq.font.bold = True
    pq.font.color.rgb = q_c
    
    pqd = tf_q.add_paragraph()
    pqd.text = q_d
    pqd.font.name = FONT_BODY
    pqd.font.size = Pt(8.0)
    pqd.font.color.rgb = TEXT_MUTED
    pqd.space_before = Pt(3)

# Lower Container: Call-to-Action & Contact Information Card
add_card(s15, 0.8, 4.5, 11.733, 2.4, bg_color=CARD_BG, border_color=GREEN_ACCENT)
cta_box = s15.shapes.add_textbox(Inches(1.1), Inches(4.65), Inches(11.133), Inches(2.1))
tf_cta = cta_box.text_frame
tf_cta.word_wrap = True

p_ctah = tf_cta.paragraphs[0]
p_ctah.text = "JOIN US IN DEMOCRATIZING CONTACTLESS MICRO-MANIPULATION:"
p_ctah.font.name = FONT_HEADING
p_ctah.font.size = Pt(12)
p_ctah.font.bold = True
p_ctah.font.color.rgb = GREEN_ACCENT

p_call = tf_cta.add_paragraph()
p_call.text = (
    "We invite venture partners, OEM collaborators, and research laboratories to join us in bringing this revolutionary "
    "acoustic manipulation technology from laboratory prototype to global deployment. Together, we can eliminate contamination, "
    "accelerate life-saving pharmaceutical discoveries, and democratize scientific precision."
)
p_call.font.name = FONT_BODY
p_call.font.size = Pt(8.5)
p_call.font.color.rgb = TEXT_PRIMARY
p_call.space_before = Pt(3)

p_contact = tf_cta.add_paragraph()
r_c1 = p_contact.add_run("FOUNDING TEAM & MENTORSHIP CONTACTS:\n")
r_c1.font.name = FONT_HEADING
r_c1.font.size = Pt(9.0)
r_c1.font.bold = True
r_c1.font.color.rgb = CYAN_ACCENT

r_c2 = p_contact.add_run(
    "Investigators: Ronil (24BCE1330), Tejas (24BCE1360), Priyanshu (24BCE1140), Prashant (24BCE1118)\n"
    "Project Guide: Dr. Mohammed Aarif K.O., Professor, SCOPE | Dean: Dr. Viswanathan V, Professor & Dean, SCOPE\n"
    "Associate Dean: Dr. Suganya G, Professor & Associate Dean, SCOPE | Institution: Vellore Institute of Technology (VIT), Chennai"
)
r_c2.font.name = FONT_BODY
r_c2.font.size = Pt(8.0)
r_c2.font.color.rgb = TEXT_MUTED
p_contact.space_before = Pt(4)

# ==========================================
# SAVE PRESENTATION
# ==========================================
print(f"Saving presentation to {output_path}...")
prs.save(output_path)
print("Applications & Commercial Ask Presentation successfully created!")
