# pyaar note viewer

A single-file web applet for reading clinical notes through an extraction pipeline. Each note is shown in linked panels: the **original note** as written, the **LLM pass** that reads it, and the **structured results** it produces, with every extracted value anchored to the exact span of text it came from.

Human-in-the-loop review is built in: flag any row and add a free-text annotation (persisted in `localStorage`), then export everything with **Download annotated CSV**.

**Live demo:** https://pyaar-noteviewer.vercel.app

## Data

All data is **fully synthetic**. `generate_synthetic.py` produces the sample CSV from fake names, random MRNs/dates, and authored prose (deterministic seed). No real patient data is used, and every extracted `span` is a verbatim quote of its synthetic note so the pipeline view renders.

## Run

The app is static — just open `public/index.html`, or serve the `public/` folder. Regenerate the sample data with:

```
python generate_synthetic.py
```

Part of [pyaar project](https://pyaarproject.org/artifacts).
