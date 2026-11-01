#!/usr/bin/env python3
"""
Acoustic Levitator Pro - Presentation Deck Generator
Generates a 15-slide, high-detail, 16:9 widescreen PowerPoint presentation covering:
1. Solution Overview
2. Application
3. Commercial Ask
"""

import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ==========================================
# PALETTE & DESIGN SYSTEM
# ==========================================
BG_COLOR       = RGBColor(11, 19, 43)     # #0B132B Deep Tech Navy
CARD_BG        = RGBColor(21, 32, 60)     # #15203C Slate Card Fill
CARD_BORDER    = RGBColor(42, 63, 107)    # #2A3F6B Subdued Slate Border
CYAN_ACCENT    = RGBColor(0, 240, 255)    # #00F0FF Neon Cyan
VIOLET_ACCENT  = RGBColor(168, 85, 247)   # #A855F7 Purple Accent
GREEN_ACCENT   = RGBColor(16, 185, 129)   # #10B981 Emerald Green
AMBER_ACCENT   = RGBColor(245, 158, 11)   # #F59E0B Warning Amber
TEXT_PRIMARY   = RGBColor(248, 250, 252)  # #F8FAFC Bright White
TEXT_MUTED     = RGBColor(148, 163, 184)  # #94A3B8 Muted Slate Gray
CARD_HIGHLIGHT = RGBColor(15, 23, 42)     # #0F172A Dark Obsidian

FONT_TITLE = "Helvetica Neue"
FONT_BODY  = "Arial"

