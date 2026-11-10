#!/usr/bin/env python3
"""
SpatialForge 3D - Dynamic Synchronized Master Walkthrough Video Generator
- Synchronized Subscenes: Automatically switches views, overlays, and camera angles WHILE the voiceover is speaking!
- Dynamic Feature Clicks: Cursor glides to the exact button mentioned, triggers click ripples, and shows the live UI response.
- Dual British Human Neural Voices: Alternates between Sonia (UK Female Neural) and Ryan (UK Male Neural).
- No Static Screens: 2 to 3 visual state transitions per chapter matching spoken sentences.
- Mathematically Centered UI & Zero Bottom-Space Obstruction.
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

WORKSPACE_DIR = "/Users/favl/Downloads/geospatial-evidence-replay"
PUBLIC_DIR = os.path.join(WORKSPACE_DIR, "spatialforge-ai/public")
BRAIN_DIR = "/Users/favl/.gemini/antigravity/brain/9c32895a-24a9-4867-ac3b-23972f1fc404"
AUDIO_DIR = "/tmp/spatialforge_epic_audio"
OUTPUT_WORKSPACE = os.path.join(WORKSPACE_DIR, "SpatialForge_3D_Promo_Walkthrough.mp4")
OUTPUT_PUBLIC = os.path.join(PUBLIC_DIR, "SpatialForge_3D_Promo_Walkthrough.mp4")
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

FONT_SANS = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_MONO = "/System/Library/Fonts/Menlo.ttc"

try:
    font_hero = ImageFont.truetype(FONT_SANS, 52)
    font_title = ImageFont.truetype(FONT_SANS, 22)
    font_card_head = ImageFont.truetype(FONT_SANS, 18)
    font_body = ImageFont.truetype(FONT_SANS, 13)
    font_bold = ImageFont.truetype(FONT_SANS, 13)
    font_badge = ImageFont.truetype(FONT_MONO, 12)
    font_mono_header = ImageFont.truetype(FONT_MONO, 13)
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

# Asset Library
ASSETS_CONFIG = {
    "landing_splash": "spatialforge_inception_splash.png",
    "landing_backdrop": "starship_cinematic_globe_backdrop_live.png",
    "landing_engage": "starship_clean_no_overlap_live.png",
    "console_3d": "console_screen_view.png",
    "console_crt": "spatialforge_3d_crt.png",
    "globe_tactical": "spatialforge_3d_globe_live.png",
    "stealth_intel": "redis_mesh_stealth_intel_live.png",
    "stealth_hud": "stealth_intel_hud_live.png",
    "texas_recon": "texas_capitol_recon_live.png",
    "rocket_cam": "starship_starlink_media_live.png",
    "starship_lifted": "starship_splash_tower_lifted.png",
    "mechazilla_catch": "starship_landing_page_catch_showcase.png",
    "mechazilla_clamp": "starship_mechazilla_catch_live.png",
    "earth_cam": "starship_orbital_earthcam_live.png",
    "starlink_mesh": "openrouter_all_layers_live.png",
    "redis_services": "redis_mesh_services_live.png",
    "all_layers": "all_layers_live_professional_icons.png",
    "infra_energy": "starship_infra_energy_live.png",
    "tactical_menu": "tactical_views_open.png",
    "antwerp_port": "antwerp_port_live.png",
    "antwerp_swipe": "touchless_swipe_antwerp_live.png",
    "replay_hud": "replay_hud_live.png",
    "ai_sitrep": "ai_sitrep_grid_simulation_live.png",
    "mission_recorder": "mission_recorder_dashboard_live.png",
}

print("Pre-loading high-resolution visual assets...")
LOADED_IMAGES = {}
for key, fname in ASSETS_CONFIG.items():
    fpath = os.path.join(BRAIN_DIR, fname)
    if os.path.exists(fpath):
        try:
            LOADED_IMAGES[key] = Image.open(fpath).convert("RGBA")
            print(f"  [OK] {key} ({fname}): {LOADED_IMAGES[key].size}")
        except Exception as e:
            print(f"  [ERR] {key}: {e}")
    else:
        print(f"  [MISSING] {key}: {fpath}")

# Helper to scale and crop base images to exact 1920x1080
FITTED_BASES = {}
for key, img in LOADED_IMAGES.items():
    iw, ih = img.size
    scale = max(WIDTH / iw, HEIGHT / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.BILINEAR)
    x1 = (nw - WIDTH) // 2
    y1 = (nh - HEIGHT) // 2
    FITTED_BASES[key] = resized.crop((x1, y1, x1 + WIDTH, y1 + HEIGHT))

# 12 Chapters with Dynamic Subscenes & Timed Interactions
CHAPTERS_DATA = [
    {
        "id": "ch_01",
        "audio_file": "chapter_00.wav",
        "narrator": "Ryan [UK Male Neural]",
        "section": "01 // SOVEREIGN SPATIAL FOUNDATION",
        "subscenes": [
            {
                "ratio_end": 0.35,
                "asset": "landing_splash",
                "cursor_start": (960, 800), "cursor_target": (960, 700), "click_ratio": None,
                "badge": "01 // LAUNCH EMULATION", "title": "SpaceX Starship 30s Ascent Profile",
                "function": "Simulates 33-Raptor liftoff trajectory over real-time twilight Earth backdrop.",
                "impact": "Unifies planetary digital twin with space launch kinematics.",
                "usage": "Launch ranges, spaceport mission control, and aerospace telemetry.",
                "card_pos": (640, 160, 640, 210), "accent": (0, 220, 255)
            },
            {
                "ratio_end": 0.70,
                "asset": "landing_backdrop",
                "cursor_start": (960, 700), "cursor_target": (960, 570), "click_ratio": 0.50,
                "badge": "01 // SYSTEM INITIALIZATION", "title": "Engage Sovereign Command Console",
                "function": "Initializes WebGL 3D Cesium core and restores sovereign geospatial sessions.",
                "impact": "Bridges aerospace defense and planetary topography in a single pane.",
                "usage": "Defense operations centers and aerospace commands.",
                "card_pos": (640, 230, 640, 210), "accent": (0, 240, 255)
            },
            {
                "ratio_end": 1.00,
                "asset": "landing_engage",
                "cursor_start": (960, 570), "cursor_target": (1530, 28), "click_ratio": 0.85,
                "badge": "01 // ACTIVE SESSION", "title": "Establishing Bi-Directional Pipelines",
                "function": "Streams real-time multi-source data feeds directly into Cesium 3D runtime.",
                "impact": "Zero latency data ingestion across orbital and terrestrial assets.",
                "usage": "Sovereign situational awareness centers.",
                "card_pos": (640, 230, 640, 210), "accent": (0, 255, 180)
            }
        ]
    },
    {
        "id": "ch_02",
        "audio_file": "chapter_01.wav",
        "narrator": "Sonia [UK Female Neural]",
        "section": "02 // CONSOLE ARCHITECTURE & SPATIAL AI",
        "subscenes": [
            {
                "ratio_end": 0.35,
                "asset": "console_3d",
                "cursor_start": (1530, 28), "cursor_target": (1400, 360), "click_ratio": 0.20,
                "badge": "02 // SPATIAL AI ENGINE", "title": "Unified Planetary World Model for AI",
                "function": "Delivers real-time 3D coordinate grounding and high-precision spatial physics.",
                "impact": "Eliminates AI hallucinations by grounding multimodal models in verified topography.",
                "usage": "AI research labs, autonomous systems architects, and national agencies.",
                "card_pos": (880, 75, 660, 210), "accent": (0, 255, 180)
            },
            {
                "ratio_end": 0.70,
                "asset": "console_crt",
                "cursor_start": (1400, 360), "cursor_target": (1480, 360), "click_ratio": 0.50,
                "badge": "02 // TACTICAL CRT MODE", "title": "Emerald Vector Display & Scanlines",
                "function": "Transforms photorealistic basemap into low-light tactical CRT vector graphics.",
                "impact": "Optimizes visual contrast for nighttime defense command operations.",
                "usage": "Military command bunkers and tactical surveillance stations.",
                "card_pos": (880, 75, 660, 210), "accent": (0, 240, 100)
            },
            {
                "ratio_end": 1.00,
                "asset": "globe_tactical",
                "cursor_start": (1480, 360), "cursor_target": (960, 540), "click_ratio": None,
                "badge": "02 // SUB-METER IMAGERY", "title": "Global Terrain & Bathymetry Index",
                "function": "Indexes global elevation, bathymetry, and celestial ephemeris continuously.",
                "impact": "Enables multi-domain spatial reasoning across land, sea, and orbit.",
                "usage": "Geospatial intelligence analysts and flight planners.",
                "card_pos": (880, 75, 660, 210), "accent": (0, 220, 255)
            }
        ]
    },
    {
        "id": "ch_03",
        "audio_file": "chapter_02.wav",
        "narrator": "Ryan [UK Male Neural]",
        "section": "03 // PHYSICAL AI & EMBODIED ROBOTICS",
        "subscenes": [
            {
                "ratio_end": 0.35,
                "asset": "stealth_intel",
                "cursor_start": (960, 540), "cursor_target": (1440, 360), "click_ratio": 0.20,
                "badge": "03 // PHYSICAL AI & ROBOTICS", "title": "Sub-Centimeter Digital Twins for Robotics",
                "function": "Streams 3D volumetric grids and navigation corridors to embodied robotic agents.",
                "impact": "Enables multi-robot swarm pathfinding, collision avoidance, and automated logistics.",
                "usage": "Advanced robotics manufacturers, automated gigafactories, and drone fleets.",
                "card_pos": (740, 180, 670, 210), "accent": (255, 170, 0)
            },
            {
                "ratio_end": 0.70,
                "asset": "stealth_hud",
                "cursor_start": (1440, 360), "cursor_target": (1180, 480), "click_ratio": 0.50,
                "badge": "03 // VOLUMETRIC CORRIDORS", "title": "Tesla Optimus & AGV Swarm Routing",
                "function": "Generates dynamic occupancy maps for factory automation and humanoid robots.",
                "impact": "Eliminates factory congestion and guarantees safe human-robot coexistence.",
                "usage": "Automotive manufacturing gigafactories and smart warehouses.",
                "card_pos": (740, 180, 670, 210), "accent": (255, 200, 0)
            },
            {
                "ratio_end": 1.00,
                "asset": "texas_recon",
                "cursor_start": (1180, 480), "cursor_target": (960, 540), "click_ratio": None,
                "badge": "03 // AUTONOMOUS RECON", "title": "Dynamic Geofenced Obstacle Avoidance",
                "function": "Real-time vectoring of autonomous ground vehicles and surveillance drones.",
                "impact": "Secures critical perimeters and enables touchless robotic patrols.",
                "usage": "Homeland defense facilities and private aerospace compounds.",
                "card_pos": (740, 180, 670, 210), "accent": (0, 240, 200)
            }
        ]
    },
    {
        "id": "ch_04",
        "audio_file": "chapter_03.wav",
        "narrator": "Sonia [UK Female Neural]",
        "section": "04 // SPACE OPERATIONS & MECHAZILLA CATCH",
        "subscenes": [
            {
                "ratio_end": 0.35,
                "asset": "rocket_cam",
                "cursor_start": (960, 540), "cursor_target": (1110, 360), "click_ratio": 0.15,
                "badge": "04 // SPACE OPERATIONS", "title": "Starship Launch Staging & Ascent Profile",
                "function": "Simulates 33 Raptor ascent, hot-staging at 64km, and supersonic boostback.",
                "impact": "Enables rapid launch turnaround and 90% reduction in orbital delivery cost.",
                "usage": "Commercial space operators (SpaceX, Rocket Lab, Blue Origin, ULA).",
                "card_pos": (480, 200, 670, 210), "accent": (255, 120, 0)
            },
            {
                "ratio_end": 0.70,
                "asset": "starship_lifted",
                "cursor_start": (1110, 360), "cursor_target": (330, 360), "click_ratio": 0.45,
                "badge": "04 // CHOPSTICK CATCH JUMP", "title": "Booster Aerodynamic Dive & Hover Flip",
                "function": "Triggers 4.2G deceleration trajectory towards Starbase launch tower.",
                "impact": "Eliminates ocean barge recovery and refurbishment latency entirely.",
                "usage": "Starbase launch teams and Space Force heavy-lift planners.",
                "card_pos": (370, 180, 670, 210), "accent": (255, 150, 0)
            },
            {
                "ratio_end": 1.00,
                "asset": "mechazilla_catch",
                "cursor_start": (330, 360), "cursor_target": (960, 540), "click_ratio": None,
                "badge": "04 // MECHAZILLA: PINS REST ON ARMS", "title": "The Real Tower: Booster Catch & 1-Hour Re-Fly",
                "function": "The arms close and lifting pins rest on the arms above launch mount; re-fly once an hour in principle.",
                "impact": "Eliminates barge recovery; historic breakthrough enabling rapid hourly rocket turnaround.",
                "usage": "SpaceX Starbase, NASA Artemis logistics, and orbital launch corridors.",
                "card_pos": (370, 180, 670, 210), "accent": (0, 255, 180)
            }
        ]
    },
    {
        "id": "ch_05",
        "audio_file": "chapter_04.wav",
        "narrator": "Ryan [UK Male Neural]",
        "section": "05 // MULTI-CAM FLIGHT DECK & TELEMETRY",
        "subscenes": [
            {
                "ratio_end": 0.50,
                "asset": "rocket_cam",
                "cursor_start": (960, 540), "cursor_target": (1110, 360), "click_ratio": 0.20,
                "badge": "05 // EXTERIOR ROCKETCAM", "title": "Vacuum Raptor Plume & Aero-Flap Gimbal",
                "function": "High-rate optical feed monitoring vacuum engine cooling and fin deflection.",
                "impact": "Replaces 20-second delay log parsing with instantaneous visual truth.",
                "usage": "Flight controllers, satellite deployment teams, and test range engineers.",
                "card_pos": (480, 200, 670, 210), "accent": (0, 210, 255)
            },
            {
                "ratio_end": 1.00,
                "asset": "earth_cam",
                "cursor_start": (1110, 360), "cursor_target": (1230, 360), "click_ratio": 0.65,
                "badge": "05 // ORBITAL EARTHCAM", "title": "Nadir Earth Horizon & Mach 24.8 Orbit",
                "function": "Synchronizes nadir optical camera with GPS orbital track at 182km altitude.",
                "impact": "Validates re-entry thermal shielding and orbital apogee coast visually.",
                "usage": "Orbital tracking stations and space defense mission control.",
                "card_pos": (480, 200, 670, 210), "accent": (0, 240, 255)
            }
        ]
    },
    {
        "id": "ch_06",
        "audio_file": "chapter_05.wav",
        "narrator": "Sonia [UK Female Neural]",
        "section": "06 // STARLINK LEO MESH & ORBITAL COMPUTERS",
        "subscenes": [
            {
                "ratio_end": 0.35,
                "asset": "starlink_mesh",
                "cursor_start": (1230, 360), "cursor_target": (1420, 360), "click_ratio": 0.15,
                "badge": "06 // 11,000 SATELLITES & SPACE MESH", "title": "11,000+ LEO Satellites & 10 Tbps Optical Laser Links",
                "function": "Models 11,000+ satellite constellation with 10 Tbps laser cross-links (100x speed) & AI computers in orbit.",
                "impact": "Dynamic orbital laser routing: 37% lower latency than terrestrial subsea fiber cables.",
                "usage": "Space-edge AI compute, semiconductor fabs, and sovereign defense networks.",
                "card_pos": (740, 180, 680, 210), "accent": (163, 230, 53)
            },
            {
                "ratio_end": 0.70,
                "asset": "redis_services",
                "cursor_start": (1420, 360), "cursor_target": (1520, 360), "click_ratio": 0.50,
                "badge": "06 // ORBITAL COMPUTER INFERENCE", "title": "Space-Edge GPU Tensor Array & Frequencies",
                "function": "Processes maritime SAR and dark fleet AIS on-orbit; bonds supplemental SpaceX spectrum channels.",
                "impact": "Eliminates ground station bottlenecks; feeds intelligence directly to chip fabs & power plants.",
                "usage": "Orbital AI clusters, TSMC/Intel wafer fabs, and critical energy grids.",
                "card_pos": (740, 180, 680, 210), "accent": (210, 150, 255)
            },
            {
                "ratio_end": 1.00,
                "asset": "starlink_mesh",
                "cursor_start": (1520, 360), "cursor_target": (960, 540), "click_ratio": None,
                "badge": "06 // DIRECT-TO-CELL SPECTRUM", "title": "More Channels for SpaceX & Carrier Bonding",
                "function": "Dynamically bonds 1910-1950 MHz radio frequencies for seamless cellular failover.",
                "impact": "Maintains unbroken data flow during regional grid failures, fiber cuts, or jamming.",
                "usage": "First responders, utility grid controllers, and defense communications.",
                "card_pos": (740, 180, 680, 210), "accent": (0, 255, 180)
            }
        ]
    },
    {
        "id": "ch_07",
        "audio_file": "chapter_06.wav",
        "narrator": "Ryan [UK Male Neural]",
        "section": "07 // GLOBAL TELECOM NETWORKS & SUBSEA CABLES",
        "subscenes": [
            {
                "ratio_end": 0.50,
                "asset": "all_layers",
                "cursor_start": (1520, 360), "cursor_target": (1530, 28), "click_ratio": 0.20,
                "badge": "07 // MOBILE CARRIER NETWORKS", "title": "Active Carrier Tracking in Contested Zones",
                "function": "Monitors Kyivstar, Vodafone UA, STC, Zain, and T-Mobile FirstNet coverage.",
                "impact": "Exposes regional cellular vulnerabilities during kinetic conflicts or storms.",
                "usage": "Telecommunications regulators, defense command staff, and emergency teams.",
                "card_pos": (740, 80, 680, 210), "accent": (0, 240, 200)
            },
            {
                "ratio_end": 1.00,
                "asset": "starlink_mesh",
                "cursor_start": (1530, 28), "cursor_target": (960, 540), "click_ratio": None,
                "badge": "07 // SUBSEA CABLE TRUNKS", "title": "550+ Transoceanic Fiber Backbones",
                "function": "Maps international undersea cables (2Africa, Grace Hopper) & landing stations.",
                "impact": "Enables proactive rerouting during subsea cable cuts or geopolitical sabotage.",
                "usage": "Global telecoms, international banking networks, and intelligence agencies.",
                "card_pos": (740, 80, 680, 210), "accent": (0, 200, 255)
            }
        ]
    },
    {
        "id": "ch_08",
        "audio_file": "chapter_07.wav",
        "narrator": "Sonia [UK Female Neural]",
        "section": "08 // 4,300+ DATA CENTERS & ENERGY SOURCES",
        "subscenes": [
            {
                "ratio_end": 0.50,
                "asset": "infra_energy",
                "cursor_start": (960, 540), "cursor_target": (1520, 360), "click_ratio": 0.15,
                "badge": "08 // HYPERSCALE COMPUTE", "title": "4,300+ Global Data Centers & Capacity",
                "function": "Catalogs global hyperscale compute nodes and power draw in real time.",
                "impact": "Reveals regional dependencies between AI training clusters and electric grids.",
                "usage": "Hyperscalers (AWS, Google, Azure), enterprise clouds, and grid authorities.",
                "card_pos": (720, 160, 680, 210), "accent": (255, 215, 0)
            },
            {
                "ratio_end": 1.00,
                "asset": "infra_energy",
                "cursor_start": (1520, 360), "cursor_target": (1420, 580), "click_ratio": 0.60,
                "badge": "08 // ENERGY GRID STABILITY", "title": "Frankfurt FRA1 (77.4MW) & Hydro Dams",
                "function": "Cross-references FRA1 with Dnipro (1,569MW) and Hoover Dam (2,080MW).",
                "impact": "Enables predictive workload shifting to regions with surplus clean energy.",
                "usage": "National power transmission operators and energy market traders.",
                "card_pos": (720, 160, 680, 210), "accent": (255, 180, 0)
            }
        ]
    },
    {
        "id": "ch_09",
        "audio_file": "chapter_08.wav",
        "narrator": "Ryan [UK Male Neural]",
        "section": "09 // MARITIME TRADE & SUPPLY CHAIN CHOKE POINTS",
        "subscenes": [
            {
                "ratio_end": 0.35,
                "asset": "tactical_menu",
                "cursor_start": (1420, 580), "cursor_target": (1400, 28), "click_ratio": 0.15,
                "badge": "09 // MARITIME CHOKE POINTS", "title": "Strait of Hormuz, Malacca, Suez & Panama",
                "function": "Monitors global strategic shipping straits and canal transit queues.",
                "impact": "Alerts shipping lines to geopolitical blockades and canal draft restrictions.",
                "usage": "Global container lines (Maersk, MSC), energy traders, and navies.",
                "card_pos": (700, 75, 680, 210), "accent": (0, 200, 255)
            },
            {
                "ratio_end": 0.70,
                "asset": "antwerp_port",
                "cursor_start": (1400, 28), "cursor_target": (1400, 160), "click_ratio": 0.45,
                "badge": "09 // PORT OF ANTWERP AIS", "title": "Live Container Vessel Traffic Vectors",
                "function": "Vectors satellite camera to Port of Antwerp with live vessel AIS data.",
                "impact": "Forecasts container berthing delays and detects sanction-evading dark fleets.",
                "usage": "Port authorities, customs enforcement, and supply chain logistics managers.",
                "card_pos": (700, 75, 680, 210), "accent": (0, 240, 200)
            },
            {
                "ratio_end": 1.00,
                "asset": "antwerp_swipe",
                "cursor_start": (1400, 160), "cursor_target": (960, 540), "click_ratio": None,
                "badge": "09 // COMPUTER VISION LABELS", "title": "Bounding Boxes, Draft & Speed Vectors",
                "function": "Applies computer vision bounding boxes and vessel classification tags.",
                "impact": "Automates maritime domain awareness and cargo volume surveillance.",
                "usage": "Coast guards, customs border protection, and intelligence analysts.",
                "card_pos": (700, 75, 680, 210), "accent": (0, 255, 180)
            }
        ]
    },
    {
        "id": "ch_10",
        "audio_file": "chapter_09.wav",
        "narrator": "Sonia [UK Female Neural]",
        "section": "10 // AVIATION RADAR & DRONE CORRIDORS",
        "subscenes": [
            {
                "ratio_end": 0.50,
                "asset": "replay_hud",
                "cursor_start": (960, 540), "cursor_target": (1400, 360), "click_ratio": 0.20,
                "badge": "10 // ADS-B FLIGHT RADAR", "title": "20,000+ Aircraft & Jet Stream Motion",
                "function": "Integrates real-time commercial ADS-B flights with wind and storm radar.",
                "impact": "Optimizes flight routes, saves fuel, and avoids convective turbulence.",
                "usage": "Civil aviation authorities (FAA, Eurocontrol) and major airlines.",
                "card_pos": (700, 160, 680, 210), "accent": (56, 189, 248)
            },
            {
                "ratio_end": 1.00,
                "asset": "texas_recon",
                "cursor_start": (1400, 360), "cursor_target": (960, 540), "click_ratio": 0.65,
                "badge": "10 // LOW-ALTITUDE UAV CORRIDORS", "title": "Texas State Capitol Geofenced Drone Paths",
                "function": "Defines 3D low-altitude urban air mobility corridors for autonomous delivery.",
                "impact": "Maintains zero-collision airspace between commercial drones and buildings.",
                "usage": "Urban air mobility operators, delivery fleets, and public safety teams.",
                "card_pos": (700, 160, 680, 210), "accent": (0, 240, 200)
            }
        ]
    },
    {
        "id": "ch_11",
        "audio_file": "chapter_10.wav",
        "narrator": "Ryan [UK Male Neural]",
        "section": "11 // AUTONOMOUS AI SITREP & 110kV BLACKOUT TEST",
        "subscenes": [
            {
                "ratio_end": 0.45,
                "asset": "ai_sitrep",
                "cursor_start": (960, 540), "cursor_target": (1540, 480), "click_ratio": 0.15,
                "badge": "11 // AUTONOMOUS AI SITREP", "title": "Neural Sensor Matrix Intelligence Fusion",
                "function": "Fuses satellite orbits, power grids, and mobile networks into a military SITREP.",
                "impact": "Eliminates cognitive overload during crisis events by synthesizing telemetry.",
                "usage": "Emergency operations centers, military commands, and infrastructure execs.",
                "card_pos": (620, 140, 680, 210), "accent": (0, 255, 170)
            },
            {
                "ratio_end": 1.00,
                "asset": "ai_sitrep",
                "cursor_start": (1540, 480), "cursor_target": (1540, 560), "click_ratio": 0.60,
                "badge": "11 // 110kV BLACKOUT FAILOVER", "title": "Simulated Grid Collapse & Starlink Diversion",
                "function": "Simulates complete power substation outage and triggers autonomous LEO failover.",
                "impact": "Guarantees 48h emergency UPS battery reserves and 100% cellular survival.",
                "usage": "Homeland security, hospitals, Tier IV data centers, and defense commands.",
                "card_pos": (620, 140, 680, 210), "accent": (255, 75, 75)
            }
        ]
    },
    {
        "id": "ch_12",
        "audio_file": "chapter_11.wav",
        "narrator": "Sonia [UK Female Neural]",
        "section": "12 // MISSION PLATFORM CERTIFIED",
        "subscenes": [
            {
                "ratio_end": 0.45,
                "asset": "mission_recorder",
                "cursor_start": (1540, 560), "cursor_target": (1180, 480), "click_ratio": 0.15,
                "badge": "12 // AIR-GAPPED DEPLOYMENT", "title": "Touchless Gesture Replay & Mission Recorder",
                "function": "Records and replays full spatial missions in secure air-gapped environments.",
                "impact": "Guarantees zero data exfiltration for defense and classified operations.",
                "usage": "Sovereign defense ministries, space agencies, and intelligence facilities.",
                "card_pos": (620, 140, 680, 210), "accent": (0, 220, 255)
            },
            {
                "ratio_end": 1.00,
                "asset": None,  # Outro Brand Card
                "cursor_start": (1180, 480), "cursor_target": (960, 540), "click_ratio": None,
                "badge": "12 // PLATFORM READY", "title": "SpatialForge 3D // Sovereign Spatial Intelligence",
                "function": "Mission platform certified for enterprise, defense, and aerospace deployment.",
                "impact": "Full spectrum planetary dominance across space, ground, sea, and cyber domains.",
                "usage": "Deploy now: GitHub / SpatialForge-AI.",
                "card_pos": None, "accent": (0, 255, 180)
            }
        ]
    }
]

def ease_in_out(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        f = (2 * t) - 2
        return 0.5 * f * f * f + 1

def draw_centered_text(draw, y, text, font, fill):
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    x = (WIDTH - text_w) // 2
    draw.text((x, y), text, fill=fill, font=font)
    return text_w, bbox[3] - bbox[1]

def draw_centered_button(draw, y, text, font, fill_btn, outline_btn, fill_text, pad_x=36, pad_y=16):
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
        radius = int(8 + click_age * 30)
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
    tx, ty = target_pt
    anchor_x = max(card_x, min(card_x + card_w, tx))
    anchor_y = card_y + card_h if ty > card_y + card_h else card_y
    draw.line([(anchor_x, anchor_y), (tx, ty)], fill=(accent[0], accent[1], accent[2], 140), width=1)
    draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=accent)

    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=8, fill=(8, 16, 28, 238), outline=(accent[0], accent[1], accent[2], 180), width=1)
    draw.rounded_rectangle([card_x, card_y, card_x + 5, card_y + card_h], radius=2, fill=accent)

    bw = len(badge_text) * 8 + 16
    draw.rounded_rectangle([card_x + 16, card_y + 12, card_x + 16 + bw, card_y + 32], radius=4, fill=(accent[0], accent[1], accent[2], 40), outline=accent, width=1)
    draw.text((card_x + 24, card_y + 15), badge_text, fill=accent, font=font_badge)

    draw.text((card_x + 16, card_y + 40), title, fill=(255, 255, 255, 255), font=font_card_head)

    y_c = card_y + 72
    draw.text((card_x + 16, y_c), "FUNCTION:     ", fill=(130, 180, 220, 255), font=font_bold)
    draw.text((card_x + 115, y_c), function_text[:72], fill=(225, 235, 245, 255), font=font_body)
    if len(function_text) > 72:
        y_c += 18
        draw.text((card_x + 115, y_c), function_text[72:144], fill=(225, 235, 245, 255), font=font_body)

    y_c += 24
    draw.text((card_x + 16, y_c), "WHY & IMPACT: ", fill=(0, 255, 180, 255), font=font_bold)
    draw.text((card_x + 115, y_c), impact_text[:72], fill=(160, 255, 220, 255), font=font_body)
    if len(impact_text) > 72:
        y_c += 18
        draw.text((card_x + 115, y_c), impact_text[72:144], fill=(160, 255, 220, 255), font=font_body)

    y_c += 24
    draw.text((card_x + 16, y_c), "REAL USAGE:   ", fill=(255, 215, 0, 255), font=font_bold)
    draw.text((card_x + 115, y_c), usage_text[:72], fill=(255, 240, 180, 255), font=font_body)
    if len(usage_text) > 72:
        y_c += 18
        draw.text((card_x + 115, y_c), usage_text[72:144], fill=(255, 240, 180, 255), font=font_body)

def draw_hud_top_bar(draw, timecode, section_name, narrator):
    draw.rectangle([0, 0, WIDTH, 36], fill=(6, 12, 22, 220))
    draw.line([0, 36, WIDTH, 36], fill=(0, 200, 255, 90), width=1)
    draw.ellipse([20, 13, 30, 23], fill=(255, 50, 50, 255))
    draw.text((38, 10), f"MASTER TUTORIAL  [● {timecode}]", fill=(255, 255, 255, 255), font=font_mono_header)
    draw.text((450, 10), "SPATIALFORGE 3D // SOVEREIGN SPATIAL PLATFORM", fill=(0, 210, 255, 255), font=font_mono_header)
    draw.text((WIDTH - 540, 10), f"DOMAIN: {section_name.upper()}", fill=(255, 215, 0, 255), font=font_mono_header)
    draw.text((WIDTH - 200, 10), narrator, fill=(160, 220, 255, 255), font=font_mono_header)

def render_brand_card(draw, is_intro=True):
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(6, 12, 22, 255))
    for x in range(0, WIDTH, 96):
        draw.line([x, 0, x, HEIGHT], fill=(20, 40, 65, 80), width=1)
    for y in range(0, HEIGHT, 96):
        draw.line([0, y, WIDTH, y], fill=(20, 40, 65, 80), width=1)
    cy = HEIGHT // 2

    if is_intro:
        draw_centered_text(draw, cy - 140, "SPATIALFORGE 3D", font_hero, (255, 255, 255, 255))
        draw_centered_text(draw, cy - 60, "SOVEREIGN SPATIAL INTELLIGENCE & SATELLITE COMMAND", font_title, (0, 220, 255, 255))
        draw_centered_text(draw, cy - 15, "MULTI-DOMAIN MASTER TUTORIAL // SPACE • AI • INFRASTRUCTURE • DEFENSE", font_body, (190, 220, 245, 255))
        badges = ["CESIUM 3D CORE", "STARSHIP & STARLINK", "PHYSICAL ROBOTICS AI", "4,300+ DATA CENTERS", "AI SITREP ENGINE"]
        total_w = len(badges) * 190
        start_x = (WIDTH - total_w) // 2
        for i, b in enumerate(badges):
            bx = start_x + i * 190
            draw.rounded_rectangle([bx, cy + 30, bx + 175, cy + 64], radius=4, fill=(12, 28, 48, 220), outline=(0, 200, 255, 180), width=1)
            draw.text((bx + 12, cy + 40), b, fill=(210, 240, 255, 255), font=font_badge)
        draw_centered_text(draw, cy + 130, "DUAL UK HUMAN NEURAL NARRATION (SONIA & RYAN) • SYNCHRONIZED WALKTHROUGH", font_mono_header, (255, 215, 0, 255))
    else:
        # OUTRO CARD: 100% mathematically centered
        draw_centered_text(draw, cy - 150, "SPATIALFORGE 3D", font_hero, (255, 255, 255, 255))
        draw_centered_text(draw, cy - 70, "MISSION PLATFORM CERTIFIED", font_title, (0, 255, 180, 255))
        draw_centered_text(draw, cy - 20, "FULL SPECTRUM AEROSPACE & INFRASTRUCTURE COMMAND", font_body, (190, 220, 245, 255))
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
    # Read duration of each cached audio file
    print("\nReading exact audio durations for all 12 chapters...")
    total_audio_time = 0.0
    for ch in CHAPTERS_DATA:
        wav_path = os.path.join(AUDIO_DIR, ch["audio_file"])
        cmd_probe = [
            "/opt/homebrew/bin/ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            wav_path
        ]
        out = subprocess.check_output(cmd_probe).decode().strip()
        dur = float(out)
        ch["duration"] = dur
        total_audio_time += dur
        print(f"  [{ch['id']}] {ch['section']}: {dur:.2f}s")

    total_frames = int(total_audio_time * FPS)
    print(f"\nTotal Synchronized Master Video: {total_audio_time/60:.2f} mins ({total_audio_time:.1f}s, {total_frames} frames @ {FPS} fps)...")

    raw_video_path = os.path.join(AUDIO_DIR, "dynamic_raw_video.mp4")

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
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        raw_video_path
    ]

    print(f"Launching FFmpeg: {' '.join(cmd)}")
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    frame_index = 0
    current_cursor = (960, 540)

    for ch_idx, ch in enumerate(CHAPTERS_DATA):
        ch_duration = ch["duration"]
        ch_frames = int(ch_duration * FPS)
        section = ch["section"]
        narrator = ch["narrator"]
        subscenes = ch["subscenes"]

        print(f"Rendering Chapter {ch_idx + 1}/12: {section} ({len(subscenes)} subscenes, {ch_duration:.1f}s, {ch_frames} frames)...")

        for f in range(ch_frames):
            prog = f / max(1, ch_frames - 1)
            time_sec = frame_index / FPS
            mins = int(time_sec // 60)
            secs = int(time_sec % 60)
            timecode = f"{mins:02d}:{secs:02d}"

            # Determine active subscene based on progression ratio
            active_sub = None
            prev_ratio = 0.0
            for sub in subscenes:
                if prog <= sub["ratio_end"]:
                    active_sub = sub
                    break
                prev_ratio = sub["ratio_end"]
            if not active_sub:
                active_sub = subscenes[-1]

            # Progression inside current subscene
            sub_len = active_sub["ratio_end"] - prev_ratio
            sub_prog = (prog - prev_ratio) / max(0.001, sub_len)

            # Base canvas selection
            asset_key = active_sub.get("asset")
            if asset_key and asset_key in FITTED_BASES:
                base_canvas = FITTED_BASES[asset_key]
            else:
                base_canvas = Image.new("RGBA", (WIDTH, HEIGHT), (6, 12, 22, 255))
                render_brand_card(ImageDraw.Draw(base_canvas), is_intro=False)

            # Overlay for cursor, HUD bar, and floating explanation cards
            frame_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(frame_overlay)

            draw_hud_top_bar(draw_ov, timecode, section, narrator)

            # Cursor motion and click within subscene
            start_c = active_sub.get("cursor_start", current_cursor)
            target_c = active_sub.get("cursor_target", start_c)
            click_r = active_sub.get("click_ratio")

            move_ratio = click_r if click_r else 0.50
            move_p = min(1.0, sub_prog / move_ratio)
            eased_t = ease_in_out(move_p)
            cur_x = int(start_c[0] + (target_c[0] - start_c[0]) * eased_t)
            cur_y = int(start_c[1] + (target_c[1] - start_c[1]) * eased_t)
            current_cursor = (cur_x, cur_y)

            is_clicking = click_r and abs(sub_prog - click_r) < 0.06
            click_age = (sub_prog - click_r) / (1.0 - click_r) if (click_r and sub_prog >= click_r) else 0.0

            card_pos = active_sub.get("card_pos")
            if card_pos:
                cx, cy, cw, ch_h = card_pos
                draw_floating_card(
                    draw_ov, cx, cy, cw, ch_h,
                    active_sub["badge"], active_sub["title"],
                    active_sub["function"], active_sub["impact"], active_sub["usage"],
                    target_c,
                    accent=active_sub.get("accent", (0, 220, 255))
                )

            if asset_key is not None:
                draw_cursor(draw_ov, cur_x, cur_y, is_clicking=is_clicking, click_age=click_age)

            final_frame = Image.alpha_composite(base_canvas, frame_overlay)
            pipe.stdin.write(final_frame.convert("RGB").tobytes())
            frame_index += 1

    pipe.stdin.close()
    pipe.wait()
    print("Raw video render complete!")

    # Mux final video and master audio track
    print("\nMuxing synchronized dynamic video with master audio track...")
    final_audio_path = os.path.join(AUDIO_DIR, "final_epic_master_audio.m4a")
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
    print(f"Master Video ready at: {OUTPUT_WORKSPACE}")

    import shutil
    shutil.copy2(OUTPUT_WORKSPACE, OUTPUT_PUBLIC)
    print(f"Public asset mirrored: {OUTPUT_PUBLIC}")

if __name__ == "__main__":
    main()

