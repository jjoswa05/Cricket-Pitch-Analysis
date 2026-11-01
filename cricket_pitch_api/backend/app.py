from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
from PIL import Image
import io
import cv2
import numpy as np


# =========================================================
# 1. CREATE FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Cricket Pitch Analysis API",
    description="YOLOv8 based Cricket Pitch Analysis with Bowling Recommendation",
    version="1.0"
)


# =========================================================
# 2. LOAD TRAINED YOLOv8 MODEL
# =========================================================

model = YOLO("best.pt")


# =========================================================
# 3. PITCH FEATURE ANALYSIS
# =========================================================

def analyze_pitch(pitch_image):

    # Convert PIL image to OpenCV format
    image = np.array(pitch_image)

    # RGB → BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Resize for consistent analysis
    image = cv2.resize(image, (500, 500))

    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # -----------------------------------------------------
    # FEATURE 1: GREEN / GRASS RATIO
    # -----------------------------------------------------

    lower_green = np.array([30, 30, 30])
    upper_green = np.array([100, 255, 255])

    green_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    grass_ratio = (
        np.sum(green_mask > 0)
        / green_mask.size
    )

    grass_score = grass_ratio * 100


    # -----------------------------------------------------
    # FEATURE 2: DRYNESS
    # -----------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    average_brightness = np.mean(gray)

    dryness_score = np.clip(
        (average_brightness - 70) / 180 * 100,
        0,
        100
    )


    # -----------------------------------------------------
    # FEATURE 3: ROUGHNESS / TEXTURE
    # -----------------------------------------------------

    texture_score = np.std(gray)

    roughness_score = np.clip(
        texture_score / 80 * 100,
        0,
        100
    )


    # -----------------------------------------------------
    # FEATURE 4: CRACK PROXY
    # -----------------------------------------------------

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    edge_ratio = (
        np.sum(edges > 0)
        / edges.size
    )

    crack_score = np.clip(
        edge_ratio * 500,
        0,
        100
    )


    # -----------------------------------------------------
    # FEATURE 5: MOISTURE PROXY
    # -----------------------------------------------------

    # Dark-pixel ratio is only a visual proxy.
    # It is NOT actual moisture measurement.

    dark_pixels = gray < 80

    dark_ratio = (
        np.sum(dark_pixels)
        / dark_pixels.size
    )

    moisture_proxy = np.clip(
        dark_ratio * 200,
        0,
        100
    )


    # =====================================================
    # BOWLING RECOMMENDATION
    # =====================================================

    pace_score = 0
    seam_score = 0
    spin_score = 0


    # -----------------------------------------------------
    # PACE RULES
    # -----------------------------------------------------

    if dryness_score >= 60:
        pace_score += 30

    if roughness_score < 40:
        pace_score += 25

    if grass_score < 30:
        pace_score += 20


    # -----------------------------------------------------
    # SEAM RULES
    # -----------------------------------------------------

    if grass_score >= 35:
        seam_score += 40

    if moisture_proxy >= 30:
        seam_score += 30

    if roughness_score >= 20:
        seam_score += 10


    # -----------------------------------------------------
    # SPIN RULES
    # -----------------------------------------------------

    if dryness_score >= 55:
        spin_score += 25

    if roughness_score >= 50:
        spin_score += 35

    if crack_score >= 35:
        spin_score += 30

    if grass_score < 25:
        spin_score += 10


    # -----------------------------------------------------
    # DETERMINE FINAL RECOMMENDATION
    # -----------------------------------------------------

    scores = {
        "Pace": pace_score,
        "Seam": seam_score,
        "Spin": spin_score
    }

    recommendation = max(
        scores,
        key=scores.get
    )


    # =====================================================
    # RETURN ANALYSIS
    # =====================================================

    return {
        "grass_score": round(grass_score, 2),
        "dryness_score": round(dryness_score, 2),
        "roughness_score": round(roughness_score, 2),
        "crack_score": round(crack_score, 2),
        "moisture_proxy": round(moisture_proxy, 2),

        "bowling_scores": {
            "pace": pace_score,
            "seam": seam_score,
            "spin": spin_score
        },

        "recommendation": recommendation
    }


# =========================================================
# 4. HOME ENDPOINT
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Cricket Pitch Analysis API is running",
        "model": "YOLOv8"
    }


# =========================================================
# 5. PREDICTION ENDPOINT
# =========================================================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # -----------------------------------------------------
    # Read uploaded image
    # -----------------------------------------------------

    image_bytes = await file.read()

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")


    # -----------------------------------------------------
    # YOLOv8 prediction
    # -----------------------------------------------------

    results = model.predict(
        source=image,
        conf=0.25
    )


    predictions = []

    recommendation = None
    pitch_analysis = None


    # -----------------------------------------------------
    # Process YOLO detections
    # -----------------------------------------------------

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])

            confidence = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()


            # -------------------------------------------------
            # Save detection
            # -------------------------------------------------

            predictions.append({

                "class_id": class_id,

                "class_name": model.names[class_id],

                "confidence": round(
                    confidence,
                    4
                ),

                "bounding_box": {

                    "x1": round(x1, 2),

                    "y1": round(y1, 2),

                    "x2": round(x2, 2),

                    "y2": round(y2, 2)
                }
            })


            # -------------------------------------------------
            # CROP DETECTED PITCH
            # -------------------------------------------------

            image_width, image_height = image.size

            x1 = max(0, int(x1))
            y1 = max(0, int(y1))

            x2 = min(image_width, int(x2))
            y2 = min(image_height, int(y2))


            pitch_crop = image.crop(
                (x1, y1, x2, y2)
            )


            # -------------------------------------------------
            # ANALYZE PITCH
            # -------------------------------------------------

            pitch_analysis = analyze_pitch(
                pitch_crop
            )

            recommendation = (
                pitch_analysis["recommendation"]
            )


    # =====================================================
    # FINAL API RESPONSE
    # =====================================================

    return {

        "filename": file.filename,

        "detections": predictions,

        "pitch_analysis": pitch_analysis,

        "bowling_recommendation": recommendation
    }