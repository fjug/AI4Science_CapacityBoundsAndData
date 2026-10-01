"""Colour schemes for all movies. Pick one with the THEME environment variable
(THEME=light | dark, default light); render_all.py does this for you.

"light" is the paper's Fig. 1 palette, taken from source.ai. "dark" is meant for
black slides: same hues, lifted in lightness so they read on black, with the
light pastel fills turned into dark tints of the same hue.
"""

THEMES = {
    "light": dict(
        BG="#FFFFFF",
        GRID="#CFD3D7", AXIS="#B7BCC1", ARROW="#777777", CENTRE="#666666",
        TEXT="#111111",
        BLUE_D="#2F65A7",      # model A dashed outline, its data dots
        BLUE_S="#7EA6D8",      # model A solid (learned) outline
        ORANGE_D="#E67E22",    # model B dashed outline, its data dots
        ORANGE_S="#F2AD73",    # model B solid (learned) outline
        OLIVE="#A4A44D",       # ring: useful new data / successful prediction
        RED="#B95C3D",         # ring: not actionable / extrapolation query
        GREY_FILL="#D5D7D8",   # fill: not actionable data
        FILL_A="#C8D0DB",      # learned area A
        FILL_B="#FCF1E7",      # learned area B
        FILL_AB="#E8E1DD",     # overlap of A and B
        GREEN="#669443",       # fill: prediction succeeded
        FAIL="#CC833C",        # fill: prediction failed
        TXT_INTER="#A4A44D", TXT_EXTRA="#CC833C", TXT_FAIL="#D62F27",
        REACH_FILL="#F4F4E9",  # band between learned outline and extrapolation reach
        REDUNDANT="#C4C4C4",   # fill: redundant data (inside the learned area), as in (c)
        # epistemic uncertainty, low -> high
        UNC_0="#4E9A3E", UNC_1="#C9B83A", UNC_2="#E8892B", UNC_3="#C0392B",
    ),
    "dark": dict(
        BG="#000000",
        GRID="#3A3E44", AXIS="#4C5157", ARROW="#8C8C8C", CENTRE="#9A9A9A",
        TEXT="#E8E8E8",
        BLUE_D="#5B95E0",
        BLUE_S="#8DB4E8",
        ORANGE_D="#F08C32",
        ORANGE_S="#F5B47E",
        OLIVE="#C2C25A",
        RED="#E0704A",
        GREY_FILL="#4A4D52",
        FILL_A="#1C2A40",
        FILL_B="#3A2614",
        FILL_AB="#332E2C",
        GREEN="#7DB84F",
        FAIL="#E89645",
        TXT_INTER="#CBCB66", TXT_EXTRA="#F0A35A", TXT_FAIL="#FF5C50",
        REACH_FILL="#26261A",
        REDUNDANT="#5E6166",
        UNC_0="#6CC04A", UNC_1="#E3CF4A", UNC_2="#F5963A", UNC_3="#F04E3E",
    ),
}
