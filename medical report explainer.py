import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import fitz
import easyocr
import numpy as np
from PIL import Image
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# =========================================================
# EASY OCR
# =========================================================

print("Loading EasyOCR...")
print("Please wait...")

reader = easyocr.Reader(
    ['en'],
    gpu=False,
    verbose=False
)

print("EasyOCR loaded successfully!")


# =========================================================
# GLOBAL VARIABLES
# =========================================================

extracted_text = ""
medical_info = {}
explanation = {}
clinical_result = {}


# =========================================================
# OCR AND TEXT EXTRACTION
# =========================================================

def extract_text(file_path):

    text = ""

    # -----------------------------------------------------
    # PDF FILE
    # -----------------------------------------------------

    if file_path.lower().endswith(".pdf"):

        document = fitz.open(file_path)

        for page in document:

            # Try normal PDF text extraction
            page_text = page.get_text()

            if page_text.strip():

                text += page_text + "\n"

            else:

                # Scanned PDF - use EasyOCR
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                # Convert image to NumPy array
                image_array = np.array(image)

                # EasyOCR
                result = reader.readtext(
                    image_array,
                    detail=0
                )

                text += "\n".join(result) + "\n"

        document.close()

    # -----------------------------------------------------
    # IMAGE FILE
    # -----------------------------------------------------

    else:

        image = Image.open(file_path)

        # Convert image to RGB
        image = image.convert("RGB")

        # Convert image to NumPy array
        image_array = np.array(image)

        # EasyOCR
        result = reader.readtext(
            image_array,
            detail=0
        )

        text = "\n".join(result)

    return text


# =========================================================
# MEDICAL INFORMATION EXTRACTION
# =========================================================

def extract_medical_information(text):

    text_lower = text.lower()

    # -----------------------------------------------------
    # SYMPTOMS
    # -----------------------------------------------------

    symptoms_list = [
        "fever",
        "cough",
        "headache",
        "fatigue",
        "pain",
        "nausea",
        "vomiting",
        "dizziness",
        "shortness of breath"
    ]

    # -----------------------------------------------------
    # MEDICAL TESTS
    # -----------------------------------------------------

    tests_list = [
        "blood test",
        "cbc",
        "hemoglobin",
        "glucose",
        "cholesterol",
        "blood pressure",
        "x-ray",
        "mri",
        "ct scan"
    ]

    # -----------------------------------------------------
    # FIND SYMPTOMS
    # -----------------------------------------------------

    symptoms = []

    for item in symptoms_list:

        if item in text_lower:

            symptoms.append(item)

    # -----------------------------------------------------
    # FIND TESTS
    # -----------------------------------------------------

    tests = []

    for item in tests_list:

        if item in text_lower:

            tests.append(item)

    # -----------------------------------------------------
    # FIND NUMERIC VALUES
    # -----------------------------------------------------

    values = re.findall(
        r'\b\d+(?:\.\d+)?\s*(?:mg/dL|g/dL|mmHg|°C|%)?\b',
        text
    )

    # -----------------------------------------------------
    # FIND OBSERVATIONS
    # -----------------------------------------------------

    observations = []

    keywords = [
        "high",
        "low",
        "normal",
        "abnormal",
        "elevated",
        "reduced"
    ]

    for word in keywords:

        if word in text_lower:

            observations.append(word)

    return {
        "symptoms": symptoms,
        "tests": tests,
        "values": values,
        "observations": observations
    }


# =========================================================
# PATIENT-FRIENDLY EXPLANATION
# =========================================================

def generate_explanation(info):

    symptoms = info.get(
        "symptoms",
        []
    )

    tests = info.get(
        "tests",
        []
    )

    values = info.get(
        "values",
        []
    )

    observations = info.get(
        "observations",
        []
    )

    summary = ""

    # -----------------------------------------------------
    # SYMPTOM SUMMARY
    # -----------------------------------------------------

    if symptoms:

        summary += (
            "The report mentions these symptoms: "
            + ", ".join(symptoms)
            + ".\n\n"
        )

    # -----------------------------------------------------
    # TEST SUMMARY
    # -----------------------------------------------------

    if tests:

        summary += (
            "The report mentions these medical tests: "
            + ", ".join(tests)
            + ".\n\n"
        )

    # -----------------------------------------------------
    # OBSERVATION SUMMARY
    # -----------------------------------------------------

    if observations:

        summary += (
            "The report contains these observations: "
            + ", ".join(observations)
            + ".\n\n"
        )

    # -----------------------------------------------------
    # NO INFORMATION
    # -----------------------------------------------------

    if not summary:

        summary = (
            "The system could not identify enough medical "
            "information from the report."
        )

    # -----------------------------------------------------
    # GENERAL HEALTH INFORMATION
    # -----------------------------------------------------

    health_information = [

        "Review abnormal findings with a qualified healthcare professional.",

        "Keep the original medical report for clinical reference.",

        "Do not make treatment decisions using only this automated summary."

    ]

    return {

        "summary": summary,

        "values": values,

        "health_information": health_information

    }


