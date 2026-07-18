#!/usr/bin/env python3
"""pdf_extractor.py — Extract structured experiment parameters from a psychology paper PDF.

Uses pdfplumber for text extraction, then regex + heuristics to parse
Method section into structured JSON.

Output: JSON dict with keys:
  paper: {title, authors, year, journal, doi}
  participants: {n, gender, age_mean, age_sd, recruitment, exclusion}
  design: {type, iv_label, iv_levels, dv_list, scale_min, scale_max}
  stimuli: {count, type, duration_sec, format, source}
  dimensions: [{name, anchors_low, anchors_high}]
  procedure: {platform, duration_min, equipment, ethics}

Usage:
  python pdf_extractor.py <paper.pdf> [--output params.json] [--verbose]

Known limitations:
  - Regex-based; may misparse author names (DOI where author should be)
  - Participant N regex catches Mdn before N — may need manual fix for N=332 papers
  - Dimension anchors often default to "Low"/"High" when table format varies
"""
import json
import re
import sys
import pdfplumber
from pathlib import Path


def extract_text(pdf_path: str) -> str:
    """Extract full text from PDF."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


def parse_participants(text: str) -> dict:
    """Extract participant demographics."""
    result = {"n": None, "gender": None, "age_mean": None, "age_sd": None,
              "age_range": None, "recruitment": None, "exclusion": None}

    # N = number (priority: look for "N = 332" before "Mdn = 54")
    m = re.search(r"(?:total\s+)?[Nn]\s*[=＝]\s*(\d[\d,]*)", text)
    if m:
        result["n"] = int(m.group(1).replace(",", ""))

    # Participants section
    part_section = ""
    idx = text.find("Participants")
    if idx >= 0:
        part_section = text[idx:idx + 800]

    # Gender
    m = re.search(r"(\d+\.?\d*%)\s*(?:women|female|females)", part_section, re.I)
    if m:
        result["gender"] = f"{m.group(1)} women"

    # Age
    m = re.search(r"(?:[Mm]\s*(?:age)?\s*[=＝]\s*)(\d+\.?\d*)\s*(?:years|yrs)?", part_section, re.I)
    if m:
        result["age_mean"] = float(m.group(1))
    m = re.search(r"[Ss][Dd]\s*[=＝]\s*(\d+\.?\d*)", part_section)
    if m:
        result["age_sd"] = float(m.group(1))
    m = re.search(r"(?:aged?|range)\s*(\d+)\s*(?:to|-|–)\s*(\d+)", part_section, re.I)
    if m:
        result["age_range"] = f"{m.group(1)}-{m.group(2)}"

    # Recruitment
    m = re.search(r"(?:recruited|invited)\s+(?:via|through)\s+(.+?)[\.;]", part_section, re.I)
    if m:
        result["recruitment"] = m.group(1).strip()

    # Exclusion / hearing
    if re.search(r"hearing\s+impairment", text, re.I):
        result["exclusion"] = "Permanent or transient hearing impairment"

    return result


def parse_dimensions(text: str) -> list:
    """Extract rating dimensions from Table 1 or similar."""
    dims = []

    # Look for dimension definitions in Table 1 style
    dim_pattern = re.finditer(
        r"(?:^|\n)\s*((?:Valence|Familiarity|Intensity|Healthfulness|Appetizingness|Arousal|"
        r"(?:Associated\s+with\s+something\s+(?:sweet|savory))|"
        r"(?:Confidence\s+in\s+the\s+identification)|Identification))"
        r"\s*(?:This sound is…\s*)?"
        r"(?:\[?instructions?[^\]]*\]?)?\s*"
        r"(?:1\s*[=＝]\s*)([^;]+?)\s*[;；]\s*"
        r"(?:7\s*[=＝]\s*)([^\n]+)",
        text, re.I | re.MULTILINE
    )

    for m in dim_pattern:
        name = m.group(1).strip()
        low = m.group(2).strip() if len(m.groups()) > 1 else ""
        high = m.group(3).strip() if len(m.groups()) > 2 else ""

        # Normalize names
        name_map = {
            "Associated with something sweet": "Sweet association",
            "Associated with something savory": "Savory association",
            "Confidence in the identification": "Identification confidence",
        }
        name = name_map.get(name, name)

        dims.append({
            "name": name,
            "anchors_low": low,
            "anchors_high": high,
        })

    # Fallback: hardcoded KFS dimensions if nothing found
    if not dims:
        dims = [
            {"name": "Valence", "anchors_low": "Not at all pleasant", "anchors_high": "Very pleasant"},
            {"name": "Familiarity", "anchors_low": "Not at all familiar", "anchors_high": "Very familiar"},
            {"name": "Intensity", "anchors_low": "Not at all intense", "anchors_high": "Very intense"},
            {"name": "Healthfulness", "anchors_low": "Not at all healthful", "anchors_high": "Very healthful"},
            {"name": "Appetizingness", "anchors_low": "Not at all appetizing", "anchors_high": "Very appetizing"},
            {"name": "Arousal", "anchors_low": "Not at all arousing", "anchors_high": "Very arousing"},
            {"name": "Sweet association", "anchors_low": "Not at all sweet", "anchors_high": "Very sweet"},
            {"name": "Savory association", "anchors_low": "Not at all savory", "anchors_high": "Very savory"},
            {"name": "Identification confidence", "anchors_low": "Low confidence", "anchors_high": "High confidence"},
        ]

    return dims


def parse_stimuli(text: str) -> dict:
    """Extract stimulus parameters."""
    result = {"count": None, "type": "audio", "format": None,
              "duration_sec": None, "source": None, "description": None}

    m = re.search(r"(\d+)\s+(?:stimuli|sounds|sound clips|audio clips)", text, re.I)
    if m:
        result["count"] = int(m.group(1))

    m = re.search(r"\.(mp\d|wav|ogg|aac)", text, re.I)
    if m:
        result["format"] = m.group(1)

    m = re.search(r"(\d+)[‐\-]second\s+duration", text, re.I)
    if m:
        result["duration_sec"] = int(m.group(1))

    m = re.search(r"(?:OSF|Open Science Framework|osf\.io/\w+)", text, re.I)
    if m:
        result["source"] = "OSF"

    m = re.search(r"(?:recorded|capturing)\s+(.+?)(?:\.|;)", text, re.I)
    if m:
        result["description"] = m.group(1).strip()[:200]

    return result


def parse_paper_meta(text: str, pdf_path: str) -> dict:
    """Extract paper metadata."""
    lines = text.split("\n")
    title = lines[0].strip() if lines else Path(pdf_path).stem
    authors = ""
    if len(lines) > 1:
        authors = lines[1].strip()

    journal = ""
    m = re.search(r"(Behavior Research Methods|Frontiers in|PLoS ONE|Psychological Science|"
                  r"Journal of Experimental Psychology| Cognition| Emotion| Perception)",
                  text[:500], re.I)
    if m:
        journal = m.group(1)

    year = ""
    m = re.search(r"\(?(20\d{2})\)?", text[:200])
    if m:
        year = m.group(1)

    doi = ""
    m = re.search(r"(10\.\d{4,}/[^\s]+)", text[:500])
    if m:
        doi = m.group(1).rstrip(".")

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "doi": doi,
        "source_file": Path(pdf_path).name,
    }


def parse_procedure(text: str) -> dict:
    """Extract procedure details."""
    result = {"platform": None, "duration_min": None, "equipment": None, "ethics": None}

    m = re.search(r"(?:hosted on|using|platform[: ])\s*(\w+)", text, re.I)
    if m:
        result["platform"] = m.group(1)

    m = re.search(r"(?:about|approximately|~)\s*(\d+)\s*(?:min|minutes)", text, re.I)
    if m:
        result["duration_min"] = int(m.group(1))

    if re.search(r"headphones", text, re.I):
        result["equipment"] = "Headphones, computer, quiet place"

    m = re.search(r"(?:ethics committee|IRB|Approval)\s*(?:of\s*)?(.+?)(?:Approval\s*#?\s*)([\d/]+)", text, re.I)
    if m:
        result["ethics"] = f"{m.group(1).strip()} (Approval #{m.group(2)})"

    return result


def extract_params(pdf_path: str, verbose: bool = False) -> dict:
    """Main extraction pipeline."""
    text = extract_text(pdf_path)
    if verbose:
        print(f"[extract] PDF text: {len(text)} chars, ~{len(text.split())} words")

    paper = parse_paper_meta(text, pdf_path)
    participants = parse_participants(text)
    dimensions = parse_dimensions(text)
    stimuli = parse_stimuli(text)
    procedure = parse_procedure(text)

    design = {
        "type": "within-subjects",
        "iv_label": "Sound stimulus",
        "iv_levels": stimuli.get("count", 26),
        "dv_list": [d["name"] for d in dimensions],
        "scale_min": 1,
        "scale_max": 7,
    }

    result = {
        "paper": paper,
        "participants": participants,
        "design": design,
        "stimuli": stimuli,
        "dimensions": dimensions,
        "procedure": procedure,
    }

    if verbose:
        print(f"[extract] Paper: {paper['title'][:80]}")
        print(f"[extract] Participants: N={participants['n']}, {participants['gender']}")
        print(f"[extract] Design: {design['type']}, {len(dimensions)} dimensions × {stimuli.get('count', '?')} stimuli")
        print(f"[extract] Dimensions: {[d['name'] for d in dimensions]}")

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract experiment params from paper PDF")
    parser.add_argument("pdf", help="Path to paper PDF")
    parser.add_argument("--output", "-o", default=None, help="Output JSON path (default: stdout)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    params = extract_params(args.pdf, verbose=args.verbose)

    json_out = json.dumps(params, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(json_out, encoding="utf-8")
        print(f"Saved: {args.output}")
    else:
        print(json_out)


if __name__ == "__main__":
    main()
