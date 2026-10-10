import re

css_path = "/Users/ullasuchiha/KCAVP/static/css/style.css"
html_path = "/Users/ullasuchiha/KCAVP/templates/index.html"
js_path = "/Users/ullasuchiha/KCAVP/static/js/dashboard.js"

replacements = {
    # Primary (Indigo -> Ocean Blue)
    "#6366f1": "#2563eb",
    "rgba(99, 102, 241": "rgba(37, 99, 235",
    "#4f46e5": "#1e40af", 
    "#818cf8": "#60a5fa", 
    
    # Cyan (Neon cyan -> Sky Blue)
    "#06b6d4": "#0284c7",
    "rgba(6, 182, 212": "rgba(2, 132, 199",
    "#38bdf8": "#38bdf8", 
    
    # Emerald (Neon green -> Muted Emerald)
    "#10b981": "#059669",
    "rgba(16, 185, 129": "rgba(5, 150, 105",
    
    # Rose (Neon pinkish red -> Crimson/Rose)
    "#f43f5e": "#be123c",
    "rgba(244, 63, 94": "rgba(190, 18, 60",
    
    # Amber (Neon orange -> Bronze/Amber)
    "#f59e0b": "#d97706",
    "rgba(245, 158, 11": "rgba(217, 119, 6",
    "#fbbf24": "#b45309",
    
    # Purple (Neon purple -> Deep Indigo)
    "#8b5cf6": "#4f46e5",
    "rgba(139, 92, 246": "rgba(79, 70, 229",
    
    # Pink (Neon pink -> Muted pink/magenta)
    "#ec4899": "#be185d",
    "rgba(236, 72, 153": "rgba(190, 24, 93",
    
    # Property category 
    "#3b82f6": "#2563eb",
    "rgba(59, 130, 246": "rgba(37, 99, 235",
}

def increase_font(match):
    size = float(match.group(1))
    new_size = int(size + 2)
    return f"font-size: {new_size}px"

def process_file(filepath, inc_fonts=True):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        if inc_fonts:
            content = re.sub(r'font-size:\s*(\d+(?:\.\d+)?)px', increase_font, content)
            
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")
    except Exception as e:
        print(f"Error updating {filepath}: {e}")

process_file(css_path, inc_fonts=True)
process_file(html_path, inc_fonts=True)
process_file(js_path, inc_fonts=False)