# =========================================================
# CLINICAL DECISION SUPPORT
# =========================================================

def clinical_analysis(info):

    risk_flags = []

    possible_conditions = []

    follow_up = []

    observations = info.get(
        "observations",
        []
    )

    symptoms = info.get(
        "symptoms",
        []
    )

    # -----------------------------------------------------
    # HIGH VALUE
    # -----------------------------------------------------

    if "high" in observations:

        risk_flags.append(
            "The report mentions one or more high values."
        )

        follow_up.append(
            "Review the specific high value with a healthcare professional."
        )

    # -----------------------------------------------------
    # LOW VALUE
    # -----------------------------------------------------

    if "low" in observations:

        risk_flags.append(
            "The report mentions one or more low values."
        )

        follow_up.append(
            "Review the specific low value with a healthcare professional."
        )

    # -----------------------------------------------------
    # ABNORMAL VALUE
    # -----------------------------------------------------

    if "abnormal" in observations:

        risk_flags.append(
            "The report contains an abnormal finding."
        )

        follow_up.append(
            "Discuss the abnormal finding with a healthcare professional."
        )

    # -----------------------------------------------------
    # FEVER
    # -----------------------------------------------------

    if "fever" in symptoms:

        possible_conditions.append(
            "Fever-related causes require clinical evaluation."
        )

    # -----------------------------------------------------
    # COUGH
    # -----------------------------------------------------

    if "cough" in symptoms:

        possible_conditions.append(
            "Respiratory symptoms may require clinical assessment."
        )

    # -----------------------------------------------------
    # SHORTNESS OF BREATH
    # -----------------------------------------------------

    if "shortness of breath" in symptoms:

        risk_flags.append(
            "Shortness of breath may require prompt medical assessment."
        )

    return {

        "risk_flags": risk_flags,

        "possible_conditions": possible_conditions,

        "follow_up": follow_up

    }


# =========================================================
# UPLOAD FILE
# =========================================================

def upload_report():

    global extracted_text
    global medical_info
    global explanation
    global clinical_result

    file_path = filedialog.askopenfilename(

        title="Select Medical Report",

        filetypes=[

            (
                "Medical Reports",
                "*.pdf *.png *.jpg *.jpeg"
            ),

            (
                "PDF Files",
                "*.pdf"
            ),

            (
                "Image Files",
                "*.png *.jpg *.jpeg"
            )

        ]
    )

    if not file_path:

        return

    try:

        # -------------------------------------------------
        # EXTRACT TEXT
        # -------------------------------------------------

        extracted_text = extract_text(
            file_path
        )

        # -------------------------------------------------
        # EXTRACT MEDICAL INFORMATION
        # -------------------------------------------------

        medical_info = extract_medical_information(
            extracted_text
        )

        # -------------------------------------------------
        # GENERATE EXPLANATION
        # -------------------------------------------------

        explanation = generate_explanation(
            medical_info
        )

        # -------------------------------------------------
        # CLINICAL SUPPORT
        # -------------------------------------------------

        clinical_result = clinical_analysis(
            medical_info
        )

        # -------------------------------------------------
        # DISPLAY EXTRACTED TEXT
        # -------------------------------------------------

        text_box.delete(
            "1.0",
            tk.END
        )

        text_box.insert(
            tk.END,
            extracted_text
        )

        messagebox.showinfo(
            "Success",
            "Medical report processed successfully using EasyOCR!"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )


# =========================================================
# SHOW MEDICAL INFORMATION
# =========================================================

def show_medical_information():

    if not medical_info:

        messagebox.showinfo(
            "Information",
            "Please upload a medical report first."
        )

        return

    text_box.delete(
        "1.0",
        tk.END
    )

    text_box.insert(
        tk.END,
        "EXTRACTED MEDICAL INFORMATION\n"
    )

    text_box.insert(
        tk.END,
        "================================\n\n"
    )

    # -----------------------------------------------------
    # SYMPTOMS
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "SYMPTOMS\n"
    )

    if medical_info["symptoms"]:

        for item in medical_info["symptoms"]:

            text_box.insert(
                tk.END,
                "• " + item + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "• None detected\n"
        )

    # -----------------------------------------------------
    # TESTS
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "\nTESTS\n"
    )

    if medical_info["tests"]:

        for item in medical_info["tests"]:

            text_box.insert(
                tk.END,
                "• " + item + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "• None detected\n"
        )

    # -----------------------------------------------------
    # VALUES
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "\nVALUES\n"
    )

    if medical_info["values"]:

        for item in medical_info["values"]:

            text_box.insert(
                tk.END,
                "• " + item + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "• None detected\n"
        )

    # -----------------------------------------------------
    # OBSERVATIONS
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "\nOBSERVATIONS\n"
    )

    if medical_info["observations"]:

        for item in medical_info["observations"]:

            text_box.insert(
                tk.END,
                "• " + item + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "• None detected\n"
        )


