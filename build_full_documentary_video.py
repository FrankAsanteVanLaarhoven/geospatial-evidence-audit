#!/usr/bin/env python3
"""
SpatialForge 3D - Comprehensive Master Walkthrough & Documentary Video Generator
- Narration: Full voice-over for every workflow using high-fidelity TTS (Daniel).
- Text Alignment: 100% mathematically centered text and buttons (resolving the UI misalignment in the user image).
- Comprehensive Workflows: Explains Function, Why & Impact, and Real-World Usage for defense, space agencies, and critical infrastructure.
- Interactive Cursor & Click Ripples: Realistic pointer with smooth cubic easing and physical activation pulses.
- Clean Layout: NO bulky bottom overlays blocking the UI.
- Audio Bed: Mixed voiceover with ambient aerospace telemetry audio.
- FastStart H.264 1080p export saved directly to Desktop.
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

OUTPUT_WORKSPACE = "/Users/favl/Downloads/geospatial-evidence-replay/SpatialForge_3D_Promo_Walkthrough.mp4"
OUTPUT_DESKTOP = "/Users/favl/Desktop/SpatialForge_3D_Promo_Walkthrough.mp4"
BRAIN_DIR = "/Users/favl/.gemini/antigravity/brain/9c32895a-24a9-4867-ac3b-23972f1fc404"
AUDIO_DIR = "/tmp/spatialforge_narration"
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"

os.makedirs(AUDIO_DIR, exist_ok=True)

WIDTH = 1920
HEIGHT = 1080
FPS = 30

FONT_SANS = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"

try:
    font_hero = ImageFont.truetype(FONT_SANS, 54)
    font_title = ImageFont.truetype(FONT_SANS, 22)
    font_card_head = ImageFont.truetype(FONT_SANS, 18)
    font_body = ImageFont.truetype(FONT_SANS, 13)
    font_bold = ImageFont.truetype(FONT_SANS, 13)
    font_badge = ImageFont.truetype(FONT_MONO, 12)
    font_mono_header = ImageFont.truetype(FONT_MONO, 14)
    font_mono_small = ImageFont.truetype(FONT_MONO, 12)
except Exception:
    font_hero = ImageFont.load_default()
    font_title = ImageFont.load_default()
    font_card_head = ImageFont.load_default()
    font_body = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_badge = ImageFont.load_default()
    font_mono_header = ImageFont.load_default()
    font_mono_small = ImageFont.load_default()

# Master Narratives & Workflow Explanations
SCENE_SCRIPTS = [
    {
        "id": "prologue",
        "type": "card_intro",
        "section": "SYSTEM ARCHITECTURE",
        "voice": "Welcome to SpatialForge 3D, the sovereign spatial intelligence and orbital command platform. Designed for aerospace defense, satellite fleet operators, and critical infrastructure authorities, SpatialForge unifies planetary digital twins with on-device neural sensor fusion.",
    },
    {
        "id": "step_01_engage",
        "asset_before": "landing_splash",
        "asset_after": "landing_engage",
        "section": "MISSION INITIALIZATION",
        "voice": "We begin on the landing console, watching the SpaceX Starship liftoff emulation. Clicking Engage System connects the WebGL 3D Cesium core and restores our sovereign intelligence session. In real-world operations, this allows aerospace engineers and mission directors to immediately transition from orbital launch tracking to global ground domain awareness.",
        "start_cursor": (960, 750),
        "target_cursor": (960, 570),
        "card_pos": (640, 240, 640, 210),
        "badge": "01 // SYSTEM INITIALIZATION",
        "title": "Engage Sovereign Command Session",
        "function": "Initializes Cesium 3D WebGL engine and restores multi-source geospatial session.",
        "impact": "Eliminates multi-application fragmentation by unifying aerospace telemetry with global terrain.",
        "usage": "Defense operations centers, spaceport launch ranges, and orbital payload tracking teams.",
        "accent": (0, 220, 255),
    },
    {
        "id": "step_02_cockpit",
        "asset_before": "console_3d",
        "asset_after": "console_3d",
        "section": "STARSHIP COCKPIT",
        "voice": "Clicking the Starship and Starlink cockpit button activates our real-time aerospace flight deck. This interface tracks thirty-three Raptor engines, Mach 24.8 orbital velocity, altitude, and staging dynamics. For space defense agencies, having instantaneous flight dynamics synchronized with planetary topography is critical for launch range safety and trajectory verification.",
        "start_cursor": (960, 570),
        "target_cursor": (1530, 28),
        "card_pos": (920, 75, 650, 210),
        "badge": "02 // STARSHIP MISSION COCKPIT",
        "title": "SpaceX Starship Flight 5 & 6 HUD",
        "function": "Renders real-time telemetry, 33 Raptor engine staging, and orbital trajectory arcs.",
        "impact": "Enables millisecond-accurate monitoring of ascent velocity, pitch deflection, and staging separation.",
        "usage": "Commercial launch providers, US Space Force range safety, and telemetry analysis stations.",
        "accent": (0, 240, 255),
    },
    {
        "id": "step_03_multicam",
        "asset_before": "rocket_cam",
        "asset_after": "earth_cam",
        "section": "MULTI-CAM SENSORS",
        "voice": "Next, we toggle the cockpit multi-cam sensor feeds between RocketCam and EarthCam. RocketCam monitors the vacuum Raptor engine plumes and Starlink dish link, while EarthCam provides real-time nadir orbital imagery. This visual and sensor synchronization gives flight controllers visual truth alongside telemetry, critical for in-flight anomaly detection.",
        "start_cursor": (1530, 28),
        "target_cursor": (1170, 360),
        "card_pos": (460, 210, 660, 210),
        "badge": "03 // MULTI-CAM FLIGHT DECK",
        "title": "Exterior RocketCam & Orbital EarthCam",
        "function": "Streams synchronized optical sensor feeds linked to real-time vehicle GPS coordinates.",
        "impact": "Validates engine thermal shielding, plume ionization, and atmospheric curvature visually.",
        "usage": "Mission flight controllers, satellite deployment teams, and aerospace broadcast networks.",
        "accent": (255, 180, 0),
    },
    {
        "id": "step_04_mechazilla",
        "asset_before": "earth_cam",
        "asset_after": "mechazilla_catch",
        "section": "MECHAZILLA CATCH",
        "voice": "We now trigger the historic Mechazilla Tower Catch sequence. The platform emulates the Super Heavy booster's rapid four-point-two G deceleration and center Raptor hover-flip, culminating in the precision chopstick clamp. This breakthrough enables rapid rocket reusability, slashing orbital launch costs by ninety percent for commercial and government constellations.",
        "start_cursor": (1170, 360),
        "target_cursor": (330, 360),
        "card_pos": (370, 180, 660, 210),
        "badge": "04 // MECHAZILLA TOWER CATCH",
        "title": "Precision Dual Chopstick Booster Capture",
        "function": "Emulates autonomous booster aerodynamic dive, hover-flip, and chopstick clamp lock.",
        "impact": "Revolutionizes space economics by eliminating booster ocean recovery and turnaround delays.",
        "usage": "Starbase launch operations, rapid orbital deployment logistics, and heavy-lift space programs.",
        "accent": (255, 140, 0),
    },
    {
        "id": "step_05_starlink",
        "asset_before": "mechazilla_catch",
        "asset_after": "starlink_mesh",
        "section": "STARLINK & CARRIERS",
        "voice": "Transitioning to the Connectivity module, the platform visualizes over six thousand Starlink LEO satellites with active cross-links. Crucially, it detects regional mobile carrier handoffs across Ukraine, the Middle East, and North America. When terrestrial infrastructure fails during natural disasters or conflict, Starlink Direct-to-Cell maintains sovereign communication lines.",
        "start_cursor": (330, 360),
        "target_cursor": (1420, 360),
        "card_pos": (760, 180, 660, 210),
        "badge": "05 // STARLINK LEO & DIRECT-TO-CELL",
        "title": "LEO Space Mesh & Mobile Carrier Detection",
        "function": "Tracks 6,000+ LEO orbits and maps Direct-to-Cell connectivity to Kyivstar, STC, and T-Mobile.",
        "impact": "Guarantees zero communication blackout when ground fiber and cellular towers are disrupted.",
        "usage": "Disaster relief agencies, humanitarian missions, and sovereign defense tactical networks.",
        "accent": (190, 130, 255),
    },
    {
        "id": "step_06_infra",
        "asset_before": "starlink_mesh",
        "asset_after": "infra_energy",
        "section": "CRITICAL INFRASTRUCTURE",
        "voice": "In the Critical Infrastructure and Energy module, we activate four thousand three hundred hyperscale data centers, five hundred hydroelectric dams, and global submarine fiber cables. Our semantic Find and Fly instantly vectors to Frankfurt FRA1 and the Dnipro Hydroelectric Station. This allows utility authorities and hyperscalers to correlate cloud compute capacity directly with power grid stability.",
        "start_cursor": (1420, 360),
        "target_cursor": (1520, 360),
        "card_pos": (720, 160, 670, 210),
        "badge": "06 // GLOBAL CRITICAL INFRASTRUCTURE",
        "title": "4,300+ Data Centers, Power Dams & Cables",
        "function": "Semantic search targeting hyperscale compute, energy generation, and subsea cable landing stations.",
        "impact": "Exposes regional dependencies between power grid output and hyperscale compute availability.",
        "usage": "National grid operators, cloud hyperscalers (AWS, Google, Azure), and energy regulators.",
        "accent": (255, 215, 0),
    },
    {
        "id": "step_07_sitrep",
        "asset_before": "infra_energy",
        "asset_after": "ai_sitrep",
        "section": "AUTONOMOUS AI SITREP",
        "voice": "We now execute an Autonomous AI SITREP. The on-device neural matrix fuses satellite telemetry, power grid health, and communications into an executive briefing. It assigns DEFCON readiness, locks onto active satellite beams, and assesses critical infrastructure risk, delivering automated decision intelligence without cloud latency.",
        "start_cursor": (1520, 360),
        "target_cursor": (1540, 480),
        "card_pos": (600, 140, 670, 210),
        "badge": "07 // NEURAL SENSOR FUSION",
        "title": "Autonomous AI Situation Briefing (SITREP)",
        "function": "On-device neural matrix fuses multi-layer intelligence into an actionable military SITREP.",
        "impact": "Eliminates cognitive overload during crisis events by synthesizing thousands of sensors instantly.",
        "usage": "Emergency operations centers, military command staff, and critical infrastructure executives.",
        "accent": (0, 255, 170),
    },
    {
        "id": "step_08_blackout",
        "asset_before": "ai_sitrep",
        "asset_after": "ai_sitrep",
        "section": "GRID RESILIENCE TEST",
        "voice": "To demonstrate true sovereign resilience, we trigger the one-hundred-and-ten kilovolt Grid Blackout simulation. As regional power drops, the platform simulates instantaneous fallback to forty-eight hour emergency UPS reserves and diverts one hundred percent of cellular routing to Starlink Direct-to-Cell satellites, proving unbroken continuity during grid collapse.",
        "start_cursor": (1540, 480),
        "target_cursor": (1540, 560),
        "card_pos": (600, 140, 670, 210),
        "badge": "08 // RESILIENCE STRESS TEST",
        "title": "110kV Blackout & LEO Satellite Failover",
        "function": "Simulates complete substation power failure to verify automated failover mechanisms.",
        "impact": "Proves operational continuity for financial systems, hospitals, and command posts during blackouts.",
        "usage": "Homeland security, electrical grid operators, and mission-critical data center facilities.",
        "accent": (255, 75, 75),
    },
    {
        "id": "step_09_recon",
        "asset_before": "ai_sitrep",
        "asset_after": "antwerp_port",
        "section": "TACTICAL RECON",
        "voice": "Finally, in Tactical Views, we inspect multi-theater operations, vectoring to the Port of Antwerp for real-time AIS maritime tracking, and the Texas State Capitol for drone corridor surveillance. With integrated air-gapped flight recording, sovereign agencies can review mission telemetry securely without risk of data exfiltration.",
        "start_cursor": (1540, 560),
        "target_cursor": (1400, 28),
        "card_pos": (700, 75, 670, 210),
        "badge": "09 // TACTICAL INTELLIGENCE",
        "title": "Multi-Theater Recon: Maritime AIS & UAV Paths",
        "function": "Tracks maritime vessel vectors and UAV flight corridors with air-gapped replay capabilities.",
        "impact": "Provides real-time domain awareness across maritime choke points and urban airspace.",
        "usage": "Coast guards, port authorities, urban airspace managers, and sovereign defense intelligence.",
        "accent": (0, 240, 200),
    },
    {
        "id": "epilogue",
        "type": "card_outro",
        "section": "MISSION READY",
        "voice": "SpatialForge 3D represents the future of sovereign spatial intelligence. From orbital mechanics to critical energy grids, the platform is certified and ready for enterprise and defense deployment.",
    }
]

ASSET_MAP = {
    "landing_splash": os.path.join(BRAIN_DIR, "starship_cinematic_globe_backdrop_live.png"),
    "landing_engage": os.path.join(BRAIN_DIR, "starship_clean_no_overlap_live.png"),
    "console_3d": os.path.join(BRAIN_DIR, "console_screen_view.png"),
    "rocket_cam": os.path.join(BRAIN_DIR, "starship_starlink_media_live.png"),
    "earth_cam": os.path.join(BRAIN_DIR, "starship_orbital_earthcam_live.png"),
    "mechazilla_catch": os.path.join(BRAIN_DIR, "starship_landing_page_catch_showcase.png"),
    "starlink_mesh": os.path.join(BRAIN_DIR, "openrouter_all_layers_live.png"),
    "infra_energy": os.path.join(BRAIN_DIR, "starship_infra_energy_live.png"),
    "ai_sitrep": os.path.join(BRAIN_DIR, "ai_sitrep_grid_simulation_live.png"),
    "antwerp_port": os.path.join(BRAIN_DIR, "antwerp_port_live.png"),
}

print("Loading image assets...")
CACHED_ASSETS = {}
for k, path in ASSET_MAP.items():
    if os.path.exists(path):
        CACHED_ASSETS[k] = Image.open(path).convert("RGBA")
        print(f"  [OK] {k}: {CACHED_ASSETS[k].size}")
    else:
        print(f"  [MISSING] {k}: {path}")

def generate_voiceovers():
    """Generates Daniel's authoritative voiceover for every scene and computes audio duration."""
    print("\nGenerating authoritative voiceover audio tracks with Daniel...")
    audio_files = []
    
    for i, s in enumerate(SCENE_SCRIPTS):
        voice_text = s["voice"]
        aiff_path = os.path.join(AUDIO_DIR, f"scene_{i:02d}.aiff")
        wav_path = os.path.join(AUDIO_DIR, f"scene_{i:02d}.wav")
        
        # Run macOS say with voice Daniel
        cmd_say = ["say", "-v", "Daniel", "-o", aiff_path, voice_text]
        subprocess.run(cmd_say, check=True)
        
        # Convert to WAV
        cmd_conv = [FFMPEG_PATH, "-y", "-i", aiff_path, "-ar", "44100", "-ac", "2", wav_path]
        subprocess.run(cmd_conv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Measure duration with ffprobe
        cmd_probe = [
            "/opt/homebrew/bin/ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            wav_path
        ]
        out = subprocess.check_output(cmd_probe).decode().strip()
        duration = float(out) + 1.2  # add 1.2s padding for natural pacing
        s["duration"] = duration
        s["audio_path"] = wav_path
        print(f"  [Scene {i:02d}] {s['section']}: {duration:.2f}s ({wav_path})")
        audio_files.append(wav_path)

    # Concatenate all speech audio files into a single master speech track
    concat_list_path = os.path.join(AUDIO_DIR, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for p in audio_files:
            f.write(f"file '{p}'\n")
            
    master_speech_path = os.path.join(AUDIO_DIR, "master_speech.wav")
    cmd_concat = [
        FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-c", "copy", master_speech_path
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Generate a subtle ambient aerospace low-frequency background telemetry drone
    total_duration = sum(s["duration"] for s in SCENE_SCRIPTS)
    ambient_path = os.path.join(AUDIO_DIR, "ambient_drone.wav")
    cmd_synth = [
        FFMPEG_PATH, "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency=72:duration={total_duration + 2}",
        "-af", "volume=0.08,lowpass=f=200",
        ambient_path
    ]
    subprocess.run(cmd_synth, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Mix speech with subtle ambient bed
    final_audio_path = os.path.join(AUDIO_DIR, "final_master_audio.m4a")
    cmd_mix = [
        FFMPEG_PATH, "-y",
        "-i", master_speech_path,
        "-i", ambient_path,
        "-filter_complex", "[0:a]volume=1.0[speech];[1:a]volume=0.12[bed];[speech][bed]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "[out]",
        "-c:a", "aac",
        "-b:a", "192k",
        final_audio_path
    ]
    subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Master voiceover & ambient mix created: {final_audio_path}\n")
    return final_audio_path

def ease_in_out(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        f = (2 * t) - 2
        return 0.5 * f * f * f + 1

def draw_centered_text(draw, y, text, font, fill):
    """Dynamically calculates font bounding box and centers text mathematically."""
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    x = (WIDTH - text_w) // 2
    draw.text((x, y), text, fill=fill, font=font)
    return text_w, bbox[3] - bbox[1]

def draw_centered_button(draw, y, text, font, fill_btn, outline_btn, fill_text, pad_x=36, pad_y=16):
    """Mathematically centers button outline and inner text perfectly."""
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    btn_w = text_w + pad_x * 2
    btn_h = text_h + pad_y * 2
    btn_x = (WIDTH - btn_w) // 2
    draw.rounded_rectangle([btn_x, y, btn_x + btn_w, y + btn_h], radius=8, fill=fill_btn, outline=outline_btn, width=1)
    text_x = btn_x + pad_x
    text_y = y + pad_y
    draw.text((text_x, text_y), text, fill=fill_text, font=font)
    return btn_x, y, btn_w, btn_h

def draw_cursor(draw, x, y, is_clicking=False, click_age=0.0):
    if click_age > 0.0 and click_age < 1.0:
        radius = int(8 + click_age * 28)
        alpha = int((1.0 - click_age) * 220)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], outline=(0, 240, 255, alpha), width=2)
        inner_r = int(radius * 0.5)
        draw.ellipse([x - inner_r, y - inner_r, x + inner_r, y + inner_r], fill=(0, 240, 255, int(alpha * 0.4)))
    
    poly = [(x, y), (x, y + 21), (x + 5, y + 16), (x + 11, y + 24), (x + 15, y + 22), (x + 9, y + 14), (x + 17, y + 14)]
    shadow_poly = [(px + 2, py + 2) for px, py in poly]
    draw.polygon(shadow_poly, fill=(0, 0, 0, 140))
    fill_col = (210, 250, 255, 255) if not is_clicking else (0, 255, 240, 255)
    draw.polygon(poly, fill=fill_col, outline=(15, 25, 40, 255))

def draw_floating_card(draw, card_x, card_y, card_w, card_h, badge_text, title, function_text, impact_text, usage_text, target_pt, accent=(0, 220, 255)):
    """Renders comprehensive workflow explanation card with zero text overlap."""
    tx, ty = target_pt
    anchor_x = max(card_x, min(card_x + card_w, tx))
    anchor_y = card_y + card_h if ty > card_y + card_h else card_y
    draw.line([(anchor_x, anchor_y), (tx, ty)], fill=(accent[0], accent[1], accent[2], 140), width=1)
    draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=accent)

    # Translucent card background
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=8, fill=(8, 16, 28, 238), outline=(accent[0], accent[1], accent[2], 180), width=1)
    draw.rounded_rectangle([card_x, card_y, card_x + 5, card_y + card_h], radius=2, fill=accent)

    # Badge
    bw = len(badge_text) * 8 + 16
    draw.rounded_rectangle([card_x + 16, card_y + 12, card_x + 16 + bw, card_y + 32], radius=4, fill=(accent[0], accent[1], accent[2], 40), outline=accent, width=1)
    draw.text((card_x + 24, card_y + 15), badge_text, fill=accent, font=font_badge)

    # Title
    draw.text((card_x + 16, card_y + 40), title, fill=(255, 255, 255, 255), font=font_card_head)

    # Function
    y_c = card_y + 72
    draw.text((card_x + 16, y_c), "FUNCTION:     ", fill=(130, 180, 220, 255), font=font_bold)
    draw.text((card_x + 115, y_c), function_text[:70], fill=(225, 235, 245, 255), font=font_body)
    if len(function_text) > 70:
        y_c += 18
        draw.text((card_x + 115, y_c), function_text[70:140], fill=(225, 235, 245, 255), font=font_body)

    # Why & Impact
    y_c += 24
    draw.text((card_x + 16, y_c), "WHY & IMPACT: ", fill=(0, 255, 180, 255), font=font_bold)
    draw.text((card_x + 115, y_c), impact_text[:70], fill=(160, 255, 220, 255), font=font_body)
    if len(impact_text) > 70:
        y_c += 18
        draw.text((card_x + 115, y_c), impact_text[70:140], fill=(160, 255, 220, 255), font=font_body)

    # Real-World Usage
    y_c += 24
    draw.text((card_x + 16, y_c), "REAL USAGE:   ", fill=(255, 215, 0, 255), font=font_bold)
    draw.text((card_x + 115, y_c), usage_text[:70], fill=(255, 240, 180, 255), font=font_body)
    if len(usage_text) > 70:
        y_c += 18
        draw.text((card_x + 115, y_c), usage_text[70:140], fill=(255, 240, 180, 255), font=font_body)

def draw_hud_top_bar(draw, timecode, section_name):
    draw.rectangle([0, 0, WIDTH, 36], fill=(6, 12, 22, 220))
    draw.line([0, 36, WIDTH, 36], fill=(0, 200, 255, 90), width=1)
    draw.ellipse([20, 13, 30, 23], fill=(255, 50, 50, 255))
    draw.text((38, 10), f"MASTER TUTORIAL WALKTHROUGH  [● {timecode}]", fill=(255, 255, 255, 255), font=font_mono_header)
    draw.text((540, 10), "SPATIALFORGE 3D // SOVEREIGN SPATIAL INTELLIGENCE", fill=(0, 210, 255, 255), font=font_mono_header)
    draw.text((WIDTH - 420, 10), f"WORKFLOW: {section_name.upper()}", fill=(255, 215, 0, 255), font=font_mono_header)

def get_fitted_base_image(img):
    iw, ih = img.size
    scale = max(WIDTH / iw, HEIGHT / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.BILINEAR)
    x1 = (nw - WIDTH) // 2
    y1 = (nh - HEIGHT) // 2
    return resized.crop((x1, y1, x1 + WIDTH, y1 + HEIGHT))

def render_brand_card(draw, progress, is_intro=True):
    """Draws cinematic title card with 100% mathematically centered text and button."""
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(6, 12, 22, 255))
    
    # Modern aerospace grid
    for x in range(0, WIDTH, 96):
        draw.line([x, 0, x, HEIGHT], fill=(20, 40, 65, 80), width=1)
    for y in range(0, HEIGHT, 96):
        draw.line([0, y, WIDTH, y], fill=(20, 40, 65, 80), width=1)
        
    cy = HEIGHT // 2
    
    if is_intro:
        draw_centered_text(draw, cy - 140, "SPATIALFORGE 3D", font_hero, (255, 255, 255, 255))
        draw_centered_text(draw, cy - 60, "SOVEREIGN SPATIAL INTELLIGENCE & SATELLITE COMMAND", font_title, (0, 220, 255, 255))
        draw_centered_text(draw, cy - 15, "FULL SPECTRUM AEROSPACE, ENERGY & DEFENSE PLATFORM", font_body, (190, 220, 245, 255))
        
        # Capability chips row
        badges = ["CESIUM 3D CORE", "STARSHIP FLIGHT 5/6", "MECHAZILLA CATCH", "4,300+ DATA CENTERS", "AI SITREP ENGINE"]
        total_w = len(badges) * 190
        start_x = (WIDTH - total_w) // 2
        for i, b in enumerate(badges):
            bx = start_x + i * 190
            draw.rounded_rectangle([bx, cy + 30, bx + 175, cy + 64], radius=4, fill=(12, 28, 48, 220), outline=(0, 200, 255, 180), width=1)
            draw.text((bx + 12, cy + 40), b, fill=(210, 240, 255, 255), font=font_badge)
            
        draw_centered_text(draw, cy + 130, "COMPREHENSIVE MASTER WORKFLOW WALKTHROUGH", font_mono_header, (255, 215, 0, 255))
    else:
        # OUTRO CARD: Mathematical centering fixes the off-center bug reported by user
        draw_centered_text(draw, cy - 150, "SPATIALFORGE 3D", font_hero, (255, 255, 255, 255))
        draw_centered_text(draw, cy - 70, "MISSION PLATFORM CERTIFIED", font_title, (0, 255, 180, 255))
        draw_centered_text(draw, cy - 20, "FULL SPECTRUM AEROSPACE & INFRASTRUCTURE COMMAND", font_body, (190, 220, 245, 255))
        
        # Deploy button: mathematically centered
        draw_centered_button(
            draw, cy + 35,
            "DEPLOY NOW: GITHUB / SPATIALFORGE-AI",
            font_title,
            fill_btn=(14, 28, 52, 230),
            outline_btn=(0, 220, 255, 220),
            fill_text=(255, 255, 255, 255),
            pad_x=36, pad_y=16
        )
        draw_centered_text(draw, cy + 130, "READY FOR DEFENSE & COMMERCIAL DEPLOYMENT", font_mono_small, (120, 160, 190, 255))

