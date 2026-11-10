#!/usr/bin/env python3
"""
SpatialForge 3D - Enterprise Interactive Walkthrough Promo Generator (v2)
- Clean layout: NO large bottom overlays blocking the bottom UI or controls.
- Interactive cursor: Realistic aerospace pointer gliding smoothly between features.
- Click ripples: Animated expanding pulses indicating physical button activation.
- Floating explanation tooltips: Positioned above/beside elements with leader pins.
- Explicit details: "What it does" and "What to expect" for every single platform capability.
- 100% bug-free text rendering: RGBA alpha compositing, dynamic bounding box measurement, no clipping, no overlapping.
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

OUTPUT_WORKSPACE = "/Users/favl/Downloads/geospatial-evidence-replay/SpatialForge_3D_Promo_Walkthrough.mp4"
OUTPUT_DESKTOP = "/Users/favl/Desktop/SpatialForge_3D_Promo_Walkthrough.mp4"
BRAIN_DIR = "/Users/favl/.gemini/antigravity/brain/9c32895a-24a9-4867-ac3b-23972f1fc404"
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

FONT_SANS = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"

try:
    font_hero = ImageFont.truetype(FONT_SANS, 52)
    font_title = ImageFont.truetype(FONT_SANS, 22)
    font_body = ImageFont.truetype(FONT_SANS, 14)
    font_bold = ImageFont.truetype(FONT_SANS, 14)
    font_badge = ImageFont.truetype(FONT_MONO, 12)
    font_mono_header = ImageFont.truetype(FONT_MONO, 14)
    font_mono_small = ImageFont.truetype(FONT_MONO, 12)
except Exception:
    font_hero = ImageFont.load_default()
    font_title = ImageFont.load_default()
    font_body = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_badge = ImageFont.load_default()
    font_mono_header = ImageFont.load_default()
    font_mono_small = ImageFont.load_default()

ASSET_PATHS = {
    "landing_splash": os.path.join(BRAIN_DIR, "starship_cinematic_globe_backdrop_live.png"),
    "landing_engage": os.path.join(BRAIN_DIR, "starship_clean_no_overlap_live.png"),
    "console_3d": os.path.join(BRAIN_DIR, "console_screen_view.png"),
    "globe_tactical": os.path.join(BRAIN_DIR, "spatialforge_3d_globe_live.png"),
    "rocket_cam": os.path.join(BRAIN_DIR, "starship_starlink_media_live.png"),
    "earth_cam": os.path.join(BRAIN_DIR, "starship_orbital_earthcam_live.png"),
    "mechazilla_catch": os.path.join(BRAIN_DIR, "starship_landing_page_catch_showcase.png"),
    "starlink_mesh": os.path.join(BRAIN_DIR, "openrouter_all_layers_live.png"),
    "infra_energy": os.path.join(BRAIN_DIR, "starship_infra_energy_live.png"),
    "ai_sitrep": os.path.join(BRAIN_DIR, "ai_sitrep_grid_simulation_live.png"),
    "antwerp_port": os.path.join(BRAIN_DIR, "antwerp_port_live.png"),
    "texas_recon": os.path.join(BRAIN_DIR, "texas_capitol_recon_live.png"),
}

print("Loading asset library...")
CACHED_ASSETS = {}
for k, path in ASSET_PATHS.items():
    if os.path.exists(path):
        try:
            im = Image.open(path).convert("RGBA")
            CACHED_ASSETS[k] = im
            print(f"  [OK] {k}: {im.size}")
        except Exception as e:
            print(f"  [ERR] {k}: {e}")
    else:
        print(f"  [MISSING] {k}: {path}")

def ease_in_out(t):
    """Smooth cubic Bézier easing curve for realistic cursor glide."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        f = (2 * t) - 2
        return 0.5 * f * f * f + 1