# =========================================================
# SHOW PATIENT EXPLANATION
# =========================================================

def show_explanation():

    if not explanation:

        messagebox.showinfo(
            "Information",
            "Please upload a medical report first."
        )

        return

    text_box.delete(
        "1.0",
        tk.END
    )

    text_box.insert(
        tk.END,
        "PATIENT-FRIENDLY EXPLANATION\n"
    )

    text_box.insert(
        tk.END,
        "================================\n\n"
    )

    text_box.insert(
        tk.END,
        explanation["summary"]
    )

    # -----------------------------------------------------
    # IMPORTANT VALUES
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "\n\nIMPORTANT VALUES\n"
    )

    if explanation["values"]:

        for value in explanation["values"]:

            text_box.insert(
                tk.END,
                "• " + value + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "• None detected\n"
        )

    # -----------------------------------------------------
    # HEALTH INFORMATION
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "\nGENERAL HEALTH INFORMATION\n"
    )

    for item in explanation["health_information"]:

        text_box.insert(
            tk.END,
            "• " + item + "\n"
        )


# =========================================================
# SHOW CLINICAL SUPPORT
# =========================================================

def show_clinical_support():

    if not clinical_result:

        messagebox.showinfo(
            "Information",
            "Please upload a medical report first."
        )

        return

    text_box.delete(
        "1.0",
        tk.END
    )

    text_box.insert(
        tk.END,
        "CLINICAL DECISION SUPPORT\n"
    )

    text_box.insert(
        tk.END,
        "================================\n\n"
    )

    # -----------------------------------------------------
    # RISK FLAGS
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "RISK FLAGS\n"
    )

    if clinical_result["risk_flags"]:

        for risk in clinical_result["risk_flags"]:

            text_box.insert(
                tk.END,
                "WARNING: " + risk + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "No automated risk flags detected.\n"
        )

    # -----------------------------------------------------
    # POSSIBLE AREAS
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "\nPOSSIBLE AREAS REQUIRING ATTENTION\n"
    )

    if clinical_result["possible_conditions"]:

        for item in clinical_result[
            "possible_conditions"
        ]:

            text_box.insert(
                tk.END,
                "• " + item + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "• No specific area detected.\n"
        )

    # -----------------------------------------------------
    # FOLLOW-UP
    # -----------------------------------------------------

    text_box.insert(
        tk.END,
        "\nSUGGESTED FOLLOW-UP\n"
    )

    if clinical_result["follow_up"]:

        for item in clinical_result[
            "follow_up"
        ]:

            text_box.insert(
                tk.END,
                "• " + item + "\n"
            )

    else:

        text_box.insert(
            tk.END,
            "• Routine professional review is recommended.\n"
        )


# =========================================================
# GENERATE PDF REPORT
# =========================================================

