# DOGFOOD Portal

An offline-first, open-source hackathon submission and judging portal, fully verified for the DOGFOOD 2026 challenge.

## Project status
**Fully Implemented & Verified (PASS 7/7).**

`
T1  gallery is public ................. PASS
T1  project from fixtures shown ....... PASS
T1  closed event refuses submissions .. PASS
T2  judge sees own scores ............. PASS
T2  judge cannot see peer scores ...... PASS
T2  participant blocked ............... PASS
T2  csv export works .................. PASS

claimed T1 T2, verified T1 T2
`

## Quick start

### 1. Boot the application
`
docker compose up --build
`

### 2. Run Acceptance Checker
`
python run.py .dogfood.toml
`

## License
MIT License — see LICENSE