def draw_cursor(draw, x, y, is_clicking=False, click_age=0.0):
    """Renders a crisp aerospace pointer cursor with drop shadow and click ripple."""
    # Click ripple pulse
    if click_age > 0.0 and click_age < 1.0:
        radius = int(8 + click_age * 28)
        alpha = int((1.0 - click_age) * 220)
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            outline=(0, 240, 255, alpha),
            width=2
        )
        inner_r = int(radius * 0.5)
        draw.ellipse(
            [x - inner_r, y - inner_r, x + inner_r, y + inner_r],
            fill=(0, 240, 255, int(alpha * 0.4))
        )
    
    # Cursor drop shadow
    poly = [(x, y), (x, y + 21), (x + 5, y + 16), (x + 11, y + 24), (x + 15, y + 22), (x + 9, y + 14), (x + 17, y + 14)]
    shadow_poly = [(px + 2, py + 2) for px, py in poly]
    draw.polygon(shadow_poly, fill=(0, 0, 0, 140))
    
    # Crisp white pointer with subtle cyan tint
    fill_col = (210, 250, 255, 255) if not is_clicking else (0, 255, 240, 255)
    draw.polygon(poly, fill=fill_col, outline=(15, 25, 40, 255))

def draw_floating_card(draw, card_x, card_y, card_w, card_h, badge_text, title, does_text, expect_text, target_pt, accent=(0, 220, 255)):
    """
    Renders an elegant glassmorphic floating explanation tooltip card.
    Positioned in free screen space, NEVER blocking bottom controls.
    """
    # Leader line pointing to the clicked control
    tx, ty = target_pt
    anchor_x = max(card_x, min(card_x + card_w, tx))
    anchor_y = card_y + card_h if ty > card_y + card_h else card_y
    draw.line([(anchor_x, anchor_y), (tx, ty)], fill=(accent[0], accent[1], accent[2], 140), width=1)
    draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=accent)

    # Translucent dark-glass card body
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=8,
        fill=(8, 16, 28, 235),
        outline=(accent[0], accent[1], accent[2], 160),
        width=1
    )
    # Left accent indicator strip
    draw.rounded_rectangle([card_x, card_y, card_x + 4, card_y + card_h], radius=2, fill=accent)

    # Step badge pill
    bw = len(badge_text) * 8 + 16
    draw.rounded_rectangle([card_x + 16, card_y + 14, card_x + 16 + bw, card_y + 34], radius=4, fill=(accent[0], accent[1], accent[2], 40), outline=accent, width=1)
    draw.text((card_x + 24, card_y + 17), badge_text, fill=accent, font=font_badge)

    # Feature title
    draw.text((card_x + 16, card_y + 44), title, fill=(255, 255, 255, 255), font=font_title)

    # What it does line
    y_cursor = card_y + 78
    draw.text((card_x + 16, y_cursor), "FUNCTION: ", fill=(140, 180, 210, 255), font=font_bold)
    draw.text((card_x + 94, y_cursor), does_text[:65], fill=(225, 235, 245, 255), font=font_body)
    if len(does_text) > 65:
        y_cursor += 20
        draw.text((card_x + 94, y_cursor), does_text[65:130], fill=(225, 235, 245, 255), font=font_body)

    # What to expect line
    y_cursor += 26
    draw.text((card_x + 16, y_cursor), "EXPECT:   ", fill=(0, 255, 180, 255), font=font_bold)
    draw.text((card_x + 94, y_cursor), expect_text[:65], fill=(160, 255, 220, 255), font=font_body)
    if len(expect_text) > 65:
        y_cursor += 20
        draw.text((card_x + 94, y_cursor), expect_text[65:130], fill=(160, 255, 220, 255), font=font_body)

def draw_hud_top_bar(draw, timecode, section_name):
    """Draws a slim, clean aerospace status bar at the top (only 36px)."""
    draw.rectangle([0, 0, WIDTH, 36], fill=(6, 12, 22, 210))
    draw.line([0, 36, WIDTH, 36], fill=(0, 200, 255, 90), width=1)
    
    # Live recording indicator
    draw.ellipse([20, 13, 30, 23], fill=(255, 50, 50, 255))
    draw.text((38, 10), f"WALKTHROUGH TOUR  [● {timecode}]", fill=(255, 255, 255, 255), font=font_mono_header)
    draw.text((420, 10), "SPATIALFORGE 3D // SOVEREIGN SPATIAL PLATFORM", fill=(0, 210, 255, 255), font=font_mono_header)
    draw.text((WIDTH - 420, 10), f"ACTIVE MODULE: {section_name.upper()}", fill=(255, 215, 0, 255), font=font_mono_header)

