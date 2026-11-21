# AGENTS.md
- Always update prompts.md after each request with what I asked, what you changed, and whether it worked.
- Before changing application code for a spec-based feature, first update spec.md to reflect the agreed behavior. Do not implement spec changes and app changes in the same turn unless the app change is purely verification or correction of that already-updated spec.
- After finalizing each section of the spec or build and before moving on, make sure we commit what we have done. Wait until that section or stage is finalized before commiting.

## Project layout

- `AGENTS.md` contains project instructions and layout rules.
- `spec.md` contains the project specification.
- `prompts.md` contains development prompts.
- `index.html` is the top-level single-file web app for GitHub Pages.
- `00_planning/` contains planning notes and sketches.
- `01_data/` contains data files.
- `02_validation/` contains hand calculations and test cases.
- `03_output/` contains screenshots and exported results.

## File placement rule

Save every new project file in the most appropriate folder: top-level files only for
the project entry documents and app; put notes and sketches in `00_planning/`, data
files in `01_data/`, calculations and test cases in `02_validation/`, and screenshots
or exported results in `03_output/`. Do not place miscellaneous files in the project
root.