def create_deck(output_path):
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
        # Category pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_TITLE
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN_ACCENT

        # Title & subtitle
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.75))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_TITLE
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_PRIMARY

        p_sub = tf_title.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, x, y, w, h, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Ambient center card
    add_card(s1, 1.2, 1.0, 10.933, 5.5, bg_color=CARD_BG, border_color=CYAN_ACCENT)

    # Badge
    badge_box = s1.shapes.add_textbox(Inches(1.8), Inches(1.4), Inches(9.7), Inches(0.4))
    tf_b = badge_box.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "EMBEDDED SYSTEMS & APPLIED ACOUSTIC LEVITATION"
    p_b.font.name = FONT_TITLE
    p_b.font.size = Pt(12)
    p_b.font.bold = True
    p_b.font.color.rgb = CYAN_ACCENT

    # Main Title
    title_box = s1.shapes.add_textbox(Inches(1.8), Inches(1.8), Inches(9.7), Inches(1.4))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "ACOUSTIC LEVITATOR PRO"
    p_t.font.name = FONT_TITLE
    p_t.font.size = Pt(40)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_PRIMARY

    p_t2 = tf_t.add_paragraph()
    p_t2.text = "Next-Generation Non-Contact Particle Trapping, Phase-Steering, & Automation Platform"
    p_t2.font.name = FONT_BODY
    p_t2.font.size = Pt(16)
    p_t2.font.color.rgb = VIOLET_ACCENT

    # Three Pillar Grid
    pillars = [
        ("01. SOLUTION OVERVIEW", "ESP32 80 MHz APB-locked silicon PWM engine, 2x L293D dual push-pull 24 Vpp drive, 6-transducer dual array with live Wi-Fi Mission Control."),
        ("02. SCIENTIFIC APPLICATIONS", "Containerless bio-pharmaceutical handling, living cell culturing, single-crystal drug synthesis, micro-reactors, and space microgravity simulation."),
        ("03. COMMERCIAL ASK", "Disrupting $30,000 lab instruments with a <$25 BOM design. Seed investment ask of $250k for industrialization, optical tracking, and commercial launch.")
    ]

    for idx, (p_head, p_desc) in enumerate(pillars):
        px = 1.8 + idx * 3.3
        add_card(s1, px, 3.5, 3.1, 2.2, bg_color=CARD_HIGHLIGHT, border_color=CARD_BORDER)
        box = s1.shapes.add_textbox(Inches(px + 0.15), Inches(3.6), Inches(2.8), Inches(2.0))
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = p_head
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = CYAN_ACCENT

        p2 = tf.add_paragraph()
        p2.text = p_desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # Footer author
    f_box = s1.shapes.add_textbox(Inches(1.8), Inches(5.9), Inches(9.7), Inches(0.4))
    f_tf = f_box.text_frame
    f_p = f_tf.paragraphs[0]
    f_p.text = "Author: Parth Agarwal  |  System Architecture: 6-Transducer Phased Array  |  Target: Commercial & Scientific Automation"
    f_p.font.name = FONT_BODY
    f_p.font.size = Pt(11)
    f_p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: EXECUTIVE SUMMARY & THE PARADIGM SHIFT
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Executive Briefing", "The Contactless Automation Paradigm Shift", "Solving micro-scale handling bottlenecks through acoustic radiation force.")

    cards_s2 = [
        ("THE PROBLEM: PHYSICAL CONTACT LIMITATIONS",
         [("Surface Adsorption:", "Expensive biological enzymes and micro-volume reagents are lost by adhering to pipette tips, test tubes, and microchannel walls."),
          ("Shear Stress Destruction:", "Mechanical micro-grippers and physical contact deform or lyse delicate mammalian cells and micro-organoids."),
          ("Container-Induced Nucleation:", "Wall impurities in physical vessels trigger uncontrolled polymorphic crystallization in novel pharmaceutical drug discovery."),
          ("Extreme Cost Barriers:", "Current commercial non-contact acoustic/optical tweezers cost between $15,000 and $45,000, severely limiting widespread deployment.")],
         RED_ACCENT := RGBColor(239, 68, 68)),

        ("OUR SOLUTION: SOLID-STATE ACOUSTIC TRAPPING",
         [("Pure Contactless Levitation:", "Suspends solids, liquids, and biological specimens in mid-air using 40 kHz acoustic standing wave pressure nodes."),
          ("Silicon-Level Phase Steering:", "Continuous vertical (Z-axis) translation and horizontal stability using zero-CPU ESP32 hardware LEDC PWM registers."),
          ("Push-Pull High Pressure:", "Dual L293D drivers deliver 24 Vpp differential swing across transducers, creating powerful 130 dB SPL acoustic traps."),
          ("Embedded Wi-Fi Mission Control:", "Zero-install web dashboard provides real-time telemetry, 60 FPS standing wave hologram, and automated frequency sweeps.")],
         CYAN_ACCENT),

        ("THE COMMERCIAL IMPACT: 90% COST DISRUPTION",
         [("Drastic BOM Reduction:", "Replaces high-end RF amplifiers and FPGAs with an optimized embedded BOM of <$25 (scale cost <$12)."),
          ("Massive Market Access:", "Democratizes non-contact manipulation for thousands of academic labs, biotech startups, and cleanroom facilities worldwide."),
          ("SaaS & Modular Expansion:", "High-margin revenue model combining core hardware units with specialized chamber modules and analytical tracking software."),
          ("The Investment Ask:", "Seeking $250,000 seed funding to achieve CE/FCC certification, integrate optical feedback, and manufacture the first 500 units.")],
         GREEN_ACCENT)
    ]

    for idx, (ctitle, items, c_accent) in enumerate(cards_s2):
        cx = 0.8 + idx * 4.0
        add_card(s2, cx, 1.6, 3.75, 5.3)
        tbox = s2.shapes.add_textbox(Inches(cx + 0.2), Inches(1.8), Inches(3.35), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = ctitle
        p_h.font.name = FONT_TITLE
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = c_accent

        for subhead, body in items:
            p_item = tf.add_paragraph()
            p_item.text = f"• {subhead} "
            p_item.font.name = FONT_TITLE
            p_item.font.size = Pt(10)
            p_item.font.bold = True
            p_item.font.color.rgb = TEXT_PRIMARY
            # Body text
            run = p_item.add_run()
            run.text = body
            run.font.name = FONT_BODY
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 3: SOLUTION OVERVIEW — PHYSICS & ACOUSTIC PRINCIPLES
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Solution Overview", "Acoustic Radiation Force & Standing Wave Physics", "How counter-propagating ultrasonic waves create stationary trapping potentials.")

    # Left Card: Physics Principles
    add_card(s3, 0.8, 1.6, 5.7, 5.3)
    tb_phys = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_p = tb_phys.text_frame
    tf_p.word_wrap = True
    p1 = tf_p.paragraphs[0]
    p1.text = "ACOUSTIC MECHANICS & GOR'KOV POTENTIAL"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = CYAN_ACCENT

    phys_points = [
        ("Standing Wave Interference:", "When two identical 40 kHz ultrasonic wavefronts travel toward each other from opposing arrays, their collision creates stationary alternating zones of high pressure (antinodes) and zero acoustic pressure (nodes)."),
        ("Gor'kov Acoustic Radiation Force:", "Small particles with positive acoustic contrast factor (denseness greater than air, such as water or polystyrene) experience a non-linear net force driving them into pressure nodes: F = -grad(U), where U is the Gor'kov acoustic potential."),
        ("Phase-Controlled Node Shifting:", "Introducing a relative phase delay (Delta Phi) between the top array and bottom array shifts the spatial position of the nodes along the vertical Z-axis: Delta Z = (Delta Phi / 360) * (lambda / 2). This allows smooth electronic vertical movement without any mechanical actuators."),
        ("Push-Pull Wave Reinforcement:", "By driving the transducer terminals with differential push-pull square waves (24 Vpp), acoustic radiation pressure scales quadratically (Force proportional to P^2), yielding four times greater trapping stability than single-ended drive.")
    ]
    for h_txt, b_txt in phys_points:
        p = tf_p.add_paragraph()
        p.text = f"• {h_txt} "
        p.font.name = FONT_TITLE
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = b_txt
        r.font.name = FONT_BODY
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # Right Card: Parameters & Cavity Geometry
    add_card(s3, 6.8, 1.6, 5.7, 5.3)
    tb_param = s3.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_pm = tb_param.text_frame
    tf_pm.word_wrap = True
    p2 = tf_pm.paragraphs[0]
    p2.text = "MATHEMATICAL PARAMETERS & CAVITY TUNING"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = VIOLET_ACCENT

    # Parameter boxes
    params = [
        ("Nominal Operating Frequency (f)", "40,000 Hz (Tunable across 38,000 – 42,000 Hz)"),
        ("Acoustic Velocity in Air (c)", "343.2 m/s (at standard 20°C atmospheric conditions)"),
        ("Acoustic Wavelength (lambda)", "lambda = c / f = 343.2 / 40,000 = 8.58 mm"),
        ("Inter-Node Spacing (Trap Interval)", "lambda / 2 = 4.29 mm (Stable trapping node every 4.29 mm)"),
        ("Calibrated Cavity Gap (D) — Mode A", "D = 8 * (lambda / 2) = 34.3 mm (Even multiple: Anti-Phase 180°)"),
        ("Calibrated Cavity Gap (D) — Mode B", "D = 6 * (lambda / 2) = 25.7 mm (Even multiple: In-Phase 0°)"),
        ("Sound Pressure Level (SPL)", "~125 – 132 dB SPL inside cavity focal region"),
        ("Maximum Particle Weight / Size", "Diameter <= 3.0 mm | Density <= 1.2 g/cm³ (Beads, droplets, seeds)")
    ]

    for p_name, p_val in params:
        p = tf_pm.add_paragraph()
        p.text = f"{p_name}: "
        p.font.name = FONT_TITLE
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        r = p.add_run()
        r.text = p_val
        r.font.name = FONT_BODY
        r.font.bold = False
        r.font.color.rgb = TEXT_PRIMARY

    # ==========================================
    # SLIDE 4: SOLUTION OVERVIEW — EMBEDDED HARDWARE ARCHITECTURE
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Solution Overview", "Embedded Hardware Architecture & Driver Topology", "Robust solid-state signal generation and push-pull amplification stage.")

    # 4 Architecture Columns
    hw_blocks = [
        ("ESP32 MICROCONTROLLER",
         "Silicon Wave Engine",
         [("Dual-Core Xtensa 240 MHz:", "Dedicated core separation for communications vs real-time control."),
          ("Hardware LEDC Peripheral:", "APB-clocked hardware PWM generates continuous 40 kHz with 0% CPU consumption."),
          ("LEDC_TIMER_0 (8-bit):", "256 discreet timer ticks per 40 kHz cycle for sub-degree phase resolution."),
          ("Non-Volatile Flash:", "Stores Wi-Fi credentials and calibration offsets in persistent memory.")],
         CYAN_ACCENT),

        ("DUAL L293D DRIVERS",
         "Push-Pull H-Bridge Stage",
         [("24 Vpp Differential Swing:", "Drives transducer pins with complementary Phase A & Phase B signals."),
          ("Dedicated Array Isolation:", "IC 1 drives Top Array (3 Tx); IC 2 drives Bottom Array (3 Tx)."),
          ("Thermal Safety:", "Center pins (4,5,12,13) tied to common ground heatsink plane."),
          ("Parallel Channel Loading:", "Transducers #1 & #2 on Bridge 1 (<75 mA), Transducer #3 on Bridge 2.")],
         VIOLET_ACCENT),

        ("POWER & PROTECTION",
         "Clean Supply Distribution",
         [("12V DC Primary Rail:", "Feeds motor driver VCC2 pins for maximum acoustic power output."),
          ("LM2596 Buck Converter:", "Steps 12V down to precision regulated 5.0V DC for logic & ESP32 VIN."),
          ("Common Ground Bus:", "Unified ground plane prevents floating potentials and ground-loop noise."),
          ("Dual-Capacitor Filter:", "470 uF electrolytic + 0.1 uF ceramic per IC to absorb ultrasonic switching spikes.")],
         GREEN_ACCENT),

        ("6-TRANSDUCER ARRAY",
         "Acoustic Cavity Geometry",
         [("40 kHz Piezo Sensors:", "High Q-factor piezoelectric ceramics with integrated aluminum horn casings."),
          ("3 Top (Down) + 3 Bottom (Up):", "Face-to-face opposed configuration forming an ultra-stable trapping pocket."),
          ("Transducer Polarity Rule:", "Outer casing pin = Ground/Phase B; Center pin = Phase A to prevent phase cancellation."),
          ("Adjustable Threaded Cage:", "M4 threaded rods allow micrometer-level cavity gap adjustment.")],
         AMBER_ACCENT)
    ]

    for idx, (b_title, b_sub, b_items, b_color) in enumerate(hw_blocks):
        bx = 0.8 + idx * 3.0
        add_card(s4, bx, 1.6, 2.85, 5.3)
        tbox = s4.shapes.add_textbox(Inches(bx + 0.15), Inches(1.8), Inches(2.55), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = b_title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = b_color

        p_s = tf.add_paragraph()
        p_s.text = b_sub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(9.5)
        p_s.font.color.rgb = TEXT_MUTED

        for h_txt, b_txt in b_items:
            p_i = tf.add_paragraph()
            p_i.text = f"• {h_txt} "
            p_i.font.name = FONT_TITLE
            p_i.font.size = Pt(9.5)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_PRIMARY
            r = p_i.add_run()
            r.text = b_txt
            r.font.name = FONT_BODY
            r.font.bold = False
            r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 5: SOLUTION OVERVIEW — FIRMWARE ENGINEERING & APB CLOCK LOCK
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Solution Overview", "Firmware Engineering & Silicon-Level Timing", "Direct hardware timer manipulation delivering zero-jitter acoustic waves.")

    cards_s5 = [
        ("DIRECT 80 MHz APB CLOCK LOCK",
         [("The Drift Problem:", "Standard microcontrollers rely on internal RC oscillators that drift by thousands of ppm under thermal load, collapsing the acoustic trap."),
          ("Silicon Crystal Locking:", "Our firmware explicitly binds LEDC_TIMER_0 to the 80 MHz APB crystal bus using LEDC_USE_APB_CLK, yielding frequency accuracy within <20 ppm."),
          ("Dynamic Frequency Scaling Immunity:", "Locks the ultrasonic PWM timer away from CPU frequency scaling so Wi-Fi transmission bursts never cause wave jitter.")]),

        ("HPOINT REGISTER ZERO-CPU PHASE DELAY",
         [("Shared Counter Reference:", "All 4 PWM channels (GPIO 4, 5, 18, 19) read from the same 8-bit hardware counter (0 to 255 ticks)."),
          ("Pure Hardware Phase Offsets:", "Shifting channel phase is accomplished by writing to the channel's hpoint register. The hardware timer changes the rising edge with zero CPU cycles."),
          ("Sub-Millimeter Motion:", "Each tick corresponds to 1.4° of acoustic phase (0.017 mm of vertical translation), enabling exceptionally smooth particle positioning.")]),

        ("FAIL-SAFE WI-FI & DUAL NETWORKING",
         [("Smart Hotspot Join:", "On boot, the ESP32 attempts connection to the primary research Wi-Fi / smartphone hotspot (6-second timeout)."),
          ("Zero-Reboot AP Fallback:", "If the network is unavailable, the firmware dynamically transitions to SoftAP mode (SSID: 'Acoustic-Levitator') without rebooting or dropping the ultrasound field."),
          ("Continuous Levitation:", "The standing wave remains 100% active and stable throughout network transitions and HTTP client connections.")])
    ]

    for idx, (ctitle, citems) in enumerate(cards_s5):
        cx = 0.8 + idx * 4.0
        add_card(s5, cx, 1.6, 3.75, 5.3)
        tbox = s5.shapes.add_textbox(Inches(cx + 0.2), Inches(1.8), Inches(3.35), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = ctitle
        p_h.font.name = FONT_TITLE
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = CYAN_ACCENT

        for h_txt, b_txt in citems:
            p = tf.add_paragraph()
            p.text = f"• {h_txt} "
            p.font.name = FONT_TITLE
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = TEXT_PRIMARY
            r = p.add_run()
            r.text = b_txt
            r.font.name = FONT_BODY
            r.font.bold = False
            r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 6: SOLUTION OVERVIEW — WEB MISSION CONTROL & REST API
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Solution Overview", "Web Mission Control & REST API Architecture", "Zero-install cross-platform cockpit accessible from any smartphone, tablet, or PC.")

    # Left: Web Dashboard Features
    add_card(s6, 0.8, 1.6, 5.7, 5.3)
    tb_web = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_w = tb_web.text_frame
    tf_w.word_wrap = True
    p1 = tf_w.paragraphs[0]
    p1.text = "INTEGRATED CYBER-DASHBOARD FEATURES"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = CYAN_ACCENT

    web_features = [
        ("Zero-Install Web Architecture:", "Hosted directly in ESP32 Flash memory via PROGMEM; open any browser to 192.168.4.1 without downloading software or apps."),
        ("60 FPS Standing Wave Hologram:", "HTML5 Canvas renders top and bottom transducer horns, animated sound wavefronts, and particle physics in real time."),
        ("Precision Motion D-Pad:", "Interactive controls for vertical translation (UP / DOWN / CENTER) with step sensitivity selection (Fine 0.2mm, Normal 0.8mm, Coarse 1.6mm)."),
        ("Automated Frequency Resonance Sweep:", "Automated scan from 38,500 Hz to 41,500 Hz in 200 Hz steps locks onto the exact mechanical resonance of the piezoelectric transducers."),
        ("Array Isolation Toggles:", "Allows muting either the top array or bottom array individually to verify emitter health and test reflection levitation mode.")
    ]
    for h_t, b_t in web_features:
        p = tf_w.add_paragraph()
        p.text = f"• {h_t} "
        p.font.name = FONT_TITLE
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = b_t
        r.font.name = FONT_BODY
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # Right: REST API Specification
    add_card(s6, 6.8, 1.6, 5.7, 5.3)
    tb_api = s6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_a = tb_api.text_frame
    tf_a.word_wrap = True
    p2 = tf_a.paragraphs[0]
    p2.text = "RESTFUL API & EXTERNAL AUTOMATION ENGINE"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = VIOLET_ACCENT

    api_endpoints = [
        ("GET /api/status", "Returns JSON telemetry: carrier frequency, relative phase angle, phase tick, array mute states, and network IP."),
        ("GET /api/move?dir=[up|down|center]", "Executes step-wise vertical particle translation or centers trap at 0° reference."),
        ("GET /api/phase?toggle=1 | ?tick=[0..255]", "Instantly flips phase between In-Phase (0°) and Anti-Phase (180°) or sets arbitrary hpoint tick."),
        ("GET /api/freq?val=[Hz] | ?delta=[+-Hz]", "Fine-tunes ultrasonic drive frequency in 50 Hz or 100 Hz increments for peak acoustic trapping force."),
        ("GET /api/toggle?target=[top|bot]", "Individually mutes or un-mutes top or bottom transducer banks."),
        ("GET /api/sweep", "Triggers automated 38.5 – 41.5 kHz resonance discovery sweep."),
        ("CORS-Enabled Integration:", "Access-Control-Allow-Origin: * headers allow LabVIEW, Python scripts, MATLAB, and ROS to command the levitator over Wi-Fi.")
    ]
    for h_a, b_a in api_endpoints:
        p = tf_a.add_paragraph()
        p.text = f"{h_a}: "
        p.font.name = FONT_TITLE
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        r = p.add_run()
        r.text = b_a
        r.font.name = FONT_BODY
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: APPLICATIONS — PHARMACEUTICALS & BIOTECHNOLOGY
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Industrial Applications", "Biotechnology & Pharmaceutical Automation", "Overcoming contamination, shear stress, and container losses in life sciences.")

    apps_bio = [
        ("ZERO-LOSS DROPLET HANDLING",
         "Ultra-Rare Reagents & Enzymes",
         [("The Challenge:", "In genomic sequencing and high-potency API synthesis, reagents cost up to $10,000/mL. Up to 15% is lost due to surface wetting on pipette tips and vial walls."),
          ("Acoustic Trapping Solution:", "Suspends single micro-droplets (0.5 to 10 uL) in mid-air with zero solid contact, achieving 100% reagent utilization."),
          ("Micro-Mixing:", "Modulating ultrasonic amplitude induces acoustic streaming inside the droplet, enabling rapid mixing without stirrers.")],
         CYAN_ACCENT),

        ("LIVING CELL & ORGANOID CULTURE",
         "Low Shear-Stress Manipulation",
         [("The Challenge:", "Traditional microfluidics subject mammalian stem cells and delicate organoids to high shear stress, causing cell lysis and premature differentiation."),
          ("Acoustic Trapping Solution:", "Ultrasonic radiation pressure creates gentle, uniform holding forces that preserve cell membrane integrity over hours of observation."),
          ("Scaffold-Free Spheroid Growth:", "Acoustically clusters cells in suspension to promote natural 3D cellular self-assembly without synthetic scaffolding matrices.")],
         VIOLET_ACCENT),

        ("CONTAINERLESS CRYSTALLOGRAPHY",
         "Polymorph Control & Protein Crystals",
         [("The Challenge:", "Vessel walls act as nucleation sites, precipitating undesirable crystal polymorphs or disordered amorphous aggregates."),
          ("Acoustic Trapping Solution:", "Levitated droplet evaporation yields ultra-high purity, defect-free single crystals for X-ray diffraction and targeted drug design."),
          ("Supersaturation Studies:", "Allows solutions to reach extreme supersaturation levels impossible inside physical containers.")],
         GREEN_ACCENT)
    ]

    for idx, (atitle, asub, aitems, acolor) in enumerate(apps_bio):
        ax = 0.8 + idx * 4.0
        add_card(s7, ax, 1.6, 3.75, 5.3)
        tbox = s7.shapes.add_textbox(Inches(ax + 0.2), Inches(1.8), Inches(3.35), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = atitle
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = acolor

        p_s = tf.add_paragraph()
        p_s.text = asub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(10)
        p_s.font.color.rgb = TEXT_MUTED

        for h_t, b_t in aitems:
            p_i = tf.add_paragraph()
            p_i.text = f"• {h_t} "
            p_i.font.name = FONT_TITLE
            p_i.font.size = Pt(10)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_PRIMARY
            r = p_i.add_run()
            r.text = b_t
            r.font.name = FONT_BODY
            r.font.bold = False
            r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 8: APPLICATIONS — CHEMICAL SYNTHESIS & SPECTROSCOPY
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Industrial Applications", "Containerless Chemistry & In-Situ Spectroscopy", "Eliminating background noise and crucible reactions in high-precision chemistry.")

    apps_chem = [
        ("CONTAINERLESS MICRO-REACTORS",
         "Hazardous & Corrosive Synthesis",
         [("The Challenge:", "Highly reactive reagents (strong acids, reactive organometallics) corrode microchannels, leaching metal ions into reaction mixtures."),
          ("Acoustic Solution:", "Droplets of incompatible chemicals are levitated and coalesced in mid-air by phase manipulation, creating an inert, crucible-free micro-reactor."),
          ("Zero Cross-Contamination:", "No vessel cleaning or consumable plasticware required between experiments.")],
         CYAN_ACCENT),

        ("WINDOWLESS RAMAN & FTIR SPECTROSCOPY",
         "Zero Background Interrogation",
         [("The Challenge:", "Optical spectroscopy (Raman, UV-Vis, FTIR) suffers from optical scattering and fluorescence background noise from glass/quartz cuvettes."),
          ("Acoustic Solution:", "Excitation lasers interrogate the levitated droplet directly in open air with 360° optical access and 0% cuvette background signal."),
          ("Real-Time Reaction Kinetics:", "Monitors phase transitions, polymerization, and evaporation dynamics in-situ without sensor interference.")],
         VIOLET_ACCENT),

        ("HIGH-PURITY MATERIAL SPHEROIDIZATION",
         "Aerogels, Polymers, & Nanomaterials",
         [("The Challenge:", "Drying viscous liquid droplets on solid substrates forms distorted 'pancakes' due to gravity and surface tension wetting."),
          ("Acoustic Solution:", "Acoustic levitation maintains perfectly spherical droplet geometry throughout sol-gel transition and drying phases."),
          ("Applications:", "Fabrication of perfectly spherical micro-lenses, micro-capsules for controlled drug release, and ultra-lightweight porous aerogels.")],
         GREEN_ACCENT)
    ]

    for idx, (atitle, asub, aitems, acolor) in enumerate(apps_chem):
        ax = 0.8 + idx * 4.0
        add_card(s8, ax, 1.6, 3.75, 5.3)
        tbox = s8.shapes.add_textbox(Inches(ax + 0.2), Inches(1.8), Inches(3.35), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = atitle
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = acolor

        p_s = tf.add_paragraph()
        p_s.text = asub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(10)
        p_s.font.color.rgb = TEXT_MUTED

        for h_t, b_t in aitems:
            p_i = tf.add_paragraph()
            p_i.text = f"• {h_t} "
            p_i.font.name = FONT_TITLE
            p_i.font.size = Pt(10)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_PRIMARY
            r = p_i.add_run()
            r.text = b_t
            r.font.name = FONT_BODY
            r.font.bold = False
            r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 9: APPLICATIONS — ADVANCED MANUFACTURING & AEROSPACE
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Industrial Applications", "Semiconductors, Cleanrooms, & Space Microgravity", "Precision non-contact assembly and ground-based microgravity simulation.")

    apps_mfg = [
        ("SEMICONDUCTOR & MICRO-DIE HANDLING",
         "Scratch-Free Cleanroom Positioning",
         [("Micro-LED & Die Transfer:", "Picks and translates delicate sub-millimeter semiconductor dies without physical vacuum chucks that cause micro-cracking."),
          ("Optical Component Positioning:", "Aligns micro-lenses, fiber-optic stubs, and miniature optical filters with zero mechanical abrasion."),
          ("Static Dissipation:", "Eliminates electrostatic discharge (ESD) risks associated with physical pick-and-place metal tweezers.")],
         CYAN_ACCENT),

        ("CLEANROOM CONTAMINATION METROLOGY",
         "Particulate Analysis & Defect Trapping",
         [("Suspended Debris Inspection:", "Traps unknown airborne contaminants or cleanroom particulates in mid-air for high-magnification optical and SEM examination."),
          ("Non-Destructive Assay:", "Prevents particles from becoming embedded in sticky carbon tape or adhesive sampling stubs."),
          ("Standards Testing:", "Serves as a calibration benchmark for airborne particle counters and laminar flow hood verification.")],
         VIOLET_ACCENT),

        ("SPACE MICROGRAVITY SIMULATION",
         "Fluid Mechanics & Drop Towers",
         [("Ground-Based Microgravity:", "Counteracts gravity with upward acoustic radiation pressure, simulating true weightlessness for fluid mechanics research."),
          ("Combustion Dynamics:", "Enables crucible-free spherical fuel droplet combustion studies without buoyancy-driven convection plumes."),
          ("University & Space Agency Training:", "Affordable ground alternative to parabolic flights and drop-tower facilities for fluid physics experiments.")],
         GREEN_ACCENT)
    ]

    for idx, (atitle, asub, aitems, acolor) in enumerate(apps_mfg):
        ax = 0.8 + idx * 4.0
        add_card(s9, ax, 1.6, 3.75, 5.3)
        tbox = s9.shapes.add_textbox(Inches(ax + 0.2), Inches(1.8), Inches(3.35), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = atitle
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = acolor

        p_s = tf.add_paragraph()
        p_s.text = asub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(10)
        p_s.font.color.rgb = TEXT_MUTED

        for h_t, b_t in aitems:
            p_i = tf.add_paragraph()
            p_i.text = f"• {h_t} "
            p_i.font.name = FONT_TITLE
            p_i.font.size = Pt(10)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_PRIMARY
            r = p_i.add_run()
            r.text = b_t
            r.font.name = FONT_BODY
            r.font.bold = False
            r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 10: COMMERCIAL ASK — MARKET OPPORTUNITY & TARGET SEGMENTS
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Commercial Ask", "Market Opportunity & Addressable Segments", "A high-growth multi-billion-dollar market waiting for an accessible hardware platform.")

    # 3 Stat Cards on Top
    tam_metrics = [
        ("$8.2 BILLION", "TOTAL ADDRESSABLE MARKET (TAM)", "Global laboratory automation, non-contact liquid handling, and micro-positioning market by 2029 (CAGR 8.4%).", CYAN_ACCENT),
        ("$1.4 BILLION", "SERVICEABLE ADDRESSABLE MARKET (SAM)", "Acoustic tweezers, microfluidics, spectroscopy sample positioning, and containerless synthesis systems.", VIOLET_ACCENT),
        ("$180 MILLION", "SERVICEABLE OBTAINABLE MARKET (SOM)", "Direct beachhead: 15,000+ university chemistry/physics research labs, biotech incubators, and analytical spectroscopy centers.", GREEN_ACCENT)
    ]
    for idx, (m_val, m_title, m_desc, m_col) in enumerate(tam_metrics):
        mx = 0.8 + idx * 4.0
        add_card(s10, mx, 1.6, 3.75, 1.8)
        box = s10.shapes.add_textbox(Inches(mx + 0.15), Inches(1.7), Inches(3.45), Inches(1.6))
        tf = box.text_frame
        tf.word_wrap = True
        p_v = tf.paragraphs[0]
        p_v.text = m_val
        p_v.font.name = FONT_TITLE
        p_v.font.size = Pt(24)
        p_v.font.bold = True
        p_v.font.color.rgb = m_col

        p_t = tf.add_paragraph()
        p_t.text = m_title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_PRIMARY

        p_d = tf.add_paragraph()
        p_d.text = m_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = TEXT_MUTED

    # Bottom Split Card: Customer Personas & Market Catalysts
    add_card(s10, 0.8, 3.6, 5.7, 3.3)
    tb_cp = s10.shapes.add_textbox(Inches(1.0), Inches(3.75), Inches(5.3), Inches(3.0))
    tf_cp = tb_cp.text_frame
    tf_cp.word_wrap = True
    p1 = tf_cp.paragraphs[0]
    p1.text = "PRIMARY TARGET CUSTOMER PERSONAS"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = CYAN_ACCENT

    personas = [
        ("Academic Research PIs:", "Chemistry, Physics, Materials Science, and Bio-Engineering departments requiring reliable contactless manipulation without $30k budget clearances."),
        ("Biotech & Pharma R&D:", "Early-stage drug discovery teams screening ultra-rare enzymes and developing single-crystal polymorphic formulations."),
        ("Spectroscopy Core Facilities:", "Raman and FTIR analytical laboratories seeking containerless sample stages with 360° laser interrogation ports."),
        ("STEM Higher Education:", "University lab courses teaching wave physics, mechatronics, and non-linear acoustics with modern interactive web cockpits.")
    ]
    for hp, bp in personas:
        p = tf_cp.add_paragraph()
        p.text = f"• {hp} "
        p.font.name = FONT_TITLE
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = bp
        r.font.name = FONT_BODY
        r.font.color.rgb = TEXT_MUTED

    add_card(s10, 6.8, 3.6, 5.7, 3.3)
    tb_mc = s10.shapes.add_textbox(Inches(7.0), Inches(3.75), Inches(5.3), Inches(3.0))
    tf_mc = tb_mc.text_frame
    tf_mc.word_wrap = True
    p2 = tf_mc.paragraphs[0]
    p2.text = "POWERFUL MARKET CATALYSTS & TAILWINDS"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = VIOLET_ACCENT

    catalysts = [
        ("Shift to Micro-Volume Assays:", "Rising reagent costs create urgent demand for zero-waste droplet handling technology."),
        ("Organoid & 3D Bio-Printing Boom:", "Surging clinical demand for scaffold-free cell culturing to test personalized therapeutics."),
        ("Laboratory Automation 2.0:", "Transition from bulky robotic gantry arms to agile acoustic and microfluidic manipulation modules."),
        ("Decentralized Research Tooling:", "Lower-cost hardware platforms enable academic labs in emerging markets to perform tier-1 research.")
    ]
    for hc, bc in catalysts:
        p = tf_mc.add_paragraph()
        p.text = f"• {hc} "
        p.font.name = FONT_TITLE
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = bc
        r.font.name = FONT_BODY
        r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 11: COMMERCIAL ASK — COST DISRUPTION & UNIT ECONOMICS
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Commercial Ask", "Radical Cost Disruption & Unit Economics", "Replacing complex RF equipment with modern silicon to unlock 85%+ gross margins.")

    # Left: Comparison
    add_card(s11, 0.8, 1.6, 5.7, 5.3)
    tb_comp = s11.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_c = tb_comp.text_frame
    tf_c.word_wrap = True
    p1 = tf_c.paragraphs[0]
    p1.text = "TRADITIONAL ACOUSTIC SYSTEMS VS OUR PLATFORM"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = RED_ACCENT

    comp_items = [
        ("Traditional Commercial Levitator ($15,000 – $45,000):",
         "Uses custom-machined Langevin transducers, heavy linear RF power amplifiers, and FPGA signal processing racks. High power consumption (>150W), bulky footprint (benchtop rack), complex calibration, and closed proprietary software."),
        ("Our Acoustic Levitator Pro ($799 – $2,499):",
         "Leverages commercial-off-the-shelf (COTS) 40 kHz piezoceramics, low-cost dual H-bridge push-pull drivers, and silicon-locked ESP32 timers. Low power (<15W), portable palm-sized footprint, self-calibrating auto-sweep, and open REST API connectivity."),
        ("The 95% Cost Advantage:",
         "By executing the high-speed wave synthesis inside ESP32 silicon rather than dedicated FPGAs, we reduce electronic hardware costs by over 90% without sacrificing acoustic trapping stability.")
    ]
    for hc, bc in comp_items:
        p = tf_c.add_paragraph()
        p.text = f"• {hc}\n  "
        p.font.name = FONT_TITLE
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = bc
        r.font.name = FONT_BODY
        r.font.color.rgb = TEXT_MUTED

    # Right: Unit Economics Table
    add_card(s11, 6.8, 1.6, 5.7, 5.3)
    tb_econ = s11.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_e = tb_econ.text_frame
    tf_e.word_wrap = True
    p2 = tf_e.paragraphs[0]
    p2.text = "BILL OF MATERIALS & TIERED PRICING"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = GREEN_ACCENT

    econ_points = [
        ("Current Prototype BOM Cost:", "$22.40 (₹1,850) per unit at 10-unit lab assembly scale."),
        ("Scaled Production BOM (1k units):", "< $11.80 per unit (Custom 4-layer PCB + molded acoustic horn baffle)."),
        ("Academic Research Edition ($799 MSRP):", "Includes 6-Tx levitator, acrylic draft enclosure, 12V supply, and embedded web software. Gross Margin: 92% ($735 per unit)."),
        ("Enterprise / Cleanroom Edition ($2,499 MSRP):", "Includes optical tracking micro-camera, laser alignment stage, Raman spectroscopy port, and Levitator Studio Pro SDK. Gross Margin: 86% ($2,150 per unit)."),
        ("Consumables & Accessories ($49 – $199):", "Calibrated micropipette tips, acoustic alignment grids, micro-bead calibration kits, and modular environmental chambers.")
    ]
    for he, be in econ_points:
        p = tf_e.add_paragraph()
        p.text = f"{he} "
        p.font.name = FONT_TITLE
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        r = p.add_run()
        r.text = be
        r.font.name = FONT_BODY
        r.font.color.rgb = TEXT_PRIMARY

    # ==========================================
    # SLIDE 12: COMMERCIAL ASK — BUSINESS MODEL & GO-TO-MARKET
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Commercial Ask", "Business Model & Go-To-Market Strategy", "A multi-stream flywheel combining hardware margins, modular add-ons, and software licensing.")

    bm_cards = [
        ("HARDWARE PLATFORM REVENUE",
         "High-Margin Base Hardware",
         [("Academic Edition ($799):", "High-volume direct sales to university STEM and research labs worldwide."),
          ("Industrial/Enterprise Edition ($2,499):", "Turnkey automated systems for pharmaceutical and materials R&D facilities."),
          ("Modular Chamber Add-ons ($350 – $800):", "Inert-gas purging chambers, heated/cooled acoustic stages, and optical laser pass-through ports."),
          ("OEM Array Modules:", "White-label integration into larger automated liquid handling workstations.")],
         CYAN_ACCENT),

        ("LEVITATOR STUDIO PRO (SAAS)",
         "Recurring Software Licensing",
         [("Computer Vision Tracking ($49/mo):", "AI edge camera module auto-tracks particle coordinates and logs trajectory data."),
          ("Automated Scripting Engine:", "Python & LabVIEW SDK allowing researchers to program complex multi-step droplet mixing protocols."),
          ("Cloud Telemetry & Audit Logs:", "21 CFR Part 11 compliant digital logging for pharmaceutical quality assurance and repeatability."),
          ("Freemium Community Tier:", "Open-source core web dashboard drives viral academic adoption and community advocacy.")],
         VIOLET_ACCENT),

        ("3-TIER DISTRIBUTION STRATEGY",
         "Targeted Channel Execution",
         [("Direct Academic B2B:", "Targeting 2,500+ material science, chemistry, and bio-engineering departments through direct academic outreach."),
          ("Lab Equipment Distributor Partnerships:", "Partnering with regional scientific equipment suppliers (Fisher Scientific, VWR, Cole-Parmer)."),
          ("Conference Showcases & Competitions:", "Live levitation demonstrations at Pittcon, SLAS (Lab Automation), and IEEE IUS conferences."),
          ("Digital Community & Open Publications:", "Publishing peer-reviewed validation papers and open protocols on bioRxiv and ChemRxiv.")],
         GREEN_ACCENT)
    ]

    for idx, (btitle, bsub, bitems, bcolor) in enumerate(bm_cards):
        bx = 0.8 + idx * 4.0
        add_card(s12, bx, 1.6, 3.75, 5.3)
        tbox = s12.shapes.add_textbox(Inches(bx + 0.2), Inches(1.8), Inches(3.35), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = btitle
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = bcolor

        p_s = tf.add_paragraph()
        p_s.text = bsub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(10)
        p_s.font.color.rgb = TEXT_MUTED

        for h_t, b_t in bitems:
            p_i = tf.add_paragraph()
            p_i.text = f"• {h_t} "
            p_i.font.name = FONT_TITLE
            p_i.font.size = Pt(10)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_PRIMARY
            r = p_i.add_run()
            r.text = b_t
            r.font.name = FONT_BODY
            r.font.bold = False
            r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 13: COMMERCIAL ASK — THE INVESTMENT & CAPITAL ALLOCATION
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Commercial Ask", "Seed Investment Ask & Capital Allocation", "Seeking $250,000 seed / grant funding to transition from prototype to commercial production.")

    # Left: The Ask Card
    add_card(s13, 0.8, 1.6, 4.2, 5.3)
    tb_ask = s13.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(3.8), Inches(4.9))
    tf_ak = tb_ask.text_frame
    tf_ak.word_wrap = True
    p1 = tf_ak.paragraphs[0]
    p1.text = "THE INVESTMENT ASK"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = CYAN_ACCENT

    p_amt = tf_ak.add_paragraph()
    p_amt.text = "$250,000"
    p_amt.font.name = FONT_TITLE
    p_amt.font.size = Pt(36)
    p_amt.font.bold = True
    p_amt.font.color.rgb = GREEN_ACCENT

    p_stage = tf_ak.add_paragraph()
    p_stage.text = "Seed Round / DeepTech Commercialization Grant\n"
    p_stage.font.name = FONT_BODY
    p_stage.font.size = Pt(11)
    p_stage.font.color.rgb = TEXT_MUTED

    ask_bullets = [
        ("Target Runway:", "18 months to cash-flow positive."),
        ("Key Valuation Driver:", "De-risked core technology with working prototype and validated 6-Tx firmware."),
        ("Strategic Objective:", "Produce certified pilot batch of 500 commercial units, secure 25 academic lab deployments, and launch Levitator Studio Pro SaaS platform.")
    ]
    for ha, ba in ask_bullets:
        p = tf_ak.add_paragraph()
        p.text = f"• {ha} "
        p.font.name = FONT_TITLE
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = ba
        r.font.name = FONT_BODY
        r.font.color.rgb = TEXT_MUTED

    # Right: Capital Allocation Breakdown
    add_card(s13, 5.3, 1.6, 7.2, 5.3)
    tb_alloc = s13.shapes.add_textbox(Inches(5.5), Inches(1.8), Inches(6.8), Inches(4.9))
    tf_al = tb_alloc.text_frame
    tf_al.word_wrap = True
    p2 = tf_al.paragraphs[0]
    p2.text = "PLANNED CAPITAL ALLOCATION BREAKDOWN"
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = VIOLET_ACCENT

    allocations = [
        ("40% ($100k) — Product Industrialization & CE/FCC Certification",
         "Transition breadboard circuit into an integrated 4-layer surface-mount PCB (SMD ESP32-WROOM-32E + integrated GaN H-bridge ICs). Complete FCC Part 15 and CE EMC pre-compliance and safety certification for lab equipment."),

        ("25% ($62.5k) — Computer Vision & Closed-Loop Control",
         "Develop custom miniature edge-AI camera module with onboard OpenCV particle centroid tracking. Implement closed-loop PID trapping algorithm that automatically compensates for air currents in real time."),

        ("20% ($50k) — Sourcing, Tooling & Initial 500-Unit Production Run",
         "Procure production tooling for injection-molded acoustic horn baffles and anodized aluminum enclosure. Source bulk piezoelectric components to lock in BOM cost below $12/unit."),

        ("15% ($37.5k) — Pilot Deployments, Academic Marketing & IP Protection",
         "Deploy 25 evaluation units across leading research universities in the US, Europe, and India. File provisional patents protecting the silicon-locked zero-CPU multi-channel acoustic steering architecture.")
    ]
    for ha, ba in allocations:
        p = tf_al.add_paragraph()
        p.text = f"{ha}\n"
        p.font.name = FONT_TITLE
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
        r = p.add_run()
        r.text = f"{ba}\n"
        r.font.name = FONT_BODY
        r.font.size = Pt(9.5)
        r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 14: 24-MONTH ROADMAP & KEY MILESTONES
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Commercial Ask", "24-Month Execution Roadmap & Value Milestones", "Disciplined phase gates taking the platform from seed capital to commercial scale.")

    phases = [
        ("PHASE 1 (M1 – M6)",
         "Industrialization & Compliance",
         [("Milestone 1.1:", "Finalize commercial SMD PCB with integrated GaN drivers."),
          ("Milestone 1.2:", "Complete CE / FCC EMC and acoustic safety certifications."),
          ("Milestone 1.3:", "Release Levitator Studio Pro Beta with Python automation API."),
          ("Milestone 1.4:", "Fabricate injection-molded acoustic horn array chassis.")],
         CYAN_ACCENT),

        ("PHASE 2 (M7 – M12)",
         "Pilot Trials & Vision Integration",
         [("Milestone 2.1:", "Ship 25 pilot evaluation units to research university partners."),
          ("Milestone 2.2:", "Integrate edge-camera module for closed-loop particle tracking."),
          ("Milestone 2.3:", "Publish collaborative research validation papers with early adopters."),
          ("Milestone 2.4:", "Expand array to 16-transducer (4x4) full 3D manipulation prototype.")],
         VIOLET_ACCENT),

        ("PHASE 3 (M13 – M18)",
         "Commercial Launch & Channels",
         [("Milestone 3.1:", "Full commercial roll-out of Academic ($799) & Enterprise ($2,499) editions."),
          ("Milestone 3.2:", "Sign 2 distribution agreements with scientific equipment distributors."),
          ("Milestone 3.3:", "Launch modular chamber accessories (inert gas, temperature control)."),
          ("Milestone 3.4:", "Surpass 350 commercial units sold; reach cash-flow breakeven.")],
         GREEN_ACCENT),

        ("PHASE 4 (M19 – M24)",
         "Enterprise Scale & Series A",
         [("Milestone 4.1:", "Achieve $1.2M annual run-rate (ARR) across hardware and SaaS."),
          ("Milestone 4.2:", "OEM partnership for integration into automated bio-workstations."),
          ("Milestone 4.3:", "Launch multi-particle acoustic tweezers platform."),
          ("Milestone 4.4:", "Prepare for Series A expansion into global clinical automation.")],
         AMBER_ACCENT)
    ]

    for idx, (p_title, p_sub, p_items, p_color) in enumerate(phases):
        px = 0.8 + idx * 3.0
        add_card(s14, px, 1.6, 2.85, 5.3)
        tbox = s14.shapes.add_textbox(Inches(px + 0.15), Inches(1.8), Inches(2.55), Inches(4.9))
        tf = tbox.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = p_title
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = p_color

        p_s = tf.add_paragraph()
        p_s.text = p_sub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(9.5)
        p_s.font.color.rgb = TEXT_MUTED

        for h_m, b_m in p_items:
            p_i = tf.add_paragraph()
            p_i.text = f"• {h_m} "
            p_i.font.name = FONT_TITLE
            p_i.font.size = Pt(9.5)
            p_i.font.bold = True
            p_i.font.color.rgb = TEXT_PRIMARY
            r = p_i.add_run()
            r.text = b_m
            r.font.name = FONT_BODY
            r.font.bold = False
            r.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 15: CONCLUSION & STRATEGIC VISION
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)

    # Ambient center card
    add_card(s15, 1.2, 1.0, 10.933, 5.5, bg_color=CARD_BG, border_color=GREEN_ACCENT)

    tb_c = s15.shapes.add_textbox(Inches(1.6), Inches(1.3), Inches(10.133), Inches(4.9))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p1 = tf_c.paragraphs[0]
    p1.text = "STRATEGIC SUMMARY & INVESTMENT HIGHLIGHTS"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = CYAN_ACCENT

    summary_pillars = [
        ("Technological Superiority:", "Proprietary zero-CPU silicon PWM phase engine running on crystal-accurate 80 MHz APB timers, generating powerful 24 Vpp push-pull acoustic traps with zero software jitter."),
        ("Massive Unlocked Market:", "Democratizes a historically $30,000 technology with an industrial BOM under $12, addressing an $8.2B global laboratory automation and non-contact handling market."),
        ("High-Margin Scalable Model:", "85%+ hardware gross margins combined with recurring SaaS revenue from Levitator Studio Pro and modular chamber accessories."),
        ("Proven & De-risked Prototype:", "Fully functional 6-transducer hardware prototype with embedded Wi-Fi mission control, REST API, automated resonance tuning, and validated levitation."),
        ("The Immediate Next Step:", "Deploying $250k seed capital across industrial PCB certification, optical closed-loop tracking, and a 500-unit commercial production batch.")
    ]
    for hs, bs in summary_pillars:
        p = tf_c.add_paragraph()
        p.text = f"✔ {hs} "
        p.font.name = FONT_TITLE
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = bs
        r.font.name = FONT_BODY
        r.font.color.rgb = TEXT_MUTED

    p_cta = tf_c.add_paragraph()
    p_cta.text = "\nReady to pioneer the future of contactless acoustic automation."
    p_cta.font.name = FONT_TITLE
    p_cta.font.size = Pt(13)
    p_cta.font.bold = True
    p_cta.font.color.rgb = GREEN_ACCENT

    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    out_dir = "/Users/parth-agarwal/Desktop/EMBEDDED/project/PPT"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Acoustic_Levitator_Commercial_and_Technical_Deck.pptx")
    create_deck(out_file)
