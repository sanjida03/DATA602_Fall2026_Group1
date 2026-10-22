"""
Filename: sephora_product_scraper.py
Author: Travisha Mills
Date: 2026-10-22
Project: Foundation Characteristics & Consumer Demand
Description:
    Sephora bestselling-sorted foundation listing.
    Source: user-captured HTML, 2026-10-22.
    Includes 45 unique non-sponsored listings
    Names are preserved from Sephora's product tiles.
"""

# Product ID: (brand, product name)
SEPHORA_LISTED_PRODUCTS = {
    'P502185': ('Haus Labs', 'Triclone Skin Tech Medium Coverage Foundation with Fermented Arnica'),
    'P519887': ('Armani Beauty', 'Luminous Silk Natural Glow Blurring Liquid Foundation with 24 Hour Wear'),
    'P525460': ('Fenty Beauty by Rihanna', "Pro Filt'r Fluid Flex Natural Matte Longwear Foundation"),
    'P526044': ('DIOR', 'Backstage Glow-Up Skin Tint Hydrating Tinted Moisturizer SPF 20'),
    'P520286': ('Estée Lauder', 'NEW Double Wear Stay-in-Place Lightweight Longwear Matte Foundation with 36H Wear'),
    'P525161': ('HUNG VANNGO BEAUTY', 'Red Carpet Skin Luminous Longwear Serum Foundation'),
    'P520563': ('m.ph by Mary Phillips', 'Le Skin Weightless Serum Foundation'),
    'P520267': ('DIOR', 'Forever Skin Glow Liquid Foundation 24HR Wear'),
    'P468694': ('MERIT', 'The Minimalist Perfecting Complexion Foundation and Concealer Stick'),
    'P520119': ('Armani Beauty', 'Mini Luminous Silk Natural Glow Blurring Liquid Foundation with 24HR Wear'),
    'P512480': ('DIOR', 'Forever Skin Perfect 24H Multi-Use Foundation Stick'),
    'P484039': ('Danessa Myricks Beauty', 'Yummy Skin Blurring Balm Powder - Tinted Primer & Foundation'),
    'P524839': ('Yves Saint Laurent', 'Skin Affair Soft Glow Cushion Foundation'),
    'P479338': ('NARS', 'Light Reflecting Skin Improving Medium Coverage Foundation with Cacao Peptides'),
    'P517849': ('NATASHA DENONA', 'Hy-Glam Foundation Hydrating & Blurring Luminous Longwear Serum Foundation'),
    'P526032': ('Drunk Elephant', 'Kamo Triple-Peptide Multi-Use Serum Foundation'),
    'P427301': ('NARS', 'Natural Radiant Longwear Full Coverage Foundation'),
    'P525457': ('Tower 28 Beauty', 'Swipe Serum Non-Acnegenic Foundation with Medium Buildable Coverage'),
    'P512640': ('HUDA BEAUTY', 'Easy Blur Natural Airbrush Foundation with Niacinamide'),
    'P517322': ('SEPHORA COLLECTION', 'Best Skin Ever 16 Hour Natural Finish Liquid Foundation'),
    'P522269': ('MAKE UP FOR EVER', 'Balancing & Perfecting Natural Finish Longwear Foundation'),
    'P520603': ('DIOR', 'Forever Skin Wear Blurring Natural Matte Foundation - 24HR Ultra Wear'),
    'P467607': ('Charlotte Tilbury', 'Mini Hollywood Flawless Filter'),
    'P521996': ('Rare Beauty by Selena Gomez', 'True to Myself Natural Matte Longwear Foundation \u200b'),
    'P516977': ('MAKEUP BY MARIO', 'SurrealSkin® Natural Finish Foundation'),
    'P507751': ('ciele', 'tint & PROTECT medium coverage serum foundation with SPF 50+'),
    'P506512': ('Danessa Myricks Beauty', 'Yummy Skin Soothing Serum Skin Tint Foundation with Peptides + Ceramides'),
    'P516897': ('Charlotte Tilbury', 'Airbrush Flawless Blurring & Matte Full Coverage Foundation'),
    'P506573': ('Hourglass', 'Veil™ Hydrating Skin Tint Foundation'),
    'P434104': ('Charlotte Tilbury', 'Hollywood Flawless Filter'),
    'P511153': ('MAC Cosmetics', 'Studio Fix Fluid SPF 15 24HR Buildable Soft-Matte Foundation + Oil Control'),
    'P308201': ('Lancôme', 'Teint Idole Ultra Wear Natural Matte Foundation with Hyaluronic Acid & Vitamin E'),
    'P525193': ('Westman Atelier', 'Suprême Bio-Complex Liquid Foundation With Exosomes + Peptides'),
    'P525815': ('Yepoda', 'The Dewy Day - Moisturizing Niacinamide & Apricot Korean Cushion Foundation'),
    'P517843': ('Too Faced', 'Born This Way Undetectable Medium-To-Full Coverage Foundation'),
    'P455418': ('ILIA', 'Super Serum Skin Tint SPF 40 - Hydrating Foundation'),
    'P525159': ('JUNG SAEM MOOL', 'Essential Skin Nuder Long-Lasting Hydrating Compact Cushion Foundation'),
    'P516457': ('MAC Cosmetics', 'Studio Fix Powder Plus Foundation with 24HR Oil Control + Blur-Matte Finish'),
    'P505903': ('SEPHORA COLLECTION', 'Best Skin Ever Matte Powder Foundation'),
    'P526967': ('MAC Cosmetics', 'Studio Radiance Skin Tint Stick'),
    'P511699': ('Charlotte Tilbury', 'Unreal Skin Sheer Glow Tint Hydrating Foundation Stick'),
    'P411885': ('IT Cosmetics', 'CC+ Cream Full Coverage Color Correcting Foundation with SPF 50+'),
    'P477829': ('Tower 28 Beauty', 'SunnyDays Skin Tint with Mineral Zinc SPF 30'),
    'P520608': ('NARS', 'Natural Matte Longwear Pore Blurring Medium-to-Full Coverage Foundation'),
    'P511130': ('Fenty Beauty by Rihanna', 'Soft’Lit Naturally Luminous Hydrating Longwear Foundation'),
}

def bestseller_status(product_id):
    """Return 1 if the product is listed, otherwise 0."""
    return 1 if product_id in SEPHORA_LISTED_PRODUCTS else 0