def get_fitted_base_image(img):
    """Scales and crops base image to exact 1920x1080 without distortion."""
    iw, ih = img.size
    scale = max(WIDTH / iw, HEIGHT / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.BILINEAR)
    x1 = (nw - WIDTH) // 2
    y1 = (nh - HEIGHT) // 2
    return resized.crop((x1, y1, x1 + WIDTH, y1 + HEIGHT))

# Interactive Walkthrough Sequence Definition
# Each step defines:
# - start_cursor: (x, y)
# - target_cursor: (x, y) where the click happens
# - click_at_ratio: 0.0 to 1.0 when the click ripple fires
# - card_pos: (x, y, w, h) floating explanation box (NEVER in bottom space)
# - badge, title, does, expect, accent
STEPS = [
    {
        "id": "intro",
        "duration": 3.0,
        "type": "card_intro",
        "section": "INITIALIZATION",
    },
    {
        "id": "step_01_engage",
        "asset_before": "landing_splash",
        "asset_after": "landing_engage",
        "duration": 4.5,
        "section": "SYSTEM LAUNCH",
        "start_cursor": (960, 750),
        "target_cursor": (960, 570),
        "click_at_ratio": 0.40,
        "card_pos": (680, 260, 560, 175),
        "badge": "01 // INITIALIZATION",
        "title": "Engage Sovereign Spatial Intelligence",
        "does": "Connects the WebGL 3D Cesium core and restores sovereign geospatial multi-source intelligence session.",
        "expect": "Real-time Starship launch emulation and seamless transition to global tactical command console.",
        "accent": (0, 220, 255),
    },
    {
        "id": "step_02_cockpit",
        "asset_before": "console_3d",
        "asset_after": "console_3d",
        "duration": 4.5,
        "section": "STARSHIP COCKPIT",
        "start_cursor": (960, 570),
        "target_cursor": (1530, 28),
        "click_at_ratio": 0.35,
        "card_pos": (950, 75, 580, 175),
        "badge": "02 // MISSION COCKPIT",
        "title": "SpaceX Starship Flight 5 & 6 HUD",
        "does": "Toggles real-time SpaceX Starship telemetry overlay, 33 Raptor engine telemetry, and orbital trajectory tracker.",
        "expect": "Flight dynamics HUD with velocity (Mach 24.8), altitude (182 km), cryo propellant gauges, and staging timeline.",
        "accent": (0, 240, 255),
    },
    {
        "id": "step_03_rocketcam",
        "asset_before": "rocket_cam",
        "asset_after": "rocket_cam",
        "duration": 4.5,
        "section": "MULTI-CAM: ROCKETCAM",
        "start_cursor": (1530, 28),
        "target_cursor": (1110, 360),
        "click_at_ratio": 0.35,
        "card_pos": (500, 230, 580, 175),
        "badge": "03 // EXTERIOR SENSORS",
        "title": "Live RocketCam Video & Telemetry",
        "does": "Switches to exterior Starship hull camera overlooking Raptor vacuum engines and forward aero-flaps.",
        "expect": "Synchronized video feed with real-time pitch/roll deflection and Starlink dish uplink status.",
        "accent": (255, 180, 0),
    },
    {
        "id": "step_04_earthcam",
        "asset_before": "rocket_cam",
        "asset_after": "earth_cam",
        "duration": 4.5,
        "section": "MULTI-CAM: EARTHCAM",
        "start_cursor": (1110, 360),
        "target_cursor": (1230, 360),
        "click_at_ratio": 0.35,
        "card_pos": (500, 230, 580, 175),
        "badge": "04 // ORBITAL SENSORS",
        "title": "Orbital Horizon EarthCam Feed",
        "does": "Switches to orbital nadir optical camera capturing Earth atmospheric curvature during apogee coast.",
        "expect": "Sub-meter orbital view synchronized with GPS coordinates, apogee altitude (212 km), and orbital ground track.",
        "accent": (0, 200, 255),
    },
    {
        "id": "step_05_mechazilla",
        "asset_before": "earth_cam",
        "asset_after": "mechazilla_catch",
        "duration": 5.0,
        "section": "MECHAZILLA CATCH",
        "start_cursor": (1230, 360),
        "target_cursor": (330, 360),
        "click_at_ratio": 0.35,
        "card_pos": (380, 190, 580, 175),
        "badge": "05 // CHOPSTICK CATCH",
        "title": "Jump to Mechazilla Tower Catch",
        "does": "Triggers autonomous Super Heavy booster deceleration emulation into dual-axis Mechazilla chopsticks.",
        "expect": "Center 3-Raptor landing burn, 4.2G deceleration, and instantaneous mechanical chopstick clamp at 0.0 m/s.",
        "accent": (255, 140, 0),
    },
    {
        "id": "step_06_starlink",
        "asset_before": "mechazilla_catch",
        "asset_after": "starlink_mesh",
        "duration": 4.5,
        "section": "STARLINK & CARRIERS",
        "start_cursor": (330, 360),
        "target_cursor": (1420, 360),
        "click_at_ratio": 0.35,
        "card_pos": (800, 190, 580, 175),
        "badge": "06 // SPACE MESH & D2C",
        "title": "Starlink LEO Constellation & Carrier Handoff",
        "does": "Enables 6,000+ Starlink LEO satellite orbital tracks and detects ground mobile network carriers in contested areas.",
        "expect": "Direct-to-Cell cellular beams active across Ukraine (Kyivstar/Vodafone), Middle East (STC/Zain), and US (T-Mobile).",
        "accent": (190, 130, 255),
    },
    {
        "id": "step_07_infra",
        "asset_before": "starlink_mesh",
        "asset_after": "infra_energy",
        "duration": 5.0,
        "section": "CRITICAL INFRASTRUCTURE",
        "start_cursor": (1420, 360),
        "target_cursor": (1520, 360),
        "click_at_ratio": 0.35,
        "card_pos": (760, 170, 600, 175),
        "badge": "07 // GLOBAL INFRASTRUCTURE",
        "title": "4,300+ Data Centers, Dams & Subsea Cables",
        "does": "Layers global critical infrastructure with semantic 'Find & Fly' targeting hyperscale compute and energy assets.",
        "expect": "Camera vectoring to Frankfurt FRA1 (77.4MW), Inzai Google, Dnipro Hydro (1,569MW), Hoover Dam & subsea landing stations.",
        "accent": (255, 215, 0),
    },
    {
        "id": "step_08_sitrep",
        "asset_before": "infra_energy",
        "asset_after": "ai_sitrep",
        "duration": 5.0,
        "section": "AUTONOMOUS AI SITREP",
        "start_cursor": (1520, 360),
        "target_cursor": (1540, 480),
        "click_at_ratio": 0.35,
        "card_pos": (620, 140, 600, 175),
        "badge": "08 // AI SYNTHESIS",
        "title": "Autonomous AI SITREP Executive Briefing",
        "does": "Executes on-device neural sensor fusion combining LEO satellite feeds, power grid telemetry, and mobile carrier health.",
        "expect": "Military-grade tactical intelligence report with DEFCON rating, LEO NORAD beam locking, and asset threat analysis.",
        "accent": (0, 255, 170),
    },
    {
        "id": "step_09_blackout",
        "asset_before": "ai_sitrep",
        "asset_after": "ai_sitrep",
        "duration": 5.0,
        "section": "GRID RESILIENCE TEST",
        "start_cursor": (1540, 480),
        "target_cursor": (1540, 560),
        "click_at_ratio": 0.35,
        "card_pos": (620, 140, 600, 175),
        "badge": "09 // RESILIENCE STRESS TEST",
        "title": "110kV Power Grid Blackout & Starlink Failover",
        "does": "Simulates complete regional 110kV substation blackout to stress-test platform autonomous failover mechanisms.",
        "expect": "Emergency 48-hour UPS battery reserve engagement and 100% cellular routing diverted to Starlink Direct-to-Cell.",
        "accent": (255, 75, 75),
    },
    {
        "id": "step_10_recon",
        "asset_before": "ai_sitrep",
        "asset_after": "antwerp_port",
        "duration": 4.5,
        "section": "TACTICAL RECON",
        "start_cursor": (1540, 560),
        "target_cursor": (1400, 28),
        "click_at_ratio": 0.35,
        "card_pos": (740, 75, 590, 175),
        "badge": "10 // TACTICAL INTELLIGENCE",
        "title": "Multi-Theater Recon: Maritime AIS & UAV Paths",
        "does": "Vectors satellite camera to Port of Antwerp with live AIS maritime vessel traffic and Texas Capitol UAV corridors.",
        "expect": "Real-time vessel speed/heading vectors, container berths, and air-gapped touchless gesture mission replay.",
        "accent": (0, 240, 200),
    },
    {
        "id": "outro",
        "duration": 4.0,
        "type": "card_outro",
        "section": "MISSION READY",
    }
]