def main():
    final_audio_path = generate_voiceovers()

    total_duration = sum(s["duration"] for s in SCENE_SCRIPTS)
    total_frames = int(total_duration * FPS)
    print(f"\nRendering Video: {total_duration:.1f}s, {total_frames} frames @ {FPS} fps, 1920x1080.")

    raw_video_path = "/tmp/spatialforge_narration/raw_video.mp4"

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        raw_video_path
    ]

    print(f"Launching FFmpeg: {' '.join(cmd)}")
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    frame_index = 0
    current_cursor = (960, 540)

    for step_idx, step in enumerate(SCENE_SCRIPTS):
        step_duration = step["duration"]
        step_frames = int(step_duration * FPS)
        section = step.get("section", "PLATFORM")
        step_type = step.get("type", "interactive")
        
        print(f"Rendering Step {step_idx + 1}/{len(SCENE_SCRIPTS)}: {section} ({step_duration:.1f}s, {step_frames} frames)...")

        for f in range(step_frames):
            prog = f / max(1, step_frames - 1)
            time_sec = frame_index / FPS
            mins = int(time_sec // 60)
            secs = int(time_sec % 60)
            frames_rem = int(frame_index % FPS)
            timecode = f"{mins:02d}:{secs:02d}:{frames_rem:02d}"

            canvas = Image.new("RGBA", (WIDTH, HEIGHT), (6, 12, 22, 255))
            overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(overlay)

            if step_type == "card_intro":
                draw_canvas = ImageDraw.Draw(canvas)
                render_brand_card(draw_canvas, prog, is_intro=True)
                draw_hud_top_bar(draw_overlay, timecode, section)
            elif step_type == "card_outro":
                draw_canvas = ImageDraw.Draw(canvas)
                render_brand_card(draw_canvas, prog, is_intro=False)
                draw_hud_top_bar(draw_overlay, timecode, section)
            else:
                click_ratio = 0.30
                is_after_click = prog >= click_ratio
                active_key = step["asset_after"] if is_after_click else step["asset_before"]
                base_img = CACHED_ASSETS.get(active_key)
                if base_img:
                    fitted = get_fitted_base_image(base_img)
                    canvas.paste(fitted, (0, 0))
                
                start_c = step.get("start_cursor", current_cursor)
                target_c = step.get("target_cursor", start_c)
                move_prog = min(1.0, prog / click_ratio)
                eased_t = ease_in_out(move_prog)
                cur_x = int(start_c[0] + (target_c[0] - start_c[0]) * eased_t)
                cur_y = int(start_c[1] + (target_c[1] - start_c[1]) * eased_t)
                current_cursor = (cur_x, cur_y)
                
                is_clicking = abs(prog - click_ratio) < 0.05
                click_age = (prog - click_ratio) / (1.0 - click_ratio) if is_after_click else 0.0
                
                draw_hud_top_bar(draw_overlay, timecode, section)
                
                card_x, card_y, card_w, card_h = step["card_pos"]
                draw_floating_card(
                    draw_overlay,
                    card_x, card_y, card_w, card_h,
                    step["badge"],
                    step["title"],
                    step["function"],
                    step["impact"],
                    step["usage"],
                    target_c,
                    accent=step.get("accent", (0, 220, 255))
                )
                draw_cursor(draw_overlay, cur_x, cur_y, is_clicking=is_clicking, click_age=click_age)

            final_frame = Image.alpha_composite(canvas, overlay)
            pipe.stdin.write(final_frame.convert("RGB").tobytes())
            frame_index += 1

    pipe.stdin.close()
    pipe.wait()
    print("Raw video render complete!")

    # Mux final video and master audio track together
    print("\nMuxing video and Daniel voiceover narration audio...")
    cmd_mux = [
        FFMPEG_PATH, "-y",
        "-i", raw_video_path,
        "-i", final_audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-movflags", "+faststart",
        OUTPUT_WORKSPACE
    ]
    subprocess.run(cmd_mux, check=True)
    print(f"Master Walkthrough Promo Video complete! Stored at: {OUTPUT_WORKSPACE}")

    try:
        import shutil
        shutil.copy2(OUTPUT_WORKSPACE, OUTPUT_DESKTOP)
        print(f"Successfully mirrored to Desktop: {OUTPUT_DESKTOP}")
    except Exception as e:
        print(f"Desktop mirror notice (sandboxed): {e}")

if __name__ == "__main__":
    main()