def generate_pdf():

    if not medical_info:

        messagebox.showinfo(
            "Information",
            "Please upload a report first."
        )

        return

    file_path = filedialog.asksaveasfilename(

        title="Save Medical Report",

        defaultextension=".pdf",

        filetypes=[
            (
                "PDF Files",
                "*.pdf"
            )
        ]
    )

    if not file_path:

        return

    document = SimpleDocTemplate(

        file_path,

        pagesize=A4
    )

    styles = getSampleStyleSheet()

    content = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    content.append(

        Paragraph(
            "Generative AI-Enabled Medical Report Explainer",
            styles["Title"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    # -----------------------------------------------------
    # PATIENT-FRIENDLY SUMMARY
    # -----------------------------------------------------

    content.append(

        Paragraph(
            "Patient-Friendly Summary",
            styles["Heading2"]
        )
    )

    summary_text = explanation[
        "summary"
    ].replace(
        "\n",
        "<br/>"
    )

    content.append(

        Paragraph(
            summary_text,
            styles["BodyText"]
        )
    )

    content.append(
        Spacer(1, 15)
    )

    # -----------------------------------------------------
    # MEDICAL INFORMATION
    # -----------------------------------------------------

    content.append(

        Paragraph(
            "Extracted Medical Information",
            styles["Heading2"]
        )
    )

    for category, values in medical_info.items():

        content.append(

            Paragraph(
                category.title(),
                styles["Heading3"]
            )
        )

        if values:

            for value in values:

                content.append(

                    Paragraph(
                        "• " + str(value),
                        styles["BodyText"]
                    )
                )

        else:

            content.append(

                Paragraph(
                    "• None detected",
                    styles["BodyText"]
                )
            )

    content.append(
        Spacer(1, 15)
    )

    # -----------------------------------------------------
    # RISK ASSESSMENT
    # -----------------------------------------------------

    content.append(

        Paragraph(
            "Risk Assessment",
            styles["Heading2"]
        )
    )

    if clinical_result["risk_flags"]:

        for risk in clinical_result[
            "risk_flags"
        ]:

            content.append(

                Paragraph(
                    "• " + risk,
                    styles["BodyText"]
                )
            )

    else:

        content.append(

            Paragraph(
                "• No automated risk flags detected.",
                styles["BodyText"]
            )
        )

    content.append(
        Spacer(1, 15)
    )

    # -----------------------------------------------------
    # SUGGESTED FOLLOW-UP
    # -----------------------------------------------------

    content.append(

        Paragraph(
            "Suggested Follow-up",
            styles["Heading2"]
        )
    )

    if clinical_result["follow_up"]:

        for item in clinical_result[
            "follow_up"
        ]:

            content.append(

                Paragraph(
                    "• " + item,
                    styles["BodyText"]
                )
            )

    else:

        content.append(

            Paragraph(
                "• Professional review of the complete report is recommended.",
                styles["BodyText"]
            )
        )

    content.append(
        Spacer(1, 20)
    )

    # -----------------------------------------------------
    # DISCLAIMER
    # -----------------------------------------------------

    content.append(

        Paragraph(
            "<b>Disclaimer:</b> This is an educational software prototype. "
            "It is not a medical diagnosis system and should not replace "
            "professional medical advice.",
            styles["BodyText"]
        )
    )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    document.build(
        content
    )

    messagebox.showinfo(
        "Success",
        "PDF report created successfully!"
    )


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title(
    "Medical Report Explainer"
)

window.geometry(
    "1100x700"
)

window.configure(
    bg="#F4F7FB"
)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(

    window,

    text="Generative AI-Enabled Multimodal Medical Report Explainer",

    font=("Arial", 20, "bold"),

    bg="#F4F7FB"
)

title.pack(
    pady=15
)


# =========================================================
# SUBTITLE
# =========================================================

subtitle = tk.Label(

    window,

    text="AI-Assisted Medical Report Understanding System",

    font=("Arial", 11),

    bg="#F4F7FB"
)

subtitle.pack()


# =========================================================
# BUTTON FRAME
# =========================================================

button_frame = tk.Frame(

    window,

    bg="#F4F7FB"
)

button_frame.pack(
    pady=20
)


# =========================================================
# UPLOAD BUTTON
# =========================================================

upload_button = tk.Button(

    button_frame,

    text="Upload Report",

    command=upload_report,

    width=18,

    height=2
)

upload_button.grid(

    row=0,

    column=0,

    padx=5
)


# =========================================================
# MEDICAL INFORMATION BUTTON
# =========================================================

info_button = tk.Button(

    button_frame,

    text="Medical Information",

    command=show_medical_information,

    width=20,

    height=2
)

info_button.grid(

    row=0,

    column=1,

    padx=5
)


# =========================================================
# PATIENT EXPLANATION BUTTON
# =========================================================

explanation_button = tk.Button(

    button_frame,

    text="Patient Explanation",

    command=show_explanation,

    width=20,

    height=2
)

explanation_button.grid(

    row=0,

    column=2,

    padx=5
)


# =========================================================
# CLINICAL SUPPORT BUTTON
# =========================================================

clinical_button = tk.Button(

    button_frame,

    text="Clinical Support",

    command=show_clinical_support,

    width=20,

    height=2
)

clinical_button.grid(

    row=0,

    column=3,

    padx=5
)


# =========================================================
# PDF BUTTON
# =========================================================

pdf_button = tk.Button(

    button_frame,

    text="Generate PDF",

    command=generate_pdf,

    width=18,

    height=2
)

pdf_button.grid(

    row=0,

    column=4,

    padx=5
)


# =========================================================
# TEXT DISPLAY
# =========================================================

text_box = scrolledtext.ScrolledText(

    window,

    width=120,

    height=28,

    font=("Arial", 11),

    wrap=tk.WORD
)

text_box.pack(

    padx=20,

    pady=10,

    fill=tk.BOTH,

    expand=True
)


# =========================================================
# FOOTER
# =========================================================

footer = tk.Label(

    window,

    text="Educational Prototype - Not a Medical Diagnosis System",

    font=("Arial", 9),

    bg="#F4F7FB"
)

footer.pack(
    pady=8
)


# =========================================================
# START APPLICATION
# =========================================================

window.mainloop()