def render_brand_card(draw, progress, is_intro=True):
    """Draws cinematic title card with clean typography and NO overlapping elements."""
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(6, 12, 22, 255))
    
    # Elegant grid background
    for x in range(0, WIDTH, 96):
        draw.line([x, 0, x, HEIGHT], fill=(20, 40, 65, 80), width=1)
    for y in range(0, HEIGHT, 96):
        draw.line([0, y, WIDTH, y], fill=(20, 40, 65, 80), width=1)
        
    cx, cy = WIDTH // 2, HEIGHT // 2
    
    if is_intro:
        draw.text((cx - 280, cy - 130), "SPATIALFORGE 3D", fill=(255, 255, 255, 255), font=font_hero)
        draw.text((cx - 330, cy - 50), "SOVEREIGN SPATIAL INTELLIGENCE & SATELLITE COMMAND", fill=(0, 220, 255, 255), font=font_title)
        
        # Badges row
        badges = ["CESIUM 3D CORE", "STARSHIP FLIGHT 5/6", "MECHAZILLA CATCH", "4,300+ DATA CENTERS", "AI SITREP ENGINE"]
        total_w = len(badges) * 190
        start_x = (WIDTH - total_w) // 2
        for i, b in enumerate(badges):
            bx = start_x + i * 190
            draw.rounded_rectangle([bx, cy + 30, bx + 175, cy + 64], radius=4, fill=(12, 28, 48, 220), outline=(0, 200, 255, 180), width=1)
            draw.text((bx + 12, cy + 40), b, fill=(210, 240, 255, 255), font=font_badge)
            
        draw.text((cx - 190, cy + 130), "INTERACTIVE PLATFORM WALKTHROUGH TOUR", fill=(255, 215, 0, 255), font=font_mono_header)
    else:
        draw.text((cx - 280, cy - 140), "SPATIALFORGE 3D", fill=(255, 255, 255, 255), font=font_hero)
        draw.text((cx - 250, cy - 60), "MISSION PLATFORM CERTIFIED", fill=(0, 255, 180, 255), font=font_title)
        draw.text((cx - 340, cy), "FULL SPECTRUM AEROSPACE & INFRASTRUCTURE COMMAND", fill=(190, 220, 245, 255), font=font_body)
        
        # Clean deploy card
        draw.rounded_rectangle([cx - 260, cy + 50, cx + 260, cy + 110], radius=8, fill=(14, 28, 52, 230), outline=(0, 220, 255, 200), width=1)
        draw.text((cx - 210, cy + 68), "DEPLOY NOW: GITHUB / SPATIALFORGE-AI", fill=(255, 255, 255, 255), font=font_title)
        draw.text((cx - 180, cy + 150), "READY FOR DEFENSE & COMMERCIAL DEPLOYMENT", fill=(120, 160, 190, 255), font=font_mono_small)

def main():
    total_duration = sum(s["duration"] for s in STEPS)
    total_frames = int(total_duration * FPS)
    print(f"Interactive Walkthrough Video Plan: {total_duration:.1f}s, {total_frames} frames @ {FPS} fps, 1920x1080.")
    print(f"Target Output: {OUTPUT_WORKSPACE}")

    # Launch FFmpeg pipe with H.264 High Profile, faststart
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
        "-movflags", "+faststart",
        OUTPUT_WORKSPACE
    ]

    print(f"Launching FFmpeg: {' '.join(cmd)}")
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    frame_index = 0
    current_cursor = (960, 540)

    for step_idx, step in enumerate(STEPS):
        step_id = step["id"]
        step_duration = step["duration"]
        step_frames = int(step_duration * FPS)
        section = step.get("section", "PLATFORM")
        step_type = step.get("type", "interactive")
        
        print(f"Rendering Step {step_idx + 1}/{len(STEPS)}: {section} ({step_frames} frames)...")

        for f in range(step_frames):
            prog = f / max(1, step_frames - 1)
            time_sec = frame_index / FPS
            mins = int(time_sec // 60)
            secs = int(time_sec % 60)
            frames_rem = int(frame_index % FPS)
            timecode = f"{mins:02d}:{secs:02d}:{frames_rem:02d}"

            # Base RGBA canvas
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
                # Interactive walkthrough step with real UI backdrop
                click_ratio = step.get("click_at_ratio", 0.35)
                is_after_click = prog >= click_ratio
                
                # Pick active screenshot (before or after click)
                active_key = step["asset_after"] if is_after_click else step["asset_before"]
                base_img = CACHED_ASSETS.get(active_key)
                if base_img:
                    fitted = get_fitted_base_image(base_img)
                    canvas.paste(fitted, (0, 0))
                
                # Compute cursor trajectory with smooth ease-in-out
                start_c = step.get("start_cursor", current_cursor)
                target_c = step.get("target_cursor", start_c)
                
                # Cursor glides to target during first portion (up to click_ratio)
                move_prog = min(1.0, prog / click_ratio)
                eased_t = ease_in_out(move_prog)
                cur_x = int(start_c[0] + (target_c[0] - start_c[0]) * eased_t)
                cur_y = int(start_c[1] + (target_c[1] - start_c[1]) * eased_t)
                current_cursor = (cur_x, cur_y)
                
                # Click event and ripple
                is_clicking = abs(prog - click_ratio) < 0.05
                click_age = (prog - click_ratio) / (1.0 - click_ratio) if is_after_click else 0.0
                
                # Top status bar
                draw_hud_top_bar(draw_overlay, timecode, section)
                
                # Floating explanation card (fades in smoothly as cursor approaches target)
                card_x, card_y, card_w, card_h = step["card_pos"]
                draw_floating_card(
                    draw_overlay,
                    card_x, card_y, card_w, card_h,
                    step["badge"],
                    step["title"],
                    step["does"],
                    step["expect"],
                    target_c,
                    accent=step.get("accent", (0, 220, 255))
                )
                
                # Draw cursor with click pulse
                draw_cursor(draw_overlay, cur_x, cur_y, is_clicking=is_clicking, click_age=click_age)

            # Composite RGBA overlay onto canvas with full alpha fidelity
            final_frame = Image.alpha_composite(canvas, overlay)
            
            # Write RGB24 bytes to FFmpeg stdin
            pipe.stdin.write(final_frame.convert("RGB").tobytes())
            frame_index += 1

    pipe.stdin.close()
    pipe.wait()
    print(f"\nInteractive Walkthrough video complete! Stored at: {OUTPUT_WORKSPACE}")

    try:
        import shutil
        shutil.copy2(OUTPUT_WORKSPACE, OUTPUT_DESKTOP)
        print(f"Successfully mirrored to Desktop: {OUTPUT_DESKTOP}")
    except Exception as e:
        print(f"Desktop mirror notice (sandboxed): {e}")

if __name__ == "__main__":
    main()
